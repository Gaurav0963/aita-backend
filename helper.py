import httpx
from bs4 import BeautifulSoup

FIREBASE_BASE_URL = "https://iiitbh-ai-lab-portal.web.app"

async def extract_questions_from_html(lab_id: str) -> dict:
    url = f"{FIREBASE_BASE_URL}/{lab_id}.html"

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(url)

    if response.status_code != 200:
        return {}

    soup = BeautifulSoup(response.text, "html.parser")
    questions = {}

    for content_div in soup.find_all("div", class_="lab-question-data"):
        parent = content_div.find_parent(attrs={"data-q": True})
        if not parent:
            continue

        q_id = parent.get("data-q")
        title_tag = parent.find("h2")
        title = title_tag.get_text(strip=True) if title_tag else "Untitled"

        text = content_div.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned_text = "\n".join(lines)

        questions[q_id] = {
            "title": title,
            "content": cleaned_text
        }

    return questions