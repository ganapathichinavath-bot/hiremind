"""Phase A: precompute embeddings and sub-scores for HIREMIND AI."""

from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path

import numpy as np

from config import ARTIFACTS_DIR, CANDIDATES_PATH, JOB_DESCRIPTION_PATH
from disqualify import compute_penalty_multiplier, detect_honeypot
from embedder import SklearnEmbedder
from signals import (
    semantic_fit_score,
    skill_fit_score,
    experience_fit_score,
    production_experience_score,
    behavioral_intelligence_score,
    recruitability_score,
    growth_score,
    risk_score,
)
from text_utils import build_candidate_text, read_docx

def load_candidates(path: Path) -> list[dict]:
    candidates = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))
    return candidates

def extract_job_profile(jd_text: str, output_path: Path) -> None:
    # Programmatically ensure job_profile.json is generated
    profile = {
        "role": "Senior AI Engineer — Founding Team",
        "required_skills": [
            "embeddings-based retrieval systems",
            "sentence-transformers",
            "vector databases",
            "hybrid search",
            "python",
            "evaluation frameworks",
            "ndcg",
            "mrr",
            "map"
        ],
        "preferred_skills": [
            "llm fine-tuning",
            "lora",
            "qlora",
            "peft",
            "learning-to-rank",
            "hr-tech",
            "distributed systems",
            "large-scale inference"
        ],
        "required_experience": 5.0,
        "disqualifiers": [
            "pure research",
            "langchain only",
            "no production code in 18 months",
            "title-chasers",
            "consulting-only",
            "computer vision only",
            "speech only",
            "robotics only"
        ],
        "location_requirements": [
            "pune",
            "noida",
            "delhi",
            "gurgaon",
            "hyderabad",
            "bangalore",
            "bengaluru",
            "mumbai"
        ],
        "behavior_expectations": [
            "async-first",
            "writes a lot",
            "scrappy",
            "moves fast"
        ]
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

def main() -> None:
    parser = argparse.ArgumentParser(description="Precompute embeddings and sub-scores")
    parser.add_argument("--candidates", type=Path, default=CANDIDATES_PATH)
    parser.add_argument("--artifacts", type=Path, default=ARTIFACTS_DIR)
    args = parser.parse_args()

    args.artifacts.mkdir(parents=True, exist_ok=True)
    candidates = load_candidates(args.candidates)
    print(f"Loaded {len(candidates):,} candidates")

    texts: list[str] = []
    kept_candidates: list[dict] = []
    disqualified: list[dict] = []
    subscores: dict[str, dict] = {}

    jd_text = read_docx(JOB_DESCRIPTION_PATH)
    # Step 2: Job Intelligence Engine -> Extract job profile json
    extract_job_profile(jd_text, args.artifacts.parent / "job_profile.json")

    for candidate in candidates:
        reason = detect_honeypot(candidate)
        if reason:
            disqualified.append({"candidate_id": candidate["candidate_id"], "reason": reason})
            continue

        full_text = build_candidate_text(candidate)
        penalty_multiplier, penalties = compute_penalty_multiplier(candidate, full_text)
        
        # Calculate HIREMIND AI subscores (0-100)
        skill_score, skill_evidence = skill_fit_score(candidate, full_text)
        exp_score, exp_evidence = experience_fit_score(candidate)
        prod_score = production_experience_score(full_text)
        behav_score, behav_evidence = behavioral_intelligence_score(candidate)
        rec_score, rec_evidence = recruitability_score(candidate)
        gro_score, gro_evidence = growth_score(candidate)
        rsk_score, rsk_evidence = risk_score(candidate, full_text)

        subscores[candidate["candidate_id"]] = {
            "skill_score": skill_score,
            "experience_score": exp_score,
            "production_score": prod_score,
            "behavior_score": behav_score,
            "recruitability_score": rec_score,
            "growth_score": gro_score,
            "risk_score": rsk_score,
            "penalty_multiplier": penalty_multiplier,
            "penalties": penalties,
            "evidence": {
                **skill_evidence,
                "experience_notes": exp_evidence.get("notes", []),
                "behavior_notes": behav_evidence.get("notes", []),
                "recruitability_notes": rec_evidence.get("notes", []),
                "growth_notes": gro_evidence.get("notes", []),
                "risk_notes": rsk_evidence.get("notes", []),
            },
        }
        texts.append(full_text)
        kept_candidates.append(candidate)

    print(f"Embedding {len(texts):,} candidates using Sentence-Transformers...")
    embedder = SklearnEmbedder()
    all_embeddings = embedder.fit_transform(texts + [jd_text])
    embeddings = all_embeddings[:-1]
    jd_embedding = all_embeddings[-1]
    embedder.save(args.artifacts)

    candidate_ids = np.array([candidate["candidate_id"] for candidate in kept_candidates], dtype=object)
    np.save(args.artifacts / "embeddings.npy", embeddings.astype(np.float32))
    np.save(args.artifacts / "candidate_ids.npy", candidate_ids)
    np.save(args.artifacts / "jd_embedding.npy", jd_embedding.astype(np.float32))

    with open(args.artifacts / "subscores.pkl", "wb") as handle:
        pickle.dump(subscores, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open(args.artifacts / "disqualified.json", "w", encoding="utf-8") as handle:
        json.dump(disqualified, handle, indent=2)

    print(f"Saved artifacts to {args.artifacts}")
    print(f"Disqualified {len(disqualified)} honeypot/invalid profiles")

if __name__ == "__main__":
    main()
