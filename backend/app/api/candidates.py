from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
import json
import io
import math
from typing import List, Dict, Any, Optional
from collections import Counter

from app.database.connection import get_db
from app.models.models import Candidate, JobDescription, SavedCandidate
from app.schemas.schemas import CandidateResponse, CandidateDetailResponse, CandidateStats
from app.api.auth import get_current_user
from app.embeddings.generator import EmbeddingGenerator
from app.services.vector_store import ChromaStore

router = APIRouter(prefix="/candidates", tags=["candidates"])

def build_candidate_text(candidate: Dict[str, Any]) -> str:
    parts = []
    profile = candidate.get("profile")
    if isinstance(profile, dict):
        parts.append(profile.get("headline") or "")
        parts.append(profile.get("summary") or "")
        parts.append(profile.get("current_title") or "")
    
    career_history = candidate.get("career_history")
    if isinstance(career_history, list):
        for role in career_history:
            if isinstance(role, dict):
                parts.append(role.get("title") or "")
                parts.append(role.get("description") or "")
        
    education = candidate.get("education")
    if isinstance(education, list):
        for edu in education:
            if isinstance(edu, dict):
                parts.append(edu.get("field_of_study") or "")
                parts.append(edu.get("degree") or "")
        
    skills = candidate.get("skills")
    if isinstance(skills, list):
        for skill in skills:
            if isinstance(skill, dict):
                parts.append(skill.get("name") or "")
        
    res = " ".join(filter(None, parts)).strip()
    return res if res else " "

