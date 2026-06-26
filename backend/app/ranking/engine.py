import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Resolve root to import signals
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import signals
from disqualify import detect_honeypot, compute_penalty_multiplier
from text_utils import build_candidate_text

def score_candidate(candidate: Dict[str, Any], semantic_similarity: float, jd_skills: List[str]) -> Tuple[float, Dict[str, Any]]:
    # Honeypot check
    hp_reason = detect_honeypot(candidate)
    if hp_reason:
        return 0.0, {
            "score": 0.0,
            "semantic_score": semantic_similarity,
            "skill_score": 0.0,
            "experience_score": 0.0,
            "education_score": 0.0,
            "behavioral_score": 0.0,
            "production_score": 0.0,
            "recruitability_score": 0.0,
            "growth_score": 0.0,
            "risk_score": 1.0,
            "is_honeypot": True,
            "is_disqualified": True,
            "disqualification_reason": hp_reason,
            "penalties": [hp_reason]
        }

    full_text = build_candidate_text(candidate)
    penalty_multiplier, penalties = compute_penalty_multiplier(candidate, full_text)

    # Subscores from signals.py (0-100 range)
    sem_score = signals.semantic_fit_score(semantic_similarity)  # 0-100
    skill_score, skill_evidence = signals.skill_fit_score(candidate, full_text)
    exp_score, exp_evidence = signals.experience_fit_score(candidate)
    prod_score = signals.production_experience_score(full_text)
    behav_score, behav_evidence = signals.behavioral_intelligence_score(candidate)
    rec_score, rec_evidence = signals.recruitability_score(candidate)
    gro_score, gro_evidence = signals.growth_score(candidate)
    rsk_score, rsk_evidence = signals.risk_score(candidate, full_text)

    # Construct the subscores dictionary for composite_score
    subscores_dict = {
        "semantic_score": sem_score,
        "skill_score": skill_score,
        "experience_score": exp_score,
        "production_score": prod_score,
        "behavior_score": behav_score,
        "recruitability_score": rec_score,
        "growth_score": gro_score,
        "risk_score": rsk_score,
        "penalty_multiplier": penalty_multiplier,
    }

    # Final DNA score (0.0 - 1.0)
    final_score = signals.composite_score(subscores_dict, semantic_similarity)

    # Scale scores from 0-100 to 0.0-1.0
    return float(final_score), {
        "score": float(final_score),
        "semantic_score": float(sem_score / 100.0),
        "skill_score": float(skill_score / 100.0),
        "experience_score": float(exp_score / 100.0),
        "education_score": float(exp_score / 100.0),  # compatibility
        "behavioral_score": float(rec_score / 100.0),   # maps to recruitability/availability
        "production_score": float(prod_score / 100.0),
        "recruitability_score": float(rec_score / 100.0),
        "growth_score": float(gro_score / 100.0),
        "risk_score": float(rsk_score / 100.0),
        "is_honeypot": False,
        "is_disqualified": len(penalties) > 0,
        "disqualification_reason": ", ".join(penalties) if penalties else None,
        "penalties": penalties,
        "evidence": {
            **skill_evidence,
            "experience_notes": exp_evidence.get("notes", []),
            "behavior_notes": behav_evidence.get("notes", []),
            "recruitability_notes": rec_evidence.get("notes", []),
            "growth_notes": gro_evidence.get("notes", []),
            "risk_notes": rsk_evidence.get("notes", []),
        }
    }
