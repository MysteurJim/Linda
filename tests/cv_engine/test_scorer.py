import pytest

from linda.cv_engine.scorer import (
    extract_relevant_keywords,
    generate_ats_report,
    score_block,
    score_plan,
)


def test_extract_keywords_matches_known_tags():
    offer = "We need a Java developer with Spring Boot and Kubernetes experience."
    known = {"java", "spring-boot", "kubernetes", "docker", "python"}
    kw = extract_relevant_keywords(offer, known)
    assert "java" in kw
    assert "spring-boot" in kw
    assert "kubernetes" in kw
    assert "docker" not in kw


def test_score_block_partial_match():
    result = score_block(["java", "spring-boot"], {"java", "spring-boot", "kubernetes"})
    assert result["score"] == pytest.approx(6.7, abs=0.2)
    assert set(result["matched"]) == {"java", "spring-boot"}


def test_score_block_no_match():
    result = score_block(["flutter", "dart"], {"java", "spring-boot"})
    assert result["score"] == 0.0
    assert result["matched"] == []


def test_score_block_empty_keywords():
    result = score_block(["java"], set())
    assert result["score"] == 0.0


def test_score_plan_returns_global_score():
    plan = {
        "offer_context": "Test",
        "sections": {
            "left": [{"type": "experiences", "items": [{"id": "acme-corp", "bullets": "all"}]}],
            "right": [],
        },
    }
    data = {
        "experiences": {
            "acme-corp": {
                "tags": ["java", "spring-boot", "sso"],
                "bullets": [{"tags": ["java"]}, {"tags": ["sso"]}],
            }
        },
        "projects": {},
    }
    report = score_plan(plan, data, "We need a Java Spring Boot developer with SSO.")
    assert report["global_score"] > 0
    assert "blocks" in report
    assert "uncovered_keywords" in report


def test_score_block_case_insensitive_tags():
    result = score_block(["Java", "Spring-Boot"], {"java", "spring-boot"})
    assert result["score"] > 0
    assert "java" in result["matched"] or "Java" not in result["matched"]
    # matched should be lowercased
    assert all(t == t.lower() for t in result["matched"])


def test_generate_ats_report_format():
    data = {
        "offer_context": "Backend Java @ ExampleCorp",
        "global_score": 78,
        "blocks": [
            {
                "id": "acme-corp",
                "type": "experience",
                "score": 9.0,
                "matched": ["java", "spring-boot"],
            },
        ],
        "uncovered_keywords": ["terraform", "grafana"],
    }
    report = generate_ats_report(data)
    assert "78/100" in report
    assert "acme-corp" in report
    assert "terraform" in report
