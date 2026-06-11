import re


def extract_relevant_keywords(offer_text: str, known_tags: set) -> set:
    """Return words from offer_text that appear in known_tags.

    Handles both simple tokens (java, kubernetes) and compound tags (spring-boot)
    by also checking if known compound tags appear as space-separated sequences
    in the offer text.
    """
    text_lower = offer_text.lower()
    # Simple single-token matches
    words = set(re.findall(r'[a-zA-Z][a-zA-Z0-9\-\.]*', text_lower))
    matched = words & known_tags

    # Compound tag matching: "spring-boot" matches "spring boot" in offer text
    for tag in known_tags:
        if tag not in matched and '-' in tag:
            # Replace hyphens with spaces to find "spring boot" from "spring-boot"
            tag_as_words = tag.replace('-', ' ')
            if tag_as_words in text_lower:
                matched.add(tag)

    return matched


def score_block(tags: list, offer_keywords: set) -> dict:
    """Score 0–10: how many of offer_keywords the block covers."""
    if not offer_keywords:
        return {"score": 0.0, "matched": []}
    matched = [t.lower() for t in tags if t.lower() in offer_keywords]
    score = round(len(matched) / len(offer_keywords) * 10, 1)
    return {"score": min(10.0, score), "matched": matched}


def _all_tags(data: dict) -> set:
    tags = set()
    blocks = list(data.get("experiences", {}).values()) + list(data.get("projects", {}).values())
    for item in blocks:
        tags.update(t.lower() for t in item.get("tags", []))
    return tags


def score_plan(plan: dict, data: dict, offer_text: str) -> dict:
    known_tags = _all_tags(data)
    offer_keywords = extract_relevant_keywords(offer_text, known_tags)

    blocks = []
    all_matched = set()

    for side in ("left", "right"):
        for section in plan["sections"].get(side, []):
            stype = section["type"]
            if stype not in ("experiences", "projects"):
                continue
            source = data.get(stype, {})
            for item_ref in section.get("items", []):
                item = source.get(item_ref["id"])
                if not item:
                    continue
                result = score_block(item.get("tags", []), offer_keywords)
                all_matched.update(result["matched"])
                blocks.append({"id": item_ref["id"], "type": stype.rstrip("s"), **result})

    total = len(offer_keywords)
    global_score = round(len(all_matched) / total * 100) if total else 0
    uncovered = sorted(offer_keywords - all_matched)

    return {
        "offer_context": plan.get("offer_context", ""),
        "global_score": global_score,
        "blocks": blocks,
        "uncovered_keywords": uncovered[:15],
    }


def generate_ats_report(report_data: dict) -> str:
    lines = [
        f"# ATS Report - {report_data['offer_context']}",
        "",
        f"Global score: {report_data['global_score']}/100",
        "",
        "## Included blocks",
    ]
    for block in report_data["blocks"]:
        matched_str = ", ".join(block["matched"]) or "-"
        lines.append(f"- {block['id']:<22}: {block['score']}/10  [{matched_str}]")

    if report_data["uncovered_keywords"]:
        lines += [
            "",
            "## Uncovered offer keywords",
            ", ".join(report_data["uncovered_keywords"]),
        ]

    return "\n".join(lines)
