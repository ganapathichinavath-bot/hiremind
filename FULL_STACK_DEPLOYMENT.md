# Full-Stack Deployment Guide

This project now supports the stack from the India Runs Track 1 plan:

```text
frontend/  Next.js + Tailwind, deploy to Vercel
backend/   FastAPI ranking API, deploy to Railway/Render/Hugging Face Docker Space
artifacts/ Local TF-IDF/SVD ranking artifacts from precompute.py
output/    generated ranked CSV files
```

## Recommended Free Setup

### Frontend: Vercel

1. Push the repository to GitHub.
2. In Vercel, import the repo.
3. Set the root directory to `frontend`.
4. Add environment variable:

```text
NEXT_PUBLIC_API_URL=https://YOUR_BACKEND_URL
```

5. Deploy.

### Backend: Railway or Render

1. Create a new Python service from the same GitHub repo.
2. Set the root directory to `backend`.
3. Use:

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port $PORT
```

4. Deploy artifacts and candidate data if you want full-corpus mode.

## Important Free-Tier Reality

The current challenge data is large:

- `candidates.jsonl`: about 487 MB
- `artifacts/embeddings.npy`: about 153 MB

For a fully public free deployment, the cleanest option is:

- deploy the frontend publicly on Vercel
- deploy the backend on Hugging Face Spaces or Railway
- include the precomputed artifacts if the host allows it
- avoid publishing private candidate data unless the competition permits it

If you cannot publish `candidates.jsonl`, keep the backend in upload/API mode or deploy privately for judges.

## Local Development

Start backend:

```bash
cd redrob-ranker
.venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Start frontend:

```bash
cd redrob-ranker/frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

## API

Health:

```http
GET /health
```

Rank full deployed corpus:

```http
POST /rank
Content-Type: application/json

{
  "job_description": "Senior AI Engineer with Python, embeddings, vector search...",
  "top_k": 25
}
```

Rank supplied candidates:

```http
POST /rank
Content-Type: application/json

{
  "job_description": "Senior AI Engineer with Python, embeddings, vector search...",
  "top_k": 25,
  "candidates": []
}
```

Export:

```http
POST /rank/export
```

## Model Training

No LLM or BERT fine-tuning is required for the current production version.

The existing ranking system uses local TF-IDF + SVD embeddings plus structured scoring. Run this when the JD, candidate corpus, or scoring logic changes:

```bash
python precompute.py
```

You can add `sentence-transformers/all-MiniLM-L6-v2` later, but it increases deployment size and cold-start time. For a free-tier hackathon deployment, the existing local artifacts are faster and easier to host.
