from pathlib import Path

from linda.cv_engine.loader import (
    load_all,
    load_education,
    load_experiences,
    load_identity,
    load_plan,
    load_projects,
    load_skills,
)

DATA_DIR = Path("examples/data")
PLAN_PATH = Path("examples/plan_fr.yaml")

def test_load_identity_returns_name():
    identity = load_identity(DATA_DIR)
    assert identity["name_first"] == "Alex"
    assert identity["name_last"] == "MARTIN"
    assert "fr" in identity["title"]
    assert "en" in identity["title"]

def test_load_experiences_keyed_by_id():
    exps = load_experiences(DATA_DIR)
    assert "acme-corp" in exps
    assert "globex" in exps

def test_experience_has_required_fields():
    exp = load_experiences(DATA_DIR)["acme-corp"]
    assert exp["id"] == "acme-corp"
    assert "fr" in exp["title"]
    assert isinstance(exp["tags"], list)
    assert isinstance(exp["bullets"], list)
    assert len(exp["bullets"]) > 0

def test_bullet_has_bilingual_text_and_tags():
    bullet = load_experiences(DATA_DIR)["acme-corp"]["bullets"][0]
    assert "fr" in bullet["text"]
    assert "en" in bullet["text"]
    assert isinstance(bullet["tags"], list)
    assert "weight" in bullet

def test_load_projects_keyed_by_id():
    projects = load_projects(DATA_DIR)
    assert "taskflow" in projects
    assert "weatherly" in projects

def test_load_skills_has_categories():
    skills = load_skills(DATA_DIR)
    ids = [c["id"] for c in skills["categories"]]
    assert "languages" in ids
    assert "frameworks" in ids

def test_load_education_has_formations():
    edu = load_education(DATA_DIR)
    ids = [f["id"] for f in edu["formations"]]
    assert "state-university" in ids

def test_load_all_returns_all_keys():
    data = load_all(DATA_DIR)
    assert set(data.keys()) == {"identity", "experiences", "projects", "skills", "education"}

def test_load_plan_lang_and_context():
    plan = load_plan(PLAN_PATH)
    assert plan["lang"] == "fr"
    assert plan["offer_context"] == "Développeur Backend @ ExampleCorp"

def test_load_plan_has_left_and_right():
    plan = load_plan(PLAN_PATH)
    assert "left" in plan["sections"]
    assert "right" in plan["sections"]

def test_load_plan_bullets_all_preserved():
    plan = load_plan(PLAN_PATH)
    exps = next(s for s in plan["sections"]["left"] if s["type"] == "experiences")
    acme = next(i for i in exps["items"] if i["id"] == "acme-corp")
    assert acme["bullets"] == "all"

def test_load_plan_bullets_list_preserved():
    plan = load_plan(PLAN_PATH)
    exps = next(s for s in plan["sections"]["left"] if s["type"] == "experiences")
    globex = next(i for i in exps["items"] if i["id"] == "globex")
    assert globex["bullets"] == [0]
