import os
import sys
import json
import pickle
import numpy as np
from pathlib import Path

# Add backend directory to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from backend.app.database.connection import SessionLocal, Base, engine
from backend.app.models.models import Candidate, JobDescription, User
from backend.app.services.vector_store import ChromaStore
from backend.app.utils.parser import extract_text_from_docx, parse_jd_requirements

def seed_database():
    print("Initializing Database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Create a default recruiter user if none exists
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        from passlib.hash import bcrypt
        hashed = bcrypt.hash("admin123")
        admin_user = User(username="admin", hashed_password=hashed, role="admin")
        db.add(admin_user)
        db.commit()
        print("Created default admin user (admin / admin123)")

    # 1. Parse and seed job description
    from config import JOB_DESCRIPTION_PATH, CANDIDATES_PATH, ARTIFACTS_DIR
    
    print("Reading and parsing job description...")
    try:
        if JOB_DESCRIPTION_PATH.exists():
            with open(JOB_DESCRIPTION_PATH, "rb") as f:
                content = f.read()
            text = extract_text_from_docx(content)
        else:
            text = "Senior AI Engineer — Founding Team\nWe are looking for a Senior AI Engineer with experience in embeddings-based retrieval systems, sentence-transformers, vector databases, hybrid search, python, and evaluation frameworks (ndcg, mrr, map)."
        
        requirements = parse_jd_requirements(text)
        
        # Deactivate previous active jobs
        db.query(JobDescription).update({JobDescription.is_active: False})
        
        db_jd = JobDescription(
            title=requirements.get("title", "Senior AI Engineer"),
            raw_text=text,
            extracted_skills=requirements.get("extracted_skills", []),
            extracted_experience=requirements.get("extracted_experience", ""),
            extracted_education=requirements.get("extracted_education", ""),
            extracted_certifications=requirements.get("extracted_certifications", []),
            extracted_responsibilities=requirements.get("extracted_responsibilities", []),
            is_active=True
        )
        db.add(db_jd)
        db.commit()
        print("Job description successfully seeded.")
    except Exception as e:
        print(f"Error seeding job description: {e}")

    # 2. Seed candidates using precomputed artifacts for fast speed
    print("Reading candidate list and precomputed subscores...")
    if not CANDIDATES_PATH.exists():
        print(f"Candidates file not found at {CANDIDATES_PATH}. Seeding aborted.")
        return

    subscores = {}
    subscores_path = ARTIFACTS_DIR / "subscores.pkl"
    if subscores_path.exists():
        with open(subscores_path, "rb") as handle:
            subscores = pickle.load(handle)

    embeddings = None
    candidate_ids = []
    embeddings_path = ARTIFACTS_DIR / "embeddings.npy"
    ids_path = ARTIFACTS_DIR / "candidate_ids.npy"
    if embeddings_path.exists() and ids_path.exists():
        embeddings = np.load(embeddings_path)
        candidate_ids = list(np.load(ids_path, allow_pickle=True))

    chroma = ChromaStore()
    
    print("Ingesting candidates to SQLite...")
    
    # We read candidates line by line
    count = 0
    batch_size = 1000
    db_candidates = []
    
    chroma_ids = []
    chroma_embeddings = []
    chroma_metadatas = []
    
    with open(CANDIDATES_PATH, "r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                cand_dict = json.loads(line)
            except Exception:
                continue
                
            candidate_id = cand_dict.get("candidate_id")
            if not candidate_id:
                continue
                
            # Check if already exists in DB
            exists = db.query(Candidate).filter(Candidate.candidate_id == candidate_id).first()
            if exists:
                count += 1
                continue
                
            profile = cand_dict.get("profile", {})
            yoe = profile.get("years_of_experience", 0.0)
            curr_title = profile.get("current_title", "")
            curr_company = profile.get("current_company", "")
            loc = f"{profile.get('location', '')}, {profile.get('country', '')}".strip(", ")
            skills_list = [s.get("name", "") for s in cand_dict.get("skills", [])]
            
            # Map subscores if available
            score = 0.0
            sem_score = 0.0
            skill_score = 0.0
            exp_score = 0.0
            edu_score = 0.0
            beh_score = 0.0
            is_hp = False
            is_disq = False
            disq_reason = None
            
            if candidate_id in subscores:
                sub = subscores[candidate_id]
                skill_score = float(sub.get("skill_score", 0.0) / 100.0)
                exp_score = float(sub.get("experience_score", 0.0) / 100.0)
                edu_score = float(sub.get("experience_score", 0.0) / 100.0)
                beh_score = float(sub.get("recruitability_score", 0.0) / 100.0)
                is_disq = len(sub.get("penalties", [])) > 0
                disq_reason = ", ".join(sub.get("penalties", [])) if is_disq else None
            else:
                # If disqualified early (honeypot)
                is_hp = True
                is_disq = True
                disq_reason = "honeypot check failed"
                
            db_cand = Candidate(
                candidate_id=candidate_id,
                profile_data=cand_dict,
                years_of_experience=yoe,
                current_title=curr_title,
                current_company=curr_company,
                location=loc,
                skills_list=skills_list,
                score=score,
                semantic_score=sem_score,
                skill_score=skill_score,
                experience_score=exp_score,
                education_score=edu_score,
                behavioral_score=beh_score,
                is_honeypot=is_hp,
                is_disqualified=is_disq,
                disqualification_reason=disq_reason
            )
            db_candidates.append(db_cand)
            
            # Prepare ChromaDB elements
            if embeddings is not None and candidate_id in candidate_ids:
                idx = candidate_ids.index(candidate_id)
                chroma_ids.append(candidate_id)
                chroma_embeddings.append(embeddings[idx].tolist())
                chroma_metadatas.append({
                    "candidate_id": candidate_id,
                    "years_of_experience": yoe,
                    "current_title": curr_title,
                    "location": loc
                })
            
            if len(db_candidates) >= batch_size:
                db.bulk_save_objects(db_candidates)
                db.commit()
                db_candidates = []
                
                if chroma_ids:
                    chroma.add_candidates(chroma_ids, chroma_embeddings, chroma_metadatas)
                    chroma_ids, chroma_embeddings, chroma_metadatas = [], [], []
                
                count += len(chroma_ids) if chroma_ids else batch_size
                print(f"Ingested {count} candidates...")
                
        # Save remaining candidates
        if db_candidates:
            db.bulk_save_objects(db_candidates)
            db.commit()
        if chroma_ids:
            chroma.add_candidates(chroma_ids, chroma_embeddings, chroma_metadatas)
            
        print(f"Finished seeding all candidates.")
        
    db.close()

if __name__ == "__main__":
    seed_database()
