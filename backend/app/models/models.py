from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, ForeignKey, DateTime
from app.database.connection import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="recruiter")  # admin, recruiter

class Candidate(Base):
    __tablename__ = "candidates"

    candidate_id = Column(String, primary_key=True, index=True)
    profile_data = Column(JSON, nullable=False)
    
    # Precomputed / populated ranking subscores
    score = Column(Float, default=0.0)
    semantic_score = Column(Float, default=0.0)
    skill_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    education_score = Column(Float, default=0.0)
    behavioral_score = Column(Float, default=0.0)
    
    # Flags and notes
    is_honeypot = Column(Boolean, default=False)
    is_disqualified = Column(Boolean, default=False)
    disqualification_reason = Column(String, nullable=True)
    rank = Column(Integer, nullable=True)
    reasoning = Column(String, nullable=True)

    # Denormalized fields for fast search/filtering
    years_of_experience = Column(Float, default=0.0)
    current_title = Column(String, default="")
    current_company = Column(String, default="")
    location = Column(String, default="")
    skills_list = Column(JSON, default=list)

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="Senior AI Engineer")
    raw_text = Column(String, nullable=False)
    extracted_skills = Column(JSON, default=list)
    extracted_experience = Column(String, default="")
    extracted_education = Column(String, default="")
    extracted_certifications = Column(JSON, default=list)
    extracted_responsibilities = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)

class SavedCandidate(Base):
    __tablename__ = "saved_candidates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    candidate_id = Column(String, ForeignKey("candidates.candidate_id"), nullable=False)
    saved_at = Column(DateTime, default=datetime.utcnow)

