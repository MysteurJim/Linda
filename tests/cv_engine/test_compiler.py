from unittest.mock import MagicMock, patch

import pytest

from linda.cv_engine.compiler import compile_pdf, make_output_dir, write_ats_report, write_typ


def test_make_output_dir_creates_path(tmp_path):
    result = make_output_dir(tmp_path, "Backend Java", "ExampleCorp", "2026-06-09")
    assert result.exists()
    assert result.name == "2026-06-09-Backend-Java-ExampleCorp"


def test_make_output_dir_slugifies(tmp_path):
    result = make_output_dir(tmp_path, "  Backend Java  ", "  ExampleCorp  ", "2026-06-09")
    assert " " not in result.name


def test_write_typ_creates_cv_typ(tmp_path):
    path = write_typ(tmp_path, "#let x = 1")
    assert path.name == "cv.typ"
    assert path.read_text(encoding="utf-8") == "#let x = 1"


def test_write_ats_report_creates_file(tmp_path):
    path = write_ats_report(tmp_path, "# ATS Report\nScore: 80/100")
    assert path.name == "ats_report.md"
    assert "80/100" in path.read_text(encoding="utf-8")


def test_compile_pdf_calls_typst(tmp_path):
    typ_path = tmp_path / "cv.typ"
    typ_path.write_text("#let x = 1", encoding="utf-8")
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        compile_pdf(typ_path)
    args = mock_run.call_args[0][0]
    assert args[0] == "typst"
    assert args[1] == "compile"
    assert str(typ_path) in args


def test_compile_pdf_raises_on_nonzero(tmp_path):
    typ_path = tmp_path / "cv.typ"
    typ_path.write_text("#invalid", encoding="utf-8")
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1, stderr="error: unknown node")
        with pytest.raises(RuntimeError, match="typst compile failed"):
            compile_pdf(typ_path)


def test_compile_pdf_raises_clear_error_when_typst_missing(tmp_path):
    typ_path = tmp_path / "cv.typ"
    typ_path.write_text("#let x = 1", encoding="utf-8")
    with patch("subprocess.run", side_effect=FileNotFoundError):
        with pytest.raises(RuntimeError, match="typst binary not found"):
            compile_pdf(typ_path)
