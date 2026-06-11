from pathlib import Path

from linda.cv_engine.loader import load_all, load_plan
from linda.cv_engine.renderer import build_context, render_cv

DATA_DIR = Path("examples/data")
TEMPLATES_DIR = Path("templates")
PLAN_PATH = Path("examples/plan_fr.yaml")


def test_build_context_identity_fr():
    data = load_all(DATA_DIR)
    plan = load_plan(PLAN_PATH)
    ctx = build_context(plan, data)
    assert ctx["identity"]["name_first"] == "Alex"
    assert ctx["identity"]["title"] == data["identity"]["title"]["fr"]
    assert ctx["identity"]["summary"] == data["identity"]["summary"]["fr"]


def test_build_context_resolves_experience_bullets_to_strings():
    data = load_all(DATA_DIR)
    plan = load_plan(PLAN_PATH)
    ctx = build_context(plan, data)
    exps = next(s for s in ctx["left_sections"] if s["type"] == "experiences")
    acme = next(i for i in exps["items"] if i["id"] == "acme-corp")
    assert isinstance(acme["bullets"], list)
    assert all(isinstance(b, str) for b in acme["bullets"])
    assert len(acme["bullets"]) == 2  # acme-corp has bullets: all (2 bullets)


def test_build_context_bullet_index_filter():
    data = load_all(DATA_DIR)
    plan = load_plan(PLAN_PATH)
    ctx = build_context(plan, data)
    exps = next(s for s in ctx["left_sections"] if s["type"] == "experiences")
    globex = next(i for i in exps["items"] if i["id"] == "globex")
    assert len(globex["bullets"]) == 1  # bullets: [0]


def test_build_context_skills_categories():
    data = load_all(DATA_DIR)
    plan = load_plan(PLAN_PATH)
    ctx = build_context(plan, data)
    assert len(ctx["skills_categories"]) > 0
    first = ctx["skills_categories"][0]
    assert "label" in first
    assert "items" in first


def test_render_cv_produces_valid_typ():
    data = load_all(DATA_DIR)
    plan = load_plan(PLAN_PATH)
    output = render_cv(plan, data, TEMPLATES_DIR)
    assert "#import" in output
    assert "Alex" in output
    assert "MARTIN" in output
    assert "ACME Corp" in output
    assert "Expériences professionnelles" in output
