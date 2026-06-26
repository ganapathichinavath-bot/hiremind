#!/usr/bin/env python3
"""Generate the approach deck as PDF."""

from pathlib import Path

from fpdf import FPDF

OUTPUT = Path(__file__).resolve().parent / "docs" / "approach_deck.pdf"


class DeckPDF(FPDF):
    def sanitize(self, text: str) -> str:
        replacements = {
            "\u2014": "-",
            "\u2013": "-",
            "\u2192": "->",
            "\u2264": "<=",
            "\u00d7": "x",
            "\u2019": "'",
            "\u201c": '"',
            "\u201d": '"',
        }
        for src, dst in replacements.items():
            text = text.replace(src, dst)
        return text.encode("latin-1", "replace").decode("latin-1")

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, "Redrob Intelligent Candidate Ranker", align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def slide_title(self, title: str):
        self.set_text_color(20, 40, 90)
        self.set_font("Helvetica", "B", 22)
        self.multi_cell(0, 12, self.sanitize(title))
        self.ln(4)

    def bullet(self, text: str):
        self.set_text_color(30, 30, 30)
        self.set_font("Helvetica", "", 12)
        self.set_x(self.l_margin)
        self.multi_cell(self.w - self.l_margin - self.r_margin, 7, self.sanitize(f"- {text}"))


def main() -> None:
    pdf = DeckPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()
    pdf.slide_title("Intelligent Candidate Discovery & Ranking")
    pdf.set_font("Helvetica", "", 14)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(
        pdf.w - pdf.l_margin - pdf.r_margin,
        8,
        pdf.sanitize(
            "A hybrid AI recruiter that ranks candidates for Redrob's Senior AI Engineer role "
            "by understanding career context, not keyword density."
        ),
    )

    slides = [
        (
            "Problem",
            [
                "Recruiters miss strong fits because keyword filters reward profile stuffing.",
                "The JD explicitly warns that Marketing Managers with AI skills are traps.",
                "Behavioral signals (availability, response rate) matter as much as skills.",
                "Ground truth scoring weights top-10 quality heavily (NDCG@10 = 50%).",
            ],
        ),
        (
            "Design Principles",
            [
                "Read the JD as requirements + anti-patterns, not a bag of words.",
                "Separate offline precompute from the 5-minute CPU-only ranking step.",
                "Every reasoning string must cite facts present in the candidate profile.",
                "Penalize honeypots and title/skill inconsistency before semantic ranking.",
            ],
        ),
        (
            "Architecture",
            [
        "Phase A (precompute): stream 100K JSONL, disqualify honeypots, embed profiles with TF-IDF+SVD.",
                "Phase B (rank): cosine similarity + weighted structured sub-scores.",
                "Output: validated CSV with monotonic scores and evidence-backed reasoning.",
            ],
        ),
        (
            "Scoring Formula",
            [
                "Final score = penalty x (0.35 technical + 0.25 career + 0.20 availability + 0.12 seniority + 0.08 semantic).",
                "Technical fit tracks must-haves: embeddings/retrieval, vector DB, Python, eval metrics.",
                "Career quality rewards product-company ML roles, stable tenure, ranking/search delivery.",
                "Availability uses open-to-work, recency, recruiter response, notice period.",
            ],
        ),
        (
            "Trap & Honeypot Handling",
            [
                "Hard disqualify: impossible YoE vs career timeline, expert skills with zero usage.",
                "Heavy penalty: non-ML titles with 6+ AI keywords (HR Manager, Accountant, etc.).",
                "Soft penalty: consulting-only careers, CV-only focus, framework-demo profiles.",
                "Matches submission spec guidance and JD 'read between the lines' section.",
            ],
        ),
        (
            "Why This Beats Keyword Matching",
            [
                "A keyword ranker puts HR Managers with stuffed skills at rank 1 (see sample_submission.csv).",
                "Our title-career consistency gate surfaces real ML engineers with production retrieval evidence.",
                "Semantic similarity rescues candidates who describe ranking systems without saying 'RAG'.",
                "Behavioral down-weighting removes perfect-on-paper but unavailable candidates.",
            ],
        ),
        (
            "Reproducibility",
            [
                "python precompute.py",
                "python rank.py --candidates ../dataset/candidates.jsonl --out output/submission.csv",
                "Runs on CPU, no network during ranking, artifacts cached under artifacts/.",
                "Streamlit sandbox (app.py) supports small-sample validation for organizers.",
            ],
        ),
    ]

    for title, bullets in slides:
        pdf.add_page()
        pdf.slide_title(title)
        for bullet in bullets:
            pdf.bullet(bullet)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
