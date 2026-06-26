---
title: hiremind-backend
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# HIREMIND AI — Recruiter Copilot 🚀

HIREMIND AI is a professional, high-performance, full-stack candidate discovery, matching, and ranking platform built for recruiters. The system automatically processes candidate profiles, dynamically parses target Job Descriptions (JDs), and calculates hybrid match scores using local vector embeddings and recruiter-grade heuristic signals.

---

## 🌟 Key Features

### 1. Dynamic Job Description (JD) Parsing
- **Multi-Domain Support**: Extract skills, target experience bands, education requirements, and responsibilities from *any* uploaded JD (e.g., Java Backend, Frontend React, DevOps, ML/AI, QA, Product Management).
- **Advanced Skill Extractor**: Merges matching against a broad predefined 150+ technology vocabulary with a heuristic section-based parser to dynamically isolate capitalized technologies (e.g., *Snowflake*, *Kubernetes*) from bullets.

### 2. Smart Hybrid Scoring Pipeline
- **Local Semantic Embeddings**: Utilizes a local TF-IDF + TruncatedSVD projection model (yielding 384-dimensional vectors) to calculate candidate-to-JD cosine similarity without relying on external network APIs.
- **Dynamic Skill Fit**: Scores candidates based on their explicit skills profile and summary text matching the JD requirements. Includes experience and proficiency multipliers (e.g., advanced vs. intermediate) and tenure bonuses.
- **Conditional ML Penalties**: Retains strict filtering rules for AI/ML/RAG roles (such as lack of ML trajectory or keyword stuffing) while allowing non-ML profiles to rank normally without unfair penalization.

### 3. Bulletproof Database Architecture
- **SQLite Concurrency**: Connects with `timeout=30` and `check_same_thread=False` to handle simultaneous transaction writes on local development environments without database lock issues.
- **ChromaDB Fault Tolerance**: Wrapped in try-except isolation and mock fallbacks so that if the vector database client experiences permission or lock issues, the main SQL database operations and web endpoints continue functioning seamlessly.

### 4. Interactive Recruiter Workspace
- **Candidate Ingest**: Drag-and-drop `.jsonl` dataset upload with real-time schema validation and automatic vector storage sync.
- **Job Criteria Setup**: Immediate extraction and visualization of requirements.
- **Match & Rank Engine**: Ranks candidate pools in milliseconds, presenting a formatted dashboard complete with medal tiers, match percentages, and explainable AI-reasoning explanations.
- **Saved Candidates & Export**: Handpick shortlists and download a submission-ready CSV with candidate rankings and explanations.

---

## 🏗️ Architecture

```text
redrob-ranker/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routes (auth, candidates, jobs)
│   │   ├── database/       # SQLAlchemy engine & SQLite connection
│   │   ├── models/         # Database models (User, Candidate, JobDescription)
│   │   ├── ranking/        # Scoring pipeline and penalty rules
│   │   ├── schemas/        # Pydantic schemas for request/response validation
│   │   ├── services/       # Vector storage interface (ChromaDB)
│   │   └── utils/          # Document and criteria parsers
│   └── main.py             # Backend main app entrypoint
├── frontend/
│   ├── src/
│   │   ├── components/     # Layout, navigation, UI wrappers
│   │   ├── pages/          # Dashboard, job criteria, matching list pages
│   │   └── providers/      # Authentication state providers
├── artifacts/              # Local precomputed TF-IDF vectorizer & SVD projections
└── seed.py                 # Automated SQL database and ChromaDB seeder
```

---

## 💻 Local Setup & Installation

### Prerequisites
- Python 3.10 or 3.11
- Node.js (v18+) & npm

### 1. Backend Setup
1. Open a terminal in the root directory:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```
2. Run the FastAPI development server:
   ```bash
   .\.venv\Scripts\uvicorn backend.app.main:app --reload --port 8000
   ```
   *Note: Upon startup, the database is auto-created and seeded with mock candidates if it is empty.*

### 2. Frontend Setup
1. In a separate terminal, navigate to the frontend folder:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
2. Open your browser and go to [http://localhost:3000](http://localhost:3000).
3. Log in using the default administrator credentials:
   - **Username**: `admin`
   - **Password**: `admin123`

---

## 📊 Core Scoring Signals

HIREMIND AI ranks candidates on a scale of **0% to 100% Match** using a weighted composite score:

1. **Semantic Fit (30%)**: Cosine similarity between candidate summary/headline and JD text.
2. **Skill Fit (20%)**: Proportion of target JD skills possessed by the candidate, boosted by advanced proficiency, duration, and endorsement counts.
3. **Production Experience (15%)**: Search matches for high-scale deployment, cloud, real-user, and latency keywords.
4. **Behavioral Intelligence (15%)**: Redrob platform availability signals, recruiter response rates, and GitHub activity scores.
5. **Recruitability & Availability (10%)**: Length of notice period (immediate joiner vs. 90-day wait) and recent activity date.
6. **Career progression & Seniority Fit (10%)**: Experience targets match (e.g. 5-9 years target), role tenure stability, and senior leadership progression.

---

## 🛡️ Disqualification & Penalties
To maintain top-tier candidate pools, the system applies multiplier penalties:
- **Consulting-only Career**: Penalized if the candidate has only worked at outsourcing/consulting IT firms.
- **Honeypot Trap**: Disqualifies candidate profiles with graduation timeline contradictions, implausible expert skill densities, or duration-date span mismatches.
- **Career Trajectory (ML Only)**: If matching for an ML role, non-ML titles or profiles lacking ML project trajectory are heavily penalized.

---

## 🔗 Main API Endpoints

### Authentication
- `POST /api/auth/login` - Authenticate recruiter credentials and retrieve JWT.
- `POST /api/auth/signup` - Register a new recruiter account.

### Candidate Ingestion
- `POST /api/candidates/upload` - Ingest, parse, and embed candidate `.jsonl` files.
- `GET /api/candidates` - Query, filter, and paginate candidate records.

### Job Criteria & Ranking
- `POST /api/jobs/upload` - Upload and parse DOCX/text Job Descriptions.
- `POST /api/jobs/rank` - Execute candidate ranking against the active JD.
- `GET /api/jobs/export/submission` - Download the top candidate rankings in CSV format.