@router.post("/upload", response_model=Dict[str, Any])
def upload_candidates(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    try:
        content = file.file.read()
        lines = content.decode("utf-8-sig").splitlines()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")
        
    generator = EmbeddingGenerator()
    chroma = ChromaStore()
    
    parsed_candidates = []
    texts_to_embed = []
    
    # Process line by line to parse JSON and check database
    for line in lines:
        if not line.strip():
            continue
        try:
            cand_dict = json.loads(line)
        except Exception:
            continue
            
        candidate_id = cand_dict.get("candidate_id")
        if not candidate_id:
            continue
            
        # Denormalize simple attributes
        profile = cand_dict.get("profile")
        if not isinstance(profile, dict):
            profile = {}
            
        yoe = profile.get("years_of_experience", 0.0)
        if yoe is None:
            yoe = 0.0
            
        curr_title = profile.get("current_title") or ""
        curr_company = profile.get("current_company") or ""
        
        loc_parts = []
        loc_val = profile.get("location")
        if loc_val:
            loc_parts.append(str(loc_val))
        country_val = profile.get("country")
        if country_val:
            loc_parts.append(str(country_val))
        loc = ", ".join(loc_parts)
        
        skills = cand_dict.get("skills")
        if not isinstance(skills, list):
            skills = []
        skills_list = []
        for s in skills:
            if isinstance(s, dict):
                name_val = s.get("name")
                if name_val:
                    skills_list.append(str(name_val))
        
        # Check if already exists
        db_cand = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
        if db_cand:
            db_cand.profile_data = cand_dict
            db_cand.years_of_experience = yoe
            db_cand.current_title = curr_title
            db_cand.current_company = curr_company
            db_cand.location = loc
            db_cand.skills_list = skills_list
        else:
            db_cand = Candidate(
                candidate_id=candidate_id,
                profile_data=cand_dict,
                years_of_experience=yoe,
                current_title=curr_title,
                current_company=curr_company,
                location=loc,
                skills_list=skills_list
            )
            db.add(db_cand)
            
        text = build_candidate_text(cand_dict)
        texts_to_embed.append(text)
        parsed_candidates.append({
            "candidate_id": candidate_id,
            "years_of_experience": yoe,
            "current_title": curr_title,
            "location": loc
        })
        
    db.commit()
    
    # Generate embeddings in batch and upload to Chroma
    if parsed_candidates:
        try:
            embeddings = generator.get_embeddings(texts_to_embed)
            ids_to_add = [c["candidate_id"] for c in parsed_candidates]
            embeddings_to_add = [emb.tolist() for emb in embeddings]
            metadatas_to_add = parsed_candidates
            
            chroma.add_candidates(ids_to_add, embeddings_to_add, metadatas_to_add)
        except Exception as e:
            print(f"Error storing to ChromaDB: {e}")
            # Do not fail request if Chroma store fails to sync, but log it
            
    return {"status": "success", "imported": len(parsed_candidates)}

@router.get("", response_model=Dict[str, Any])
def list_candidates(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    search: Optional[str] = None,
    min_experience: Optional[float] = None,
    max_experience: Optional[float] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    query = db.query(Candidate)
    
    if search:
        # Simple match title or location or company
        query = query.filter(
            (Candidate.current_title.ilike(f"%{search}%")) |
            (Candidate.current_company.ilike(f"%{search}%")) |
            (Candidate.location.ilike(f"%{search}%"))
        )
        
    if min_experience is not None:
        query = query.filter(Candidate.years_of_experience >= min_experience)
    if max_experience is not None:
        query = query.filter(Candidate.years_of_experience <= max_experience)
    if location:
        query = query.filter(Candidate.location.ilike(f"%{location}%"))
        
    total = query.count()
    # Sort by rank ascending if rank exists, else score descending
    candidates = query.order_by(Candidate.rank.asc(), Candidate.score.desc()).offset((page - 1) * limit).limit(limit).all()
    
    saved_ids = {s.candidate_id for s in db.query(SavedCandidate).filter(SavedCandidate.user_id == current_user.id).all()}

    results = []
    for cand in candidates:
        results.append({
            "candidate_id": cand.candidate_id,
            "years_of_experience": cand.years_of_experience,
            "current_title": cand.current_title,
            "current_company": cand.current_company,
            "location": cand.location,
            "score": cand.score,
            "semantic_score": cand.semantic_score,
            "skill_score": cand.skill_score,
            "experience_score": cand.experience_score,
            "education_score": cand.education_score,
            "behavioral_score": cand.behavioral_score,
            "is_honeypot": cand.is_honeypot,
            "is_disqualified": cand.is_disqualified,
            "rank": cand.rank,
            "reasoning": cand.reasoning,
            "is_saved": cand.candidate_id in saved_ids
        })

        
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": math.ceil(total / limit),
        "candidates": results
    }

@router.get("/detail/{id}", response_model=CandidateDetailResponse)
def get_candidate_details(
    id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    cand = db.query(Candidate).filter(Candidate.candidate_id == id).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    is_saved = db.query(SavedCandidate).filter(
        SavedCandidate.user_id == current_user.id,
        SavedCandidate.candidate_id == id
    ).first() is not None
    
    cand.is_saved = is_saved
    return cand


@router.get("/analytics", response_model=CandidateStats)
def get_analytics(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    candidates = db.query(Candidate).all()
    if not candidates:
        return {
            "total_candidates": 0,
            "average_score": 0.0,
            "disqualified_count": 0,
            "honeypot_count": 0,
            "top_skills": {},
            "experience_distribution": {}
        }
        
    total = len(candidates)
    score_sum = sum(c.score for c in candidates)
    avg_score = score_sum / total
    
    disqualified = sum(1 for c in candidates if c.is_disqualified)
    honeypots = sum(1 for c in candidates if c.is_honeypot)
    
    # Skill distribution
    all_skills = []
    for c in candidates:
        all_skills.extend(c.skills_list or [])
    skill_counts = Counter(all_skills).most_common(10)
    top_skills = {k: v for k, v in skill_counts}
    
    # Experience distribution
    exp_dist = {"0-2 yrs": 0, "3-5 yrs": 0, "6-8 yrs": 0, "9-12 yrs": 0, "13+ yrs": 0}
    for c in candidates:
        yoe = c.years_of_experience
        if yoe < 3:
            exp_dist["0-2 yrs"] += 1
        elif yoe < 6:
            exp_dist["3-5 yrs"] += 1
        elif yoe < 9:
            exp_dist["6-8 yrs"] += 1
        elif yoe < 13:
            exp_dist["9-12 yrs"] += 1
        else:
            exp_dist["13+ yrs"] += 1
            
    return {
        "total_candidates": total,
        "average_score": round(avg_score, 4),
        "disqualified_count": disqualified,
        "honeypot_count": honeypots,
        "top_skills": top_skills,
        "experience_distribution": exp_dist
    }

@router.post("/save/{candidate_id}", response_model=Dict[str, Any])
def save_candidate(
    candidate_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    cand = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    existing = db.query(SavedCandidate).filter(
        SavedCandidate.user_id == current_user.id,
        SavedCandidate.candidate_id == candidate_id
    ).first()
    
    if not existing:
        saved_cand = SavedCandidate(user_id=current_user.id, candidate_id=candidate_id)
        db.add(saved_cand)
        db.commit()
        
    return {"status": "success", "message": "Candidate saved successfully"}

@router.delete("/save/{candidate_id}", response_model=Dict[str, Any])
def unsave_candidate(
    candidate_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    existing = db.query(SavedCandidate).filter(
        SavedCandidate.user_id == current_user.id,
        SavedCandidate.candidate_id == candidate_id
    ).first()
    
    if existing:
        db.delete(existing)
        db.commit()
        
    return {"status": "success", "message": "Candidate unsaved successfully"}

@router.get("/saved", response_model=Dict[str, Any])
def list_saved_candidates(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    saved_query = db.query(SavedCandidate).filter(SavedCandidate.user_id == current_user.id)
    total = saved_query.count()
    
    saved_records = saved_query.offset((page - 1) * limit).limit(limit).all()
    saved_candidate_ids = [r.candidate_id for r in saved_records]
    
    if not saved_candidate_ids:
        return {
            "total": 0,
            "page": page,
            "limit": limit,
            "pages": 0,
            "candidates": []
        }
        
    candidates = db.query(Candidate).filter(Candidate.candidate_id.in_(saved_candidate_ids)).all()
    candidates_map = {c.candidate_id: c for c in candidates}
    
    results = []
    for record in saved_records:
        cand = candidates_map.get(record.candidate_id)
        if cand:
            results.append({
                "candidate_id": cand.candidate_id,
                "years_of_experience": cand.years_of_experience,
                "current_title": cand.current_title,
                "current_company": cand.current_company,
                "location": cand.location,
                "score": cand.score,
                "semantic_score": cand.semantic_score,
                "skill_score": cand.skill_score,
                "experience_score": cand.experience_score,
                "education_score": cand.education_score,
                "behavioral_score": cand.behavioral_score,
                "is_honeypot": cand.is_honeypot,
                "is_disqualified": cand.is_disqualified,
                "rank": cand.rank,
                "reasoning": cand.reasoning,
                "is_saved": True
            })
            
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": math.ceil(total / limit),
        "candidates": results
    }
