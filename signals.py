"""Structured scoring signals and engines for HIREMIND AI."""

from __future__ import annotations

from datetime import date, datetime
from config import CONSULTING_FIRMS, MUST_HAVE_SIGNALS, NICE_TO_HAVE_SIGNALS, WEIGHTS
from text_utils import (
    build_candidate_text,
    has_keyword,
    is_ml_title,
    is_non_ml_title,
    keyword_hits,
    production_evidence,
    skill_map,
)

def _signal_score(full_text: str, skills: dict[str, dict], spec: dict) -> tuple[float, list[str]]:
    hits: list[str] = []
    score = 0.0
    for keyword in spec["keywords"]:
        if has_keyword(full_text, keyword):
            hits.append(keyword)
    for skill_name in spec["skills"]:
        if skill_name in skills:
            hits.append(skills[skill_name]["name"])
    if hits:
        score = min(1.0, 0.55 + 0.15 * min(len(set(hits)), 3))
        for skill_name in spec["skills"]:
            skill = skills.get(skill_name)
            if not skill:
                continue
            prof_bonus = {"beginner": 0.0, "intermediate": 0.05, "advanced": 0.10, "expert": 0.15}
            duration = skill.get("duration_months", 0)
            endorsements = skill.get("endorsements", 0)
            score += prof_bonus.get(skill.get("proficiency", "beginner"), 0.0)
            if duration >= 24:
                score += 0.05
            if endorsements >= 10:
                score += 0.03
        score = min(1.0, score)
    return score, sorted(set(hits))

def semantic_fit_score(semantic_similarity: float) -> float:
    # Scale from 0.0-1.0 to 0-100
    return max(0.0, min(100.0, semantic_similarity * 100.0))

def skill_fit_score(candidate: dict, full_text: str, jd_skills: list[str] | None = None) -> tuple[float, dict]:
    skills = skill_map(candidate)
    evidence: dict[str, list[str]] = {"must_have": [], "nice_to_have": [], "production": production_evidence(full_text)}

    if jd_skills:
        # Match candidate skills against dynamic JD skills list
        matched_skills = []
        for skill_name in jd_skills:
            skill_name_lower = skill_name.lower()
            if skill_name_lower in skills:
                matched_skills.append(skill_name)
                evidence["must_have"].append(skill_name)
            elif has_keyword(full_text, skill_name_lower):
                matched_skills.append(skill_name)
                evidence["nice_to_have"].append(skill_name)

        # Base score is proportion of matched skills
        base = len(matched_skills) / len(jd_skills) if jd_skills else 0.0
        
        # Add proficiency and duration bonuses from explicit candidate profile skills
        bonus = 0.0
        for skill_name in jd_skills:
            skill_name_lower = skill_name.lower()
            if skill_name_lower in skills:
                cand_skill = skills[skill_name_lower]
                prof = cand_skill.get("proficiency", "beginner") or "beginner"
                prof_bonus = {"beginner": 0.0, "intermediate": 0.05, "advanced": 0.10, "expert": 0.15}
                bonus += prof_bonus.get(prof, 0.0)
                
                duration = cand_skill.get("duration_months", 0) or 0
                if duration >= 24:
                    bonus += 0.05
                endorsements = cand_skill.get("endorsements", 0) or 0
                if endorsements >= 10:
                    bonus += 0.03

        production_bonus = min(0.10, 0.03 * len(evidence["production"]))
        score = min(1.0, base + bonus + production_bonus)
    else:
        # Fallback to static weights if no jd_skills provided
        must_total = 0.0
        must_weight = 0.0
        for name, spec in MUST_HAVE_SIGNALS.items():
            score, hits = _signal_score(full_text, skills, spec)
            must_total += score * spec["weight"]
            must_weight += spec["weight"]
            if hits:
                evidence["must_have"].extend(hits)

        nice_total = 0.0
        nice_weight = 0.0
        for _, spec in NICE_TO_HAVE_SIGNALS.items():
            score, hits = _signal_score(full_text, skills, spec)
            nice_total += score * spec["weight"]
            nice_weight += spec["weight"]
            if hits:
                evidence["nice_to_have"].extend(hits)

        base = (must_total / must_weight if must_weight else 0.0) * 0.78
        bonus = (nice_total / nice_weight if nice_weight else 0.0) * 0.12
        production_bonus = min(0.10, 0.03 * len(evidence["production"]))
        score = min(1.0, base + bonus + production_bonus)

    assessment_scores = candidate.get("redrob_signals", {}).get("skill_assessment_scores", {})
    if assessment_scores:
        relevant = [
            value
            for key, value in assessment_scores.items()
            if any(token in key.lower() for token in ("python", "ml", "nlp", "retrieval", "search", "rank"))
        ]
        if relevant:
            score = min(1.0, score + 0.05 * (sum(relevant) / len(relevant) / 100))

    return score * 100.0, evidence

