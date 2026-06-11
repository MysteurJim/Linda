from pathlib import Path

import yaml


def _load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_identity(data_dir: Path) -> dict:
    return _load_yaml(data_dir / "identity.yaml")


def load_experiences(data_dir: Path) -> dict:
    result = {}
    for path in sorted((data_dir / "experiences").glob("*.yaml")):
        data = _load_yaml(path)
        result[data["id"]] = data
    return result


def load_projects(data_dir: Path) -> dict:
    result = {}
    for path in sorted((data_dir / "projects").glob("*.yaml")):
        data = _load_yaml(path)
        result[data["id"]] = data
    return result


def load_skills(data_dir: Path) -> dict:
    return _load_yaml(data_dir / "skills.yaml")


def load_education(data_dir: Path) -> dict:
    return _load_yaml(data_dir / "education.yaml")


def load_plan(path: Path) -> dict:
    return _load_yaml(path)


def load_all(data_dir: Path) -> dict:
    return {
        "identity": load_identity(data_dir),
        "experiences": load_experiences(data_dir),
        "projects": load_projects(data_dir),
        "skills": load_skills(data_dir),
        "education": load_education(data_dir),
    }
