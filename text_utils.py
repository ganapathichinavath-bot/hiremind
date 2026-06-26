"""Text extraction and matching helpers."""

from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from config import CV_ONLY_KEYWORDS, ML_TITLE_KEYWORDS, NON_ML_TITLE_KEYWORDS, PRODUCTION_KEYWORDS


def read_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml")
    root = ET.fromstring(xml)
    parts: list[str] = []
    for node in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"):
        if node.text:
            parts.append(node.text)
        if node.tail:
            parts.append(node.tail)
    return "".join(parts)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def build_candidate_text(candidate: dict) -> str:
    profile = candidate["profile"]
    chunks = [
        profile.get("headline", ""),
        profile.get("summary", ""),
        profile.get("current_title", ""),
        profile.get("current_company", ""),
        profile.get("current_industry", ""),
    ]
    for role in candidate.get("career_history", []):
        chunks.extend(
            [
                role.get("title", ""),
                role.get("company", ""),
                role.get("industry", ""),
                role.get("description", ""),
            ]
        )
    for edu in candidate.get("education", []):
        chunks.extend([edu.get("degree", ""), edu.get("field_of_study", ""), edu.get("institution", "")])
    for skill in candidate.get("skills", []):
        chunks.append(
            f"{skill.get('name', '')} {skill.get('proficiency', '')} {skill.get('duration_months', 0)} months"
        )
    for cert in candidate.get("certifications", []):
        chunks.append(cert.get("name", ""))
    return normalize(" ".join(chunks))


def skill_map(candidate: dict) -> dict[str, dict]:
    return {skill["name"].lower(): skill for skill in candidate.get("skills", [])}


def has_keyword(text: str, keyword: str) -> bool:
    keyword = keyword.lower()
    if len(keyword) <= 3:
        return re.search(rf"\b{re.escape(keyword)}\b", text) is not None
    if keyword.endswith("@"):
        return keyword in text
    stem = keyword[: max(4, len(keyword) - 2)] if len(keyword) > 5 else keyword
    return stem in text


def keyword_hits(text: str, keywords: tuple[str, ...]) -> list[str]:
    return [keyword for keyword in keywords if has_keyword(text, keyword)]


def is_ml_title(title: str) -> bool:
    title = title.lower()
    return any(keyword in title for keyword in ML_TITLE_KEYWORDS)


def is_non_ml_title(title: str) -> bool:
    title = title.lower()
    return any(keyword in title for keyword in NON_ML_TITLE_KEYWORDS)


def production_evidence(text: str) -> list[str]:
    return keyword_hits(text, PRODUCTION_KEYWORDS)


def cv_only_profile(text: str) -> bool:
    hits = keyword_hits(text, CV_ONLY_KEYWORDS)
    retrieval_hits = keyword_hits(
        text,
        ("retrieval", "embedding", "nlp", "llm", "rag", "information retrieval", "search ranking"),
    )
    return len(hits) >= 2 and len(retrieval_hits) == 0
