from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def _resolve_bullets(item_ref: dict, source_item: dict, lang: str) -> list:
    spec = item_ref.get("bullets", "all")
    all_bullets = source_item.get("bullets", [])
    if spec == "all":
        selected = all_bullets
    else:
        selected = [all_bullets[i] for i in spec if i < len(all_bullets)]
    return [b["text"][lang] for b in selected]


def _resolve_section(section: dict, data: dict, lang: str) -> dict:
    stype = section["type"]

    if stype in ("experiences", "projects"):
        source = data[stype]
        items = []
        for ref in section.get("items", []):
            src = source.get(ref["id"], {})
            items.append({
                "id": ref["id"],
                "title": src.get("title", {}).get(lang, ref["id"]),
                "org": src.get("org", ""),
                "dates": src.get("dates", ""),
                "location": src.get("location", ""),
                "bullets": _resolve_bullets(ref, src, lang),
            })
        return {"type": stype, "items": items}

    if stype == "education":
        edu_by_id = {f["id"]: f for f in data["education"].get("formations", [])}
        items = []
        for ref in section.get("items", []):
            item = edu_by_id.get(ref["id"], {})
            items.append({
                "id": ref["id"],
                "title": item.get("title", {}).get(lang, ref["id"]),
                "org": item.get("org", ""),
                "dates": item.get("dates", ""),
                "location": item.get("location", ""),
                "description": item.get("description", {}).get(lang, ""),
            })
        return {"type": stype, "items": items}

    return {"type": stype, "items": []}


def build_context(plan: dict, data: dict) -> dict:
    lang = plan.get("lang", "fr")
    raw = data["identity"]
    identity = {
        "name_first": raw["name_first"],
        "name_last": raw["name_last"],
        "title": raw["title"][lang],
        "summary": raw["summary"][lang],
        "github": raw["contact"]["github"],
        "linkedin": raw["contact"]["linkedin"],
        "email": raw["contact"]["email"],
        "location": raw["contact"]["location"][lang],
    }
    sections = plan["sections"]
    return {
        "identity": identity,
        "left_sections": [_resolve_section(s, data, lang) for s in sections.get("left", [])],
        "right_sections": [_resolve_section(s, data, lang) for s in sections.get("right", [])],
        "skills_categories": [
            {"id": c["id"], "label": c["display"][lang], "items": c["items"]}
            for c in data["skills"].get("categories", [])
        ],
    }


def _typst_escape(text: str) -> str:
    return str(text).replace("@", r"\@")


def render_cv(plan: dict, data: dict, templates_dir: Path) -> str:
    lang = plan.get("lang", "fr")
    env = Environment(loader=FileSystemLoader(str(templates_dir)), keep_trailing_newline=True)
    env.filters["typst_escape"] = _typst_escape
    template = env.get_template(f"base_{lang}.typ.j2")
    return template.render(**build_context(plan, data))
