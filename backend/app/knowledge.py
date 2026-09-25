from pathlib import Path
import re
from pypdf import PdfReader
from rapidfuzz import fuzz

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def load_documents():
    docs = []
    for p in DATA_DIR.glob("*.pdf"):
        try:
            reader = PdfReader(str(p))
            for page_no, page in enumerate(reader.pages, 1):
                text = page.extract_text() or ""
                if text.strip():
                    docs.append({"source": p.name, "page": page_no, "text": text})
        except Exception:
            pass
    team = DATA_DIR / "Team.txt"
    if team.exists():
        docs.append({"source": "Team.txt", "page": 1, "text": team.read_text(encoding="utf-8")})
    return docs

DOCS = load_documents()

def _terms(s):
    return set(re.findall(r"[a-zA-Z0-9]{3,}", s.lower()))

def search_knowledge(query: str, top_k: int = 5) -> str:
    q = _terms(query)
    scored = []
    for d in DOCS:
        t = _terms(d["text"])
        overlap = len(q & t)
        fuzzy = fuzz.partial_ratio(query.lower(), d["text"][:2500].lower()) / 100
        score = overlap + fuzzy
        if score > 0:
            scored.append((score, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored:
        return "No relevant knowledge-base content was found. Do not invent an answer."
    out=[]
    for score,d in scored[:top_k]:
        snippet = re.sub(r"\s+", " ", d["text"]).strip()
        if len(snippet)>1200: snippet=snippet[:1200]+"..."
        out.append(f"[{d['source']} p.{d['page']}] {snippet}")
    return "\n\n".join(out)
