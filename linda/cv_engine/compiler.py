import re
import subprocess
from pathlib import Path


def _slugify(text: str) -> str:
    text = text.strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'\s+', '-', text)


def make_output_dir(base: Path, job_title: str, company: str, date: str) -> Path:
    slug = f"{date}-{_slugify(job_title)}-{_slugify(company)}"
    path = base / slug
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_typ(output_dir: Path, content: str) -> Path:
    path = output_dir / "cv.typ"
    path.write_text(content, encoding="utf-8")
    return path


def write_ats_report(output_dir: Path, content: str) -> Path:
    path = output_dir / "ats_report.md"
    path.write_text(content, encoding="utf-8")
    return path


def compile_pdf(typ_path: Path) -> Path:
    pdf_path = typ_path.with_suffix(".pdf")
    try:
        result = subprocess.run(
            ["typst", "compile", str(typ_path), str(pdf_path)],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "typst binary not found. Install it from https://typst.app "
            "and make sure it is on your PATH."
        ) from None
    if result.returncode != 0:
        raise RuntimeError(f"typst compile failed:\n{result.stderr}")
    return pdf_path
