"""Configuration for the Redrob candidate ranker."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT.parent / "[PUB] India_runs_data_and_ai_challenge" / "India_runs_data_and_ai_challenge"
if not DATA_DIR.exists():
    DATA_DIR = Path("c:/Users/Gani/Downloads/INDIA RUNS project/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge")
ARTIFACTS_DIR = ROOT / "artifacts"
OUTPUT_DIR = ROOT / "output"

CANDIDATES_PATH = DATA_DIR / "candidates.jsonl"
JOB_DESCRIPTION_PATH = DATA_DIR / "job_description.docx"
VALIDATOR_PATH = DATA_DIR / "validate_submission.py"

EMBEDDING_DIM = 384

TOP_K = 100
SCORE_STEP = 0.008

WEIGHTS = {
    "semantic_score": 0.30,
    "skill_score": 0.20,
    "production_score": 0.15,
    "behavior_score": 0.15,
    "recruitability_score": 0.10,
    "growth_score": 0.05,
    "experience_score": 0.05,
}

ML_TITLE_KEYWORDS = (
    "ai engineer",
    "ml engineer",
    "machine learning",
    "data scientist",
    "research engineer",
    "nlp engineer",
    "applied ml",
    "recommendation",
    "ai specialist",
    "ai research",
    "deep learning",
    "llm engineer",
)

NON_ML_TITLE_KEYWORDS = (
    "hr manager",
    "marketing manager",
    "accountant",
    "civil engineer",
    "mechanical engineer",
    "graphic designer",
    "content writer",
    "customer support",
    "sales executive",
    "operations manager",
    "project manager",
    "business analyst",
    "qa engineer",
    "frontend engineer",
    "backend engineer",
    "account manager",
)

CONSULTING_FIRMS = {
    "tcs",
    "infosys",
    "wipro",
    "accenture",
    "cognizant",
    "capgemini",
    "hcl",
    "tech mahindra",
    "mindtree",
    "ltimindtree",
    "lti",
    "mphasis",
    "persistent",
    "cyient",
}

MUST_HAVE_SIGNALS = {
    "embeddings_retrieval": {
        "weight": 0.25,
        "keywords": (
            "embedding",
            "retrieval",
            "vector search",
            "semantic search",
            "information retrieval",
            "sentence-transformer",
            "dense retrieval",
            "hybrid search",
            "rag",
            "recommendation system",
            "ranking system",
            "search system",
        ),
        "skills": (
            "embeddings",
            "information retrieval",
            "vector search",
            "semantic search",
            "rag",
            "recommendation systems",
            "search ranking",
            "retrieval",
        ),
    },
    "vector_db": {
        "weight": 0.20,
        "keywords": (
            "pinecone",
            "weaviate",
            "qdrant",
            "milvus",
            "faiss",
            "opensearch",
            "elasticsearch",
            "vector database",
            "vector db",
            "ann index",
        ),
        "skills": (
            "pinecone",
            "weaviate",
            "qdrant",
            "milvus",
            "faiss",
            "elasticsearch",
            "opensearch",
            "vector databases",
        ),
    },
    "python": {
        "weight": 0.15,
        "keywords": ("python", "pyspark", "fastapi", "flask", "django"),
        "skills": ("python", "pyspark", "fastapi"),
    },
    "eval_framework": {
        "weight": 0.15,
        "keywords": (
            "ndcg",
            "mrr",
            "map@",
            "mean average precision",
            "offline evaluation",
            "a/b test",
            "ab test",
            "recall@",
            "precision@",
            "evaluation framework",
            "ranking metric",
        ),
        "skills": (
            "ndcg",
            "mrr",
            "map",
            "model evaluation",
            "experimentation",
            "a/b testing",
        ),
    },
}

NICE_TO_HAVE_SIGNALS = {
    "llm_finetuning": {
        "weight": 0.10,
        "keywords": ("fine-tun", "lora", "qlora", "peft", "instruction tuning"),
        "skills": ("fine-tuning llms", "lora", "peft", "llm fine-tuning"),
    },
    "learning_to_rank": {
        "weight": 0.10,
        "keywords": ("learning to rank", "ltr", "xgboost rank", "lambda rank", "ranknet"),
        "skills": ("learning to rank", "ranking models"),
    },
    "hr_tech": {
        "weight": 0.05,
        "keywords": ("recruit", "hiring", "talent", "hr tech", "candidate matching", "job matching"),
        "skills": ("recruitment tech", "hr analytics"),
    },
}

PRODUCTION_KEYWORDS = (
    "production",
    "deploy",
    "serving",
    "online",
    "at scale",
    "real users",
    "a/b",
    "latency",
    "throughput",
    "monitoring",
    "on-call",
    "ship",
    "shipped",
    "live system",
)

RESEARCH_ONLY_KEYWORDS = (
    "published paper",
    "journal",
    "thesis",
    "academic lab",
    "pure research",
    "research assistant",
)

CV_ONLY_KEYWORDS = (
    "computer vision",
    "object detection",
    "image segmentation",
    "speech recognition",
    "robotics",
    "autonomous vehicle",
)
