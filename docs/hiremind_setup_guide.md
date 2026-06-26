# Setup and Deployment Guide - HireMind AI

This guide contains instructions on how to run HireMind AI locally and deploy it online to platforms like Vercel and Render.

---

## 1. Local Development Setup

### Prerequisites
- Python 3.10 or 3.11
- Node.js v18 or later
- Git

### Step-by-Step Installation

1. **Clone and Setup Virtual Environment**:
   ```bash
   git clone <your-repo-url>
   cd redrob-ranker
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # macOS/Linux
   ```

2. **Install Python Dependencies**:
   ```bash
   # Downgrade NumPy first to support sentence-transformers
   pip install "numpy<2.0"
   pip install -r requirements.txt
   pip install -r backend/requirements.txt
   ```

3. **Run Precomputation & Database Seeding**:
   ```bash
   python precompute.py
   python seed.py
   ```

4. **Start the FastAPI Backend**:
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```

5. **Start the Next.js Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open `http://localhost:3000` in your browser.

---

## 2. Production Deployment

### Database: Supabase (PostgreSQL)
1. Sign up on [Supabase](https://supabase.com/).
2. Create a new project and navigate to **Project Settings** -> **Database**.
3. Copy the **URI Connection String** (mode: Transaction, port: 6543 or 5432).

### Backend: Render
1. Sign up on [Render](https://render.com/).
2. Create a new **Web Service** and connect your GitHub repository.
3. Configure settings:
   - **Root Directory**: `.` (Build context must be at root to include `signals.py`, `disqualify.py`, etc.)
   - **Environment**: `Docker`
   - **Docker Path**: `backend/Dockerfile`
4. Under **Environment Variables**, add:
   - `DATABASE_URL`: Your Supabase connection string.
   - `PORT`: `8000`
5. Deploy the service.

### Frontend: Vercel
1. Sign up on [Vercel](https://vercel.com/).
2. Click **Add New** -> **Project** and select your repository.
3. Configure settings:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Next.js`
4. Under **Environment Variables**, add:
   - `NEXT_PUBLIC_API_URL`: The URL of your Render backend (e.g. `https://hiremind-backend.onrender.com`).
5. Click **Deploy**.
