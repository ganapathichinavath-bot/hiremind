# Redrob Candidate Ranker

Production-ready full-stack app and offline ranking pipeline for the INDIA RUNS Intelligent Candidate Discovery and Ranking Challenge.

The system ranks Senior AI Engineer candidates using a hybrid recruiter-style score:

- structured JD signals for retrieval, vector search, Python, evaluation, and production ML
- career consistency and seniority fit checks
- Redrob availability and hiring-intent signals
- local TF-IDF + SVD semantic similarity
- honeypot and keyword-stuffing penalties

No external API is required at ranking time.

## Production Stack

```text
frontend/  Next.js + Tailwind recruiter UI
backend/   FastAPI ranking API
artifacts/ local ranking model artifacts
output/    ranked CSV submissions
app.py     Streamlit fallback/demo app
```

The recommended public deployment is:

- frontend on Vercel
- backend on Railway, Render, or Hugging Face Spaces
- artifacts bundled or mounted on the backend host

See `FULL_STACK_DEPLOYMENT.md` for the free deployment guide.

## App Modes

### Upload Ranking

Public users can upload a JSON or JSONL candidate sample and download a ranked CSV with reasoning.

```bash
uvicorn backend.main:app --reload --port 8000
cd frontend
npm install
npm run dev
```

### Full Dataset Submission

When `candidates.jsonl` and the precomputed `artifacts/` directory are available on the server, the app can generate and download the top-100 `submission.csv`.

```bash
python precompute.py
python rank.py --out output/submission.csv
```

Expected data path:

```text
../[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/
  candidates.jsonl
  job_description.docx
  validate_submission.py
```

## Local Setup

```bash
cd redrob-ranker
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

### Streamlit Community Cloud

1. Push this folder to GitHub.
2. Set the app file to `app.py`.
3. Keep upload-ranking mode public.
4. For full-dataset mode, do not commit the 487 MB candidate file or 153 MB embedding file to GitHub. Use one of:
   - regenerate artifacts in a private build/release step
   - mount/download artifacts from object storage before app startup
   - deploy with Docker on a host that supports large private assets

### Render or Railway

Use the included `Procfile`:

```bash
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### Docker

```bash
docker build -t redrob-ranker .
docker run -p 8501:8501 redrob-ranker
```

If you need full-dataset mode inside Docker, include or mount:

```text
artifacts/
../[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl
../[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/job_description.docx
```

## Do We Need To Train A Model?

You do not need to train an LLM.

This project has a lightweight local fitting step:

```bash
python precompute.py
```

That step fits a TF-IDF vectorizer and TruncatedSVD projection on the candidate corpus plus the job description, then saves local artifacts. Think of it as classical embedding precomputation, not neural model training. It is CPU-only and does not send candidate data to any external service.

Retrain or regenerate artifacts when:

- the job description changes
- a new large candidate corpus is added
- scoring features or text extraction logic changes
- you want full-dataset ranking on a fresh deployment

You do not need retraining when:

- only the Streamlit UI changes
- users upload small samples and you are comfortable using the existing artifact vocabulary
- you are only downloading a previously generated `submission.csv`

## Project Layout

```text
redrob-ranker/
  app.py                 Streamlit production app
  config.py              paths, weights, keywords
  precompute.py          artifact generation
  rank.py                full-dataset top-100 ranking
  signals.py             structured scoring
  disqualify.py          honeypot and trap detection
  evidence.py            reasoning generation
  embedder.py            TF-IDF + SVD embedding helper
  Dockerfile             container deployment
  Procfile               Render/Railway-style deployment
  .streamlit/config.toml Streamlit server and theme config
```

## Validation

```bash
python rank.py --out output/submission.csv
python ../[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/validate_submission.py output/submission.csv
```
