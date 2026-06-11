from unittest.mock import MagicMock, patch

import pytest

from linda.cv_engine.ingestor import ingest_offer


def test_ingest_text_file(tmp_path):
    f = tmp_path / "offer.txt"
    f.write_text("We need a Java developer.", encoding="utf-8")
    assert "Java" in ingest_offer(str(f))


def test_ingest_stdin():
    with patch("sys.stdin") as mock_stdin:
        mock_stdin.read.return_value = "Looking for Python developer"
        assert "Python" in ingest_offer("-")


def test_ingest_url_strips_html():
    mock_resp = MagicMock()
    mock_resp.text = "<html><body><h1>Job</h1><p>Kubernetes expert needed</p></body></html>"
    mock_resp.raise_for_status = MagicMock()
    with patch("requests.get", return_value=mock_resp):
        result = ingest_offer("https://example.com/job")
    assert "Kubernetes" in result
    assert "<h1>" not in result


def test_ingest_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        ingest_offer("/nonexistent/offer.txt")