def experience_fit_score(candidate: dict) -> tuple[float, dict]:
    profile = candidate["profile"]
    yoe = profile.get("years_of_experience", 0.0)
    score = 0.0
    notes: list[str] = []

    # Years of experience scoring
    if 5.0 <= yoe <= 9.0:
        score += 60.0
        notes.append("ideal 5-9yr experience band")
    elif 4.0 <= yoe <= 10.0:
        score += 50.0
        notes.append("within target experience band")
    elif 3.0 <= yoe <= 15.0:
        score += 35.0
    else:
        score += 15.0

    # Role progression and title check
    roles = candidate.get("career_history", [])
    titles = [(role.get("title") or "").lower() for role in roles]
    if any("senior" in title or "lead" in title or "principal" in title or "founding" in title for title in titles[-2:]):
        score += 20.0
        notes.append("recent senior progression")

    # Tenure stability
    if roles:
        durations = [role.get("duration_months") or 0 for role in roles]
        median_months = sorted(durations)[len(durations) // 2]
        if median_months >= 36:
            score += 20.0
            notes.append("stable tenure")
        elif median_months >= 24:
            score += 15.0
        elif median_months >= 18:
            score += 8.0

    return min(100.0, score), {"notes": notes}

def production_experience_score(full_text: str) -> float:
    # Explicitly check for production scale, serving, deployment keywords
    evidence = production_evidence(full_text)
    n_hits = len(evidence)
    if n_hits >= 4:
        return 100.0
    elif n_hits == 3:
        return 85.0
    elif n_hits == 2:
        return 65.0
    elif n_hits == 1:
        return 45.0
    return 20.0

def behavioral_intelligence_score(candidate: dict) -> tuple[float, dict]:
    signals = candidate.get("redrob_signals", {})
    score = 0.0
    notes: list[str] = []

    # Open To Work
    if signals.get("open_to_work_flag"):
        score += 20.0
        notes.append("open to work")

    # GitHub Activity
    github = signals.get("github_activity_score", -1)
    if github >= 60:
        score += 20.0
        notes.append("highly active github")
    elif github >= 30:
        score += 12.0
        notes.append("active github")

    # Recruiter Response Rate
    response_rate = signals.get("recruiter_response_rate", 0.0)
    score += min(15.0, response_rate * 15.0)
    if response_rate >= 0.6:
        notes.append(f"high recruiter response rate ({response_rate:.0%})")

    # Interview Completion Rate
    interview_rate = signals.get("interview_completion_rate", 0.0)
    score += min(15.0, interview_rate * 15.0)

    # Saved By Recruiters
    saved = signals.get("saved_by_recruiters_30d", 0)
    if saved >= 5:
        score += 15.0
        notes.append("strong recruiter interest")
    elif saved >= 2:
        score += 8.0

    # Profile Completeness
    completeness = signals.get("profile_completeness_score", 0.0)
    score += min(10.0, completeness * 0.10)

    # Search Appearances
    search = signals.get("search_appearance_30d", 0)
    if search >= 100:
        score += 5.0

    return min(100.0, score), {"notes": notes}

def recruitability_score(candidate: dict) -> tuple[float, dict]:
    signals = candidate.get("redrob_signals", {})
    score = 0.0
    notes: list[str] = []

    # Response Rate
    response_rate = signals.get("recruiter_response_rate", 0.0)
    score += min(30.0, response_rate * 30.0)

    # Notice Period (lower is better)
    notice = signals.get("notice_period_days", 180)
    if notice <= 15:
        score += 25.0
        notes.append("immediate joiner")
    elif notice <= 30:
        score += 20.0
        notes.append("short notice (<=30d)")
    elif notice <= 60:
        score += 12.0
    elif notice <= 90:
        score += 5.0

    # Interview Completion Rate
    interview_rate = signals.get("interview_completion_rate", 0.0)
    score += min(20.0, interview_rate * 20.0)

    # Offer Acceptance Rate
    offer_rate = signals.get("offer_acceptance_rate", -1.0)
    if offer_rate >= 0.7:
        score += 15.0
    elif offer_rate >= 0.4:
        score += 8.0

    # Recent Activity Date
    last_active = signals.get("last_active_date")
    if last_active:
        try:
            days = (date.today() - datetime.strptime(last_active, "%Y-%m-%d").date()).days
            if days <= 15:
                score += 10.0
                notes.append("active recently")
            elif days <= 45:
                score += 6.0
            elif days <= 90:
                score += 2.0
        except ValueError:
            pass

    return min(100.0, score), {"notes": notes}

def growth_score(candidate: dict) -> tuple[float, dict]:
    roles = candidate.get("career_history", [])
    if not roles:
        return 20.0, {"notes": ["no career history"]}

    score = 30.0  # Base score
    notes: list[str] = []    # Determine progression by analyzing titles sequentially from oldest to newest
    titles = [(role.get("title") or "").lower() for role in reversed(roles)]
    
    levels = []
    for title in titles:
        if "intern" in title or "trainee" in title or "co-op" in title:
            levels.append(0)
        elif "junior" in title or "associate" in title:
            levels.append(1)
        elif "senior" in title or "sr" in title:
            levels.append(3)
        elif "lead" in title or "principal" in title or "founding" in title or "head" in title or "manager" in title or "director" in title:
            levels.append(4)
        else:
            levels.append(2)  # Regular engineer / scientist

    # Check if levels are strictly or mostly non-decreasing
    progression = 0
    for i in range(len(levels) - 1):
        if levels[i+1] > levels[i]:
            progression += 1
        elif levels[i+1] < levels[i]:
            progression -= 1

    if progression > 0:
        score += min(50.0, progression * 20.0)
        notes.append("positive career progression")
    elif progression == 0 and len(levels) > 1:
        score += 15.0
    
    # Title longevity / stability bonus
    non_job_hopper = True
    for role in roles:
        if (role.get("duration_months") or 0) < 12:
            non_job_hopper = False
    
    if non_job_hopper and len(roles) >= 2:
        score += 20.0
        notes.append("progressive tenure stability")

    return min(100.0, score), {"notes": notes}

def risk_score(candidate: dict, full_text: str) -> tuple[float, dict]:
    # Risk score ranges from 0 (no risk) to 100 (extreme risk)
    # Higher risk = lower final ranking
    risk = 0.0
    signals = candidate.get("redrob_signals", {})
    notes: list[str] = []

    # 1. Keyword Stuffers Check
    title = candidate["profile"].get("current_title") or ""
    skills = candidate.get("skills", [])
    ai_skill_count = sum(
        1 for skill in skills 
        if any(token in (skill.get("name") or "").lower() for token in ("ai", "ml", "llm", "nlp", "embedding", "pytorch", "tensorflow", "rag"))
    )
    if is_non_ml_title(title) and ai_skill_count >= 5:
        risk += 35.0
        notes.append("non-ML title with stuffed AI skills")

    # 2. High Notice Period
    notice = signals.get("notice_period_days", 180)
    if notice >= 90:
        risk += 15.0
        notes.append(f"long notice period ({notice} days)")

    # 3. Poor Recruiter Response
    response_rate = signals.get("recruiter_response_rate", 1.0)
    if response_rate < 0.2:
        risk += 20.0
        notes.append("extremely low recruiter response")

    # 4. Low Activity
    last_active = signals.get("last_active_date")
    if last_active:
        try:
            days = (date.today() - datetime.strptime(last_active, "%Y-%m-%d").date()).days
            if days > 180:
                risk += 15.0
                notes.append("inactive for >6 months")
        except ValueError:
            pass

    # 5. Low Profile Completeness
    completeness = signals.get("profile_completeness_score", 100.0)
    if completeness < 30.0:
        risk += 15.0
        notes.append("incomplete profile")

    return min(100.0, risk), {"notes": notes}

def composite_score(subscores: dict, semantic_similarity: float) -> float:
    # subscores contains all precomputed engine values scaled to 0-100.
    # We calculate the weighted DNA score, then apply penalty multiplier, then scale to 0.0-1.0
    weighted_score = (
        WEIGHTS["semantic_score"] * subscores["semantic_score"]
        + WEIGHTS["skill_score"] * subscores["skill_score"]
        + WEIGHTS["production_score"] * subscores["production_score"]
        + WEIGHTS["behavior_score"] * subscores["behavior_score"]
        + WEIGHTS["recruitability_score"] * subscores["recruitability_score"]
        + WEIGHTS["growth_score"] * subscores["growth_score"]
        + WEIGHTS["experience_score"] * subscores["experience_score"]
    )
    
    # Scale from 0-100 down to 0.0-1.0
    base_dna_score = weighted_score / 100.0
    
    return base_dna_score * subscores["penalty_multiplier"]

# Backwards compatibility wrappers for UI (app.py) and FastAPI backend (backend/main.py)
def technical_fit(candidate: dict, full_text: str | None = None) -> tuple[float, dict]:
    from text_utils import build_candidate_text
    full_text = full_text or build_candidate_text(candidate)
    score, evidence = skill_fit_score(candidate, full_text)
    return score / 100.0, evidence

def career_quality(candidate: dict, full_text: str | None = None) -> tuple[float, dict]:
    score, info = experience_fit_score(candidate)
    return score / 100.0, {"notes": info.get("notes", [])}

def availability(candidate: dict) -> tuple[float, dict]:
    score, info = recruitability_score(candidate)
    return score / 100.0, {"notes": info.get("notes", [])}

def seniority_fit(candidate: dict) -> tuple[float, dict]:
    score, info = experience_fit_score(candidate)
    return score / 100.0, {"notes": info.get("notes", [])}

