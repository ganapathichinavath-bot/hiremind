"""Evidence-backed reasoning strings for HIREMIND AI."""

from __future__ import annotations
import re

def build_reasoning(candidate: dict, subscores: dict, evidence: dict, rank: int) -> str:
    profile = candidate["profile"]
    title = profile.get("current_title", "AI Engineer")
    yoe = profile.get("years_of_experience", 0)
    
    # 1. Base statement
    exp_text = f"{yoe:.1f} years of experience"
    
    # 2. Key skills matching
    skills = []
    must_haves = evidence.get("must_have", [])
    if must_haves:
        skills.extend(must_haves[:2])
    nice_to_haves = evidence.get("nice_to_have", [])
    if nice_to_haves:
        skills.extend(nice_to_haves[:1])
    
    skills_text = ""
    if skills:
        skills_text = f" building systems with {', '.join(skills)}"
        
    # 3. Production experience
    prod = evidence.get("production", [])
    prod_text = ""
    if prod:
        prod_text = f", featuring production exposure in {', '.join(prod[:2])}"

    # 4. Behavioral and recruitability strengths
    signals = candidate.get("redrob_signals", {})
    behavior_notes = []
    if signals.get("open_to_work_flag"):
        behavior_notes.append("open to work")
    github_score = signals.get("github_activity_score", -1)
    if github_score >= 30:
        behavior_notes.append("active on GitHub")
    
    availability_text = ""
    if behavior_notes:
        availability_text = f" Active candidate ({', '.join(behavior_notes)})."

    # 5. Gaps / concerns (if any)
    penalties = subscores.get("penalties", [])
    concern_text = ""
    if penalties and rank <= 50:
        concern_text = f" Gaps include {penalties[0]}."
    elif rank > 70:
        concern_text = " Displays adjacent fit with minor gaps in core ML retrieval depth."

    # Combine sentences
    sentence_1 = f"{title} with {exp_text}{skills_text}{prod_text}."
    sentence_2 = f"{availability_text}{concern_text}".strip()
    
    reasoning = f"{sentence_1} {sentence_2}".strip()
    reasoning = re.sub(r'\s+', ' ', reasoning)
    
    if len(reasoning) > 295:
        reasoning = reasoning[:292] + "..."
    return reasoning
