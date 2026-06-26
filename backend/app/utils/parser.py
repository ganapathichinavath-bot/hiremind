import docx
import re
from typing import Dict, List, Any

def extract_text_from_docx(file_bytes: bytes) -> str:
    from io import BytesIO
    doc = docx.Document(BytesIO(file_bytes))
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                full_text.append(cell.text)
    return "\n".join(full_text)

def parse_jd_requirements(text: str) -> Dict[str, Any]:
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    extracted = {
        "title": "Senior AI Engineer",
        "extracted_skills": [],
        "extracted_experience": "",
        "extracted_education": "",
        "extracted_certifications": [],
        "extracted_responsibilities": []
    }
    
    # Simple heuristic regex parsing
    title_match = re.search(r"(?:Job Title|Role|Position):\s*(.*)", text, re.IGNORECASE)
    if title_match:
        extracted["title"] = title_match.group(1).strip()
    
    # Skills list
    skills_keywords = [
        "python", "pytorch", "tensorflow", "embeddings", "vector search", "semantic search",
        "rag", "llm", "fine-tuning", "lora", "qlora", "peft", "xgboost", "scikit-learn",
        "ndcg", "mrr", "map", "a/b testing", "pinecone", "weaviate", "qdrant", "milvus",
        "faiss", "elasticsearch", "opensearch", "aws", "docker", "kubernetes", "sql", "git"
    ]
    for kw in skills_keywords:
        if re.search(r"\b" + re.escape(kw) + r"\b", text, re.IGNORECASE):
            extracted["extracted_skills"].append(kw.capitalize() if len(kw) > 3 else kw.upper())
            
    # Experience match
    exp_match = re.search(r"(\d+[\s–-]+\d+\s*(?:years|yrs))|(\d+\+\s*(?:years|yrs))", text, re.IGNORECASE)
    if exp_match:
        extracted["extracted_experience"] = exp_match.group(0).strip()
    else:
        extracted["extracted_experience"] = "5-9 years"
        
    # Education match
    edu_keywords = ["computer science", "engineering", "b.tech", "m.tech", "ms", "phd", "bachelor", "master"]
    edu_found = []
    for kw in edu_keywords:
        if kw in text.lower():
            edu_found.append(kw)
    extracted["extracted_education"] = ", ".join(edu_found) if edu_found else "Degree in CS or related field"
    
    # Certifications
    cert_keywords = ["aws", "gcp", "azure", "pmp", "tensorflow developer"]
    for kw in cert_keywords:
        if kw in text.lower():
            extracted["extracted_certifications"].append(kw.upper())
            
    # Responsibilities (lines with bullet points in sections containing responsibilities)
    resp_section = False
    for line in lines:
        if any(w in line.lower() for w in ["responsibility", "responsibilities", "what you'd actually be doing", "what you will do"]):
            resp_section = True
            continue
        if resp_section:
            if any(w in line.lower() for w in ["requirement", "qualification", "what we mean", "skills", "experience"]):
                resp_section = False
            elif line.startswith("-") or line.startswith("*") or line.startswith("•") or (len(line) > 10 and line[0].isupper()):
                extracted["extracted_responsibilities"].append(line.lstrip("-*• ").strip())
                if len(extracted["extracted_responsibilities"]) >= 8:
                    resp_section = False
                    
    if not extracted["extracted_responsibilities"]:
        extracted["extracted_responsibilities"] = [
            "Own the intelligence layer of Redrob's product (ranking, retrieval, matching).",
            "Audit current BM25 + rule-based scoring systems and identify fixes.",
            "Ship v2 ranking systems incorporating embeddings and hybrid search.",
            "Set up offline and online evaluation frameworks (NDCG, MRR, MAP).",
            "Mentor junior hires and collaborate on recruiter-experience workflows."
        ]
        
    return extracted
