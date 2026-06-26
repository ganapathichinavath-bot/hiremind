"""Honeypot and trap detection."""

from __future__ import annotations

from datetime import datetime
from text_utils import build_candidate_text, cv_only_profile, is_ml_title, is_non_ml_title, normalize, production_evidence

def career_years(candidate: dict) -> float:
    history = candidate.get("career_history")
    if not isinstance(history, list):
        history = []
    months = sum(role.get("duration_months", 0) or 0 for role in history if isinstance(role, dict))
    return months / 12.0

def detect_honeypot(candidate: dict) -> str | None:
    profile = candidate.get("profile")
    if not isinstance(profile, dict):
        profile = {}
    yoe = profile.get("years_of_experience", 0) or 0
    actual_years = career_years(candidate)
    
    skills = candidate.get("skills")
    if not isinstance(skills, list):
        skills = []
    
    # 1. Years of experience discrepancy with career history
    if yoe - actual_years > 4.0:
        return "years_of_experience exceeds verifiable career timeline"
    if actual_years - yoe > 4.0:
        return "career timeline exceeds declared years of experience"

    # 2. Expert skills with zero duration check
    expert_zero = sum(
        1
        for skill in skills
        if isinstance(skill, dict) and skill.get("proficiency") == "expert" and (skill.get("duration_months", 0) or 0) == 0
    )
    if expert_zero >= 3:
        return "multiple expert skills with zero declared usage"

    # 3. Implausible expert skill density
    expert_count = sum(1 for skill in skills if isinstance(skill, dict) and skill.get("proficiency") == "expert")
    if expert_count >= 8 and len(skills) >= 10:
        return "implausible expert skill density"

    # 4. Role duration vs date range mismatch (Honeypot timeline check)
    history = candidate.get("career_history")
    if isinstance(history, list):
        for role in history:
            if not isinstance(role, dict):
                continue
            start = role.get("start_date")
            end = role.get("end_date")
            duration = role.get("duration_months", 0) or 0
            if start:
                try:
                    start_dt = datetime.strptime(start, "%Y-%m-%d")
                    if end:
                        end_dt = datetime.strptime(end, "%Y-%m-%d")
                    else:
                        # If current role, assume up to mid 2026 (challenge date)
                        end_dt = datetime(2026, 6, 21)
                    
                    expected_months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
                    # If duration claims to be 8 years (96 months) but dates only span 3 years (36 months)
                    if duration - expected_months > 12:
                        return f"role duration ({duration} mo) exceeds date span ({expected_months} mo) at {role.get('company')}"
                except ValueError:
                    pass

    # 5. Years of experience contradicts graduation timeline
    education = candidate.get("education")
    if isinstance(education, list):
        grad_years = [edu.get("end_year") for edu in education if isinstance(edu, dict)]
        valid_grads = [y for y in grad_years if isinstance(y, (int, float))]
        if valid_grads:
            earliest_grad = min(valid_grads)
            if earliest_grad < 2026:
                max_possible_yoe = 2026 - earliest_grad + 2.0  # 2 years buffer
                if yoe > max_possible_yoe and yoe > 3.0:
                    return f"declared experience ({yoe} yrs) contradicts graduation year ({earliest_grad})"

    # 6. Ghost profile check
    signals = candidate.get("redrob_signals")
    if not isinstance(signals, dict):
        signals = {}
    if signals.get("profile_completeness_score", 100) < 5 and not (
        signals.get("verified_email") or signals.get("verified_phone")
    ):
        return "near-empty ghost profile"

    return None

def is_ml_jd(jd_title: str, jd_text: str) -> bool:
    keywords = ["ai", "ml", "machine learning", "deep learning", "nlp", "llm", "rag", "embeddings", "retrieval", "computer vision", "semantic search"]
    title_lower = jd_title.lower()
    text_lower = jd_text.lower()
    return any(kw in title_lower for kw in keywords) or any(kw in text_lower for kw in keywords)

def title_skill_trap(candidate: dict, is_ml_role: bool = True) -> str | None:
    if not is_ml_role:
        return None
    profile = candidate.get("profile")
    if not isinstance(profile, dict):
        profile = {}
    title = profile.get("current_title") or ""
    
    skills = candidate.get("skills")
    if not isinstance(skills, list):
        skills = []
    ai_skill_count = 0
    for skill in skills:
        if isinstance(skill, dict):
            name = (skill.get("name") or "").lower()
            if any(token in name for token in ("ai", "ml", "llm", "nlp", "embedding", "pytorch", "tensorflow", "rag")):
                ai_skill_count += 1

    if is_non_ml_title(title) and ai_skill_count >= 6:
        return "non-ML title with keyword-stuffed AI skills"
    return None

def compute_penalty_multiplier(candidate: dict, full_text: str, is_ml_role: bool = True) -> tuple[float, list[str]]:
    penalties: list[str] = []
    multiplier = 1.0

    trap = title_skill_trap(candidate, is_ml_role=is_ml_role)
    if trap:
        penalties.append(trap)
        multiplier *= 0.12

    profile = candidate.get("profile")
    if not isinstance(profile, dict):
        profile = {}
    title = profile.get("current_title") or ""
    
    history = candidate.get("career_history")
    if not isinstance(history, list):
        history = []

    if is_ml_role:
        if is_non_ml_title(title) and not is_ml_title(title):
            career_titles = " ".join(role.get("title") or "" for role in history if isinstance(role, dict)).lower()
            if not any(keyword in career_titles for keyword in ("engineer", "scientist", "research", "ml", "ai", "data")):
                penalties.append("career lacks ML/AI engineering trajectory")
                multiplier *= 0.35

    companies = [(role.get("company") or "").lower() for role in history if isinstance(role, dict)]
    if companies and all(any(firm in company for firm in ("tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini", "hcl")) for company in companies):
        penalties.append("consulting-only career")
        multiplier *= 0.20

    if is_ml_role:
        if cv_only_profile(full_text):
            penalties.append("CV/speech/robotics focus without retrieval exposure")
            multiplier *= 0.70

        summary = normalize(profile.get("summary") or "")
        if "langchain" in summary and "openai" in summary and len(production_evidence(full_text)) == 0:
            penalties.append("framework-demo profile without production evidence")
            multiplier *= 0.55

    if len(history) >= 4:
        short_stints = sum(1 for role in history if isinstance(role, dict) and (role.get("duration_months") or 0) < 18)
        if short_stints / len(history) >= 0.75:
            penalties.append("title-chasing job hopping pattern")
            multiplier *= 0.65

    if is_ml_role:
        research_hits = sum(
            1
            for role in history
            if isinstance(role, dict) and "research" in (role.get("title") or "").lower() and "engineer" not in (role.get("title") or "").lower()
        )
        if research_hits == len(history) and len(history) > 0 and len(production_evidence(full_text)) == 0:
            penalties.append("pure research background without deployment evidence")
            multiplier *= 0.10

    return multiplier, penalties
