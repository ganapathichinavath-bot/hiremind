from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
import csv
from typing import List, Dict, Any, Optional

from app.database.connection import get_db
from app.models.models import Candidate, JobDescription
from app.schemas.schemas import JDUploadResponse, RankRequest, RankResponse, CandidateResult
from app.api.auth import get_current_user
from app.utils.parser import extract_text_from_docx, parse_jd_requirements
from app.embeddings.generator import EmbeddingGenerator
from app.services.vector_store import ChromaStore
from app.ranking.engine import score_candidate
from app.services.explainable_ai import generate_explanation

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/upload", response_model=JDUploadResponse)
def upload_job_description(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    try:
        content = file.file.read()
        filename = file.filename or ""
        if filename.endswith(".docx"):
            text = extract_text_from_docx(content)
        else:
            text = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")
        
    requirements = parse_jd_requirements(text)
    
    # Deactivate other jobs
    db.query(JobDescription).update({JobDescription.is_active: False})
    
    db_jd = JobDescription(
        title=requirements["title"],
        raw_text=text,
        extracted_skills=requirements["extracted_skills"],
        extracted_experience=requirements["extracted_experience"],
        extracted_education=requirements["extracted_education"],
        extracted_certifications=requirements["extracted_certifications"],
        extracted_responsibilities=requirements["extracted_responsibilities"],
        is_active=True
    )
    db.add(db_jd)
    db.commit()
    db.refresh(db_jd)
    return db_jd

@router.post("/rank", response_model=RankResponse)
def rank_candidates(
    request: RankRequest,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    # Find active job description
    jd = db.query(JobDescription).filter(JobDescription.is_active == True).first()
    if not jd:
        # Check if there is any job description
        jd = db.query(JobDescription).order_by(JobDescription.id.desc()).first()
    if not jd:
        raise HTTPException(status_code=404, detail="No job description uploaded yet.")
        
    # Get all candidates
    candidates = db.query(Candidate).all()
    if not candidates:
        raise HTTPException(status_code=400, detail="No candidates imported. Ingest candidate JSONL first.")
        
    generator = EmbeddingGenerator()
    chroma = ChromaStore()
    
    # Get JD embedding
    jd_embedding = generator.get_embedding(jd.raw_text)
    
    from disqualify import is_ml_jd
    is_ml = is_ml_jd(jd.title or "", jd.raw_text or "")
    
    # Query semantic scores from ChromaDB
    semantic_results = chroma.query_candidates(jd_embedding.tolist(), top_k=len(candidates))
    semantic_lookup = {r["candidate_id"]: r["similarity"] for r in semantic_results}
    
    scored_candidates = []
    disqualified_count = 0
    
    for cand in candidates:
        sim = semantic_lookup.get(cand.candidate_id, 0.0)
        final_score, details = score_candidate(cand.profile_data, sim, jd.extracted_skills, is_ml_role=is_ml)
        
        # Update database candidate fields
        cand.score = final_score
        cand.semantic_score = details["semantic_score"]
        cand.skill_score = details["skill_score"]
        cand.experience_score = details["experience_score"]
        cand.education_score = details["education_score"]
        cand.behavioral_score = details["behavioral_score"]
        cand.is_honeypot = details["is_honeypot"]
        cand.is_disqualified = details["is_disqualified"]
        cand.disqualification_reason = details["disqualification_reason"]
        
        if details["is_disqualified"]:
            disqualified_count += 1
            
        scored_candidates.append((cand, details))
        
    # Sort candidates: (-score, candidate_id ASC)
    scored_candidates.sort(key=lambda item: (-item[0].score, item[0].candidate_id))
    
    # Assign ranks
    results = []
    for rank_idx, (cand, details) in enumerate(scored_candidates, start=1):
        cand.rank = rank_idx
        
        # Generate explainable reasoning
        explanation = generate_explanation(cand.profile_data, details, jd.extracted_skills, rank_idx)
        cand.reasoning = explanation["why_statement"]
        
        # Collect top-K results to return
        if rank_idx <= request.top_k:
            profile = cand.profile_data.get("profile", {})
            results.append(CandidateResult(
                candidate_id=cand.candidate_id,
                rank=rank_idx,
                score=round(cand.score, 4),
                semantic_score=round(cand.semantic_score, 4),
                skill_score=round(cand.skill_score, 4),
                experience_score=round(cand.experience_score, 4),
                education_score=round(cand.education_score, 4),
                behavioral_score=round(cand.behavioral_score, 4),
                medal="gold" if rank_idx == 1 else "silver" if rank_idx == 2 else "bronze" if rank_idx == 3 else "standard",
                title=profile.get("current_title", "Unknown"),
                company=profile.get("current_company", ""),
                location=cand.location,
                years_of_experience=cand.years_of_experience,
                reasoning=cand.reasoning,
                penalties=details["penalties"]
            ))
            
    db.commit()
    
    return RankResponse(
        total_candidates=len(candidates),
        disqualified_candidates=disqualified_count,
        results=results
    )

@router.get("/top-candidates", response_model=List[CandidateResult])
def get_top_candidates(
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    candidates = db.query(Candidate).filter(Candidate.rank != None).order_by(Candidate.rank.asc()).limit(limit).all()
    results = []
    for cand in candidates:
        profile = cand.profile_data.get("profile", {})
        results.append(CandidateResult(
            candidate_id=cand.candidate_id,
            rank=cand.rank or 999,
            score=round(cand.score, 4),
            semantic_score=round(cand.semantic_score, 4),
            skill_score=round(cand.skill_score, 4),
            experience_score=round(cand.experience_score, 4),
            education_score=round(cand.education_score, 4),
            behavioral_score=round(cand.behavioral_score, 4),
            medal="gold" if cand.rank == 1 else "silver" if cand.rank == 2 else "bronze" if cand.rank == 3 else "standard",
            title=profile.get("current_title", "Unknown"),
            company=profile.get("current_company", ""),
            location=cand.location,
            years_of_experience=cand.years_of_experience,
            reasoning=cand.reasoning or "",
            penalties=[]
        ))
    return results

@router.get("/export/submission")
def export_submission(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    candidates = db.query(Candidate).filter(Candidate.rank != None).order_by(Candidate.rank.asc()).limit(100).all()
    if not candidates:
        raise HTTPException(status_code=400, detail="Rankings have not been generated. Call POST /jobs/rank first.")
        
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["candidate_id", "rank", "score", "reasoning"])
    
    for cand in candidates:
        writer.writerow([
            cand.candidate_id,
            cand.rank,
            f"{cand.score:.4f}",
            cand.reasoning or ""
        ])
        
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=submission.csv"}
    )
