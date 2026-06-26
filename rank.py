"""Phase B: rank candidates and write submission CSV for HIREMIND AI."""

from __future__ import annotations

import argparse
import csv
import json
import pickle
import sys
from pathlib import Path

import numpy as np

from config import ARTIFACTS_DIR, CANDIDATES_PATH, OUTPUT_DIR, SCORE_STEP, TOP_K, VALIDATOR_PATH
from evidence import build_reasoning
from signals import composite_score, semantic_fit_score

def load_candidate_lookup(path: Path) -> dict[str, dict]:
    lookup: dict[str, dict] = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                candidate = json.loads(line)
                lookup[candidate["candidate_id"]] = candidate
    return lookup

def rank_candidates(artifacts_dir: Path) -> tuple[list[tuple[str, float, dict]], np.ndarray, dict]:
    embeddings = np.load(artifacts_dir / "embeddings.npy")
    candidate_ids = np.load(artifacts_dir / "candidate_ids.npy", allow_pickle=True)
    jd_embedding = np.load(artifacts_dir / "jd_embedding.npy")
    with open(artifacts_dir / "subscores.pkl", "rb") as handle:
        subscores = pickle.load(handle)

    # First Stage Retrieval: Retrieve Top 1000 Candidates using FAISS cosine similarity
    try:
        import faiss
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings.astype(np.float32))
        query = jd_embedding.reshape(1, -1).astype(np.float32)
        similarities, indices = index.search(query, 1000)
        top_1000_indices = indices[0]
        top_1000_similarities = similarities[0]
    except ImportError:
        # Fallback to NumPy
        semantic = embeddings @ jd_embedding
        top_1000_indices = np.argsort(-semantic)[:1000]
        top_1000_similarities = semantic[top_1000_indices]

    # Calculate Candidate DNA scores for the top 1000 candidates
    scored_candidates = []
    for idx, similarity in zip(top_1000_indices, top_1000_similarities):
        candidate_id = str(candidate_ids[idx])
        entry = subscores[candidate_id]
        
        # Calculate semantic fit score (0-100)
        entry["semantic_score"] = semantic_fit_score(float(similarity))
        
        # Compute DNA score using the configuration weights
        final_dna_score = composite_score(entry, float(similarity))
        scored_candidates.append((candidate_id, final_dna_score, entry))

    # Sort deterministically: final DNA score descending, candidate_id ascending
    sorted_candidates = sorted(scored_candidates, key=lambda x: (-x[1], x[0]))

    # Select the Top 100
    ranked = sorted_candidates[:TOP_K]
    return ranked, candidate_ids, subscores

def assign_monotonic_scores(ranked: list[tuple[str, float, dict]]) -> list[tuple[str, float, dict]]:
    if not ranked:
        return ranked
    # Align score assignments to validate successfully
    max_score = min(0.995, ranked[0][1])
    adjusted: list[tuple[str, float, dict]] = []
    for rank_index, (candidate_id, _, payload) in enumerate(ranked):
        score = round(max(0.05, max_score - rank_index * SCORE_STEP), 4)
        adjusted.append((candidate_id, score, payload))
    return adjusted

def write_submission(
    ranked: list[tuple[str, float, dict]],
    candidate_lookup: dict[str, dict],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for rank, (candidate_id, score, payload) in enumerate(ranked, start=1):
            candidate = candidate_lookup[candidate_id]
            reasoning = build_reasoning(candidate, payload, payload.get("evidence", {}), rank)
            writer.writerow([candidate_id, rank, f"{score:.4f}", reasoning])

def validate_submission(output_path: Path) -> None:
    if not VALIDATOR_PATH.exists():
        return
    import subprocess

    result = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), str(output_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    print(result.stdout.strip() or result.stderr.strip())
    if result.returncode != 0:
        raise SystemExit(result.returncode)

def main() -> None:
    parser = argparse.ArgumentParser(description="Rank candidates for the Redrob JD")
    parser.add_argument("--candidates", type=Path, default=CANDIDATES_PATH)
    parser.add_argument("--artifacts", type=Path, default=ARTIFACTS_DIR)
    parser.add_argument("--out", type=Path, default=OUTPUT_DIR / "submission.csv")
    parser.add_argument("--skip-validation", action="store_true")
    args = parser.parse_args()

    if not (args.artifacts / "embeddings.npy").exists():
        raise SystemExit(
            "Artifacts not found. Run `python precompute.py` first to generate embeddings and sub-scores."
        )

    print("Ranking candidates...")
    ranked, _, _ = rank_candidates(args.artifacts)
    ranked = assign_monotonic_scores(ranked)

    print("Loading candidate metadata for reasoning...")
    lookup = load_candidate_lookup(args.candidates)
    write_submission(ranked, lookup, args.out)
    print(f"Wrote {args.out}")

    if not args.skip_validation:
        validate_submission(args.out)

if __name__ == "__main__":
    main()
