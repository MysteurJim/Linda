import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def _read_pdf(path: Path) -> str:
    from pypdf import PdfReader
    return "\n".join(p.extract_text() or "" for p in PdfReader(str(path)).pages)


def ingest_offer(source: str) -> str:
    """Read offer text from file path, URL, or '-' for stdin."""
    if source == "-":
        return sys.stdin.read()
    if source.startswith("http://") or source.startswith("https://"):
        resp = requests.get(source, timeout=10)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser").get_text(separator=" ", strip=True)
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"Offer file not found: {source}")
    if path.suffix.lower() == ".pdf":
        return _read_pdf(path)
    return path.read_text(encoding="utf-8")
