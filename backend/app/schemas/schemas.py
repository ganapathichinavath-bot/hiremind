from pydantic import BaseModel, Field
from typing import Any, List, Dict, Optional

class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[str] = "recruiter"

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class CandidateProfile(BaseModel):
    candidate_id: str
    profile: Dict[str, Any]
    career_history: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    skills: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[Dict[str, Any]] = Field(default_factory=list)
    redrob_signals: Dict[str, Any] = Field(default_factory=dict)

class CandidateResponse(BaseModel):
    candidate_id: str
    years_of_experience: float
    current_title: str
    current_company: str
    location: str
    score: float
    semantic_score: float
    skill_score: float
    experience_score: float
    education_score: float
    behavioral_score: float
    is_honeypot: bool
    is_disqualified: bool
    rank: Optional[int] = None
    reasoning: Optional[str] = None
    is_saved: Optional[bool] = False

    class Config:
        from_attributes = True

class CandidateDetailResponse(BaseModel):
    candidate_id: str
    profile_data: Dict[str, Any]
    score: float
    semantic_score: float
    skill_score: float
    experience_score: float
    education_score: float
    behavioral_score: float
    is_honeypot: bool
    is_disqualified: bool
    disqualification_reason: Optional[str] = None
    rank: Optional[int] = None
    reasoning: Optional[str] = None
    is_saved: Optional[bool] = False

    class Config:
        from_attributes = True


class CandidateStats(BaseModel):
    total_candidates: int
    average_score: float
    disqualified_count: int
    honeypot_count: int
    top_skills: Dict[str, int]
    experience_distribution: Dict[str, int]

class JDUploadRequest(BaseModel):
    text: str

class JDUploadResponse(BaseModel):
    id: int
    title: str
    extracted_skills: List[str]
    extracted_experience: str
    extracted_education: str
    extracted_certifications: List[str]
    extracted_responsibilities: List[str]

    class Config:
        from_attributes = True

class RankRequest(BaseModel):
    job_description_id: Optional[int] = None
    top_k: int = Field(default=100, ge=1, le=500)

class CandidateResult(BaseModel):
    candidate_id: str
    rank: int
    score: float
    semantic_score: float
    skill_score: float
    experience_score: float
    education_score: float
    behavioral_score: float
    medal: str
    title: str
    company: str
    location: str
    years_of_experience: float
    reasoning: str
    penalties: List[str]

class RankResponse(BaseModel):
    total_candidates: int
    disqualified_candidates: int
    results: List[CandidateResult]

class GoogleLoginRequest(BaseModel):
    id_token: str

