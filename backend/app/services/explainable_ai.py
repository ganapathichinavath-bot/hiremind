from typing import Dict, List, Any

def generate_explanation(candidate: Dict[str, Any], subscores: Dict[str, Any], jd_skills: List[str], rank: int) -> Dict[str, Any]:
    profile = candidate.get("profile", {})
    yoe = profile.get("years_of_experience", 0.0) or 0.0
    cand_skills_lower = [s.get("name", "").lower() for s in candidate.get("skills", [])]
    
    strengths = []
    weaknesses = []
    missing_skills = []
    
    # Analyze strengths
    if subscores.get("semantic_score", 0.0) >= 0.75:
        strengths.append("Exceptional semantic alignment with core JD requirements")
    elif subscores.get("semantic_score", 0.0) >= 0.60:
        strengths.append("Good semantic alignment with the job description")
        
    if yoe >= 5.0 and yoe <= 9.0:
        strengths.append(f"Ideal industry experience ({yoe} years)")
    elif yoe > 9.0:
        strengths.append(f"Deep industry experience ({yoe} years)")
        
    if subscores.get("behavioral_score", 0.0) >= 0.70:
        strengths.append("High platform engagement and hiring responsiveness")
    elif subscores.get("behavioral_score", 0.0) >= 0.50:
        strengths.append("Consistent platform activity and profile completeness")
        
    history = candidate.get("career_history", [])
    titles = [role.get("title", "").lower() for role in history]
    if any("senior" in t or "lead" in t or "principal" in t for t in titles[:2]):
        strengths.append("Demonstrated senior or lead level engineering history")

    # Assess nice-to-haves
    if any(s in cand_skills_lower for s in ["fine-tuning", "lora", "qlora", "peft"]):
        strengths.append("Hands-on LLM fine-tuning experience (LoRA/QLoRA)")
        
    # Analyze weaknesses
    if subscores.get("is_honeypot", False):
        weaknesses.append("Disqualified: Profile metadata anomalies detected (potential honeypot)")
    if subscores.get("is_disqualified", False) and not subscores.get("is_honeypot", False):
        if subscores.get("disqualification_reason"):
            weaknesses.append(f"Concern: {subscores.get('disqualification_reason')}")
            
    signals = candidate.get("redrob_signals", {})
    notice = signals.get("notice_period_days", 0) or 0
    if notice >= 90:
        weaknesses.append(f"Long notice period ({notice} days)")
        
    response_rate = signals.get("recruiter_response_rate", 1.0) or 1.0
    if response_rate < 0.3:
        weaknesses.append("Low recruiter response rate on platform")

    # Missing skills
    for skill in jd_skills:
        if skill.lower() not in cand_skills_lower:
            missing_skills.append(skill)
            
    # Default strengths if empty
    if not strengths:
        strengths.append("Standard professional background matching adjacent roles")
        
    # Rank description sentence
    match_pct = int(subscores.get("score", 0.0) * 100)
    
    if subscores.get("is_honeypot", False):
        why_statement = "Disqualified at Rank #100 or lower due to honeypot validation failure."
    elif rank <= 10:
        why_statement = f"Ranked at #{rank} due to stellar semantic profile, top-tier skills match, and strong platform response."
    elif rank <= 50:
        why_statement = f"Ranked at #{rank} representing a strong candidate with relevant experience, though with minor skill gaps."
    else:
        why_statement = f"Ranked at #{rank} due to basic alignment with roles but containing several missing skills or notice period constraints."

    return {
        "match_percentage": match_pct,
        "strengths": strengths[:4],
        "weaknesses": weaknesses[:3],
        "missing_skills": missing_skills[:4],
        "why_statement": why_statement
    }
