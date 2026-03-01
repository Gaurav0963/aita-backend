# ==========================================================
# Utility & Extraction Functions
# ==========================================================

import hashlib
from bs4 import BeautifulSoup
from paths import LABS_DIR
from logger import setup_logger

logger = setup_logger("helper")

def get_hash(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()

def extract_questions_from_html(lab_id: str) -> dict:

    file_path = LABS_DIR / f"{lab_id}.html"

    if not file_path.exists():
        logger.warning(f"Lab file not found: {file_path}")
        return {}

    html = file_path.read_text(encoding="utf-8")

    soup = BeautifulSoup(html, "html.parser")
    questions = {}

    for content_div in soup.find_all("div", class_="lab-question-data"):

        parent = content_div.find_parent(attrs={"data-q": True})
        if not parent:
            continue

        q_id = parent.get("data-q")
        title_tag = parent.find("h2")
        title = title_tag.get_text(strip=True) if title_tag else "Untitled Question"

        text = content_div.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned_text = "\n".join(lines)

        questions[q_id] = {
            "title": title,
            "content": cleaned_text
        }

    logger.info(f"Extracted {len(questions)} questions from {lab_id}")
    return questions