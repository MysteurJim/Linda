# Data Directory Format

LINDA assembles a CV from small, reusable YAML "blocks" stored in a data
directory. Each block describes one experience, project, skill group, etc. A
[plan](./plan-format.md) then selects and orders these blocks into a finished
CV.

By default the CLI reads blocks from `cv/data/` (see `DATA_DIR` in
`linda/cli.py`). The repository ships a complete fictional dataset under
`examples/data/` that you can copy as a starting point.

## Directory layout

```
data/
├── identity.yaml          # who you are (single file, required)
├── experiences/           # one .yaml file per job
│   ├── acme-corp.yaml
│   └── globex.yaml
├── projects/              # one .yaml file per side/personal project
│   ├── taskflow.yaml
│   └── weatherly.yaml
├── skills.yaml            # technical skills, grouped by category (single file)
└── education.yaml         # degrees & certifications (single file)
```

How the loader (`linda/cv_engine/loader.py`) reads each path:

- `identity.yaml`, `skills.yaml`, `education.yaml` are loaded as single files.
- `experiences/` and `projects/` are scanned with `glob("*.yaml")`, sorted by
  filename, and **keyed by the `id` field inside each file** — not by the
  filename. The filename is cosmetic; the `id` is what the plan references. Keep
  them aligned to stay sane, but only `id` is load-bearing.

## Bilingual text objects

Any field shown as `{fr:, en:}` below is a **bilingual text object**: a mapping
with an `fr` and an `en` key. The renderer picks the branch matching the plan's
`lang` (defaulting to `fr`). If you only ever generate in one language you can
technically omit the other branch, but providing both is recommended.

```yaml
title:
  fr: "Développeur Backend"
  en: "Backend Developer"
```

Plain string fields (e.g. `org`, `dates`, `location` on an experience) are
**not** bilingual — they render verbatim in both languages.

---

## `identity.yaml` (required)

Describes the person. All fields are required; the renderer
(`build_context`) accesses them directly and will raise a `KeyError` if any are
missing.

| Field | Type | Notes |
|-------|------|-------|
| `name_first` | string | First name. |
| `name_last` | string | Last name. |
| `title` | `{fr:, en:}` | Headline / role under your name. |
| `summary` | `{fr:, en:}` | Short intro paragraph. |
| `contact.github` | string | GitHub handle (e.g. `"@alexmartin"`). Escaped for Typst. |
| `contact.linkedin` | string | LinkedIn handle. Escaped for Typst. |
| `contact.email` | string | Email address. Escaped for Typst (the `@` is escaped). |
| `contact.location` | `{fr:, en:}` | City / region. |

> The renderer runs `github`, `linkedin`, and `email` through a `typst_escape`
> filter that backslash-escapes `@`, so handles like `@alexmartin` render
> correctly in Typst.

### Minimal example

```yaml
name_first: Alex
name_last: MARTIN
title:
  fr: "Développeur Fullstack"
  en: "Fullstack Developer"
summary:
  fr: "Développeur fullstack passionné par les produits simples et bien testés."
  en: "Fullstack developer who loves simple, well-tested products."
contact:
  github: "@alexmartin"
  linkedin: "@alex-martin-example"
  email: "alex.martin@example.com"
  location:
    fr: "Lyon, France"
    en: "Lyon, France"
```

---

## `experiences/*.yaml` (one file per job)

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `id` | **yes** | string | Unique key; referenced by the plan. This is the key the loader uses, not the filename. |
| `title` | recommended | `{fr:, en:}` | Job title. Falls back to the `id` if missing. |
| `org` | optional | string | Company / organization. Defaults to `""`. |
| `dates` | optional | string | Free-form date range, e.g. `"03/2024 – présent"`. Defaults to `""`. |
| `location` | optional | string | City. Defaults to `""`. |
| `tags` | optional | list of strings | Block-level ATS keywords (see [Tags & ATS scoring](#tags--ats-scoring)). |
| `bullets` | optional | list of bullet objects | Achievements (see [Bullets](#bullets)). Defaults to `[]`. |

Only `id` is strictly required by the loader. Everything else has a safe
default in the renderer, but a useful experience block has at least `title` and
`bullets`.

### Minimal example

```yaml
id: acme-corp
title:
  fr: "Développeur Backend – Plateforme E-commerce"
  en: "Backend Developer – E-commerce Platform"
org: ACME Corp
dates: "03/2024 – présent"
location: Lyon
tags: [java, spring-boot, postgresql, kubernetes, backend, api]
bullets:
  - text:
      fr: "Conception et développement d'APIs REST en Java Spring Boot"
      en: "Designed and built REST APIs in Java Spring Boot"
    tags: [java, spring-boot, api, backend]
    weight: 1.0
```

---

## `projects/*.yaml` (one file per project)

Projects use the **same block shape as experiences** and are resolved by the
same renderer branch. The only practical difference is how the template lays
them out (projects render without an org/dates header block, just a bold title
and bullets in the FR template).

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `id` | **yes** | string | Unique key; referenced by the plan. |
| `title` | recommended | `{fr:, en:}` | Project name. Falls back to the `id`. |
| `org` | optional | string | Rarely used for projects. Defaults to `""`. |
| `dates` | optional | string | Defaults to `""`. |
| `location` | optional | string | Defaults to `""`. |
| `tags` | optional | list of strings | Block-level ATS keywords. |
| `bullets` | optional | list of bullet objects | See [Bullets](#bullets). |

### Minimal example

```yaml
id: taskflow
title:
  fr: "TaskFlow – Gestionnaire de tâches collaboratif"
  en: "TaskFlow – Collaborative Task Manager"
tags: [python, fastapi, react, postgresql, fullstack]
bullets:
  - text:
      fr: "Application web de gestion de tâches en équipe (FastAPI + React)"
      en: "Team task management web app (FastAPI + React)"
    tags: [python, fastapi, react, fullstack]
    weight: 1.0
```

---

## Bullets

Both experiences and projects carry a `bullets` list. Each bullet is an object:

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `text` | **yes** | `{fr:, en:}` | The bullet sentence. The renderer reads `text[lang]`. |
| `tags` | optional | list of strings | Per-bullet keywords. **Documentation / authoring aid only** — see note below. |
| `weight` | optional | number | Relative importance (e.g. `1.0`, `0.8`). Authoring aid only; not consumed by the renderer or scorer. |

The renderer selects bullets per the plan (`bullets: all` or a list of integer
indexes into this list) and emits only `text[lang]`.

> **Important:** the ATS scorer reads **block-level `tags` only** (on the
> experience/project), *not* per-bullet `tags`. Per-bullet `tags` and `weight`
> are useful metadata for you (and for an AI agent) when deciding which bullets
> to include, but LINDA's code does not currently read them at scoring or render
> time. Make sure any keyword you want scored also appears in the block-level
> `tags`.

---

## `skills.yaml` (required)

A list of skill categories under a top-level `categories` key.

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `categories` | **yes** | list | Each entry is a category object. |
| `categories[].id` | **yes** | string | Internal id for the category. |
| `categories[].display` | **yes** | `{fr:, en:}` | Section label shown in the CV. |
| `categories[].items` | **yes** | list of strings | Human-readable skill names, joined with `, ` in the CV. |
| `categories[].tags` | optional | list of strings | Present in the examples for symmetry, but **not read** by the scorer (which only looks at experiences/projects). Safe to keep for future use. |

### Minimal example

```yaml
categories:
  - id: languages
    display:
      fr: "Langages"
      en: "Languages"
    items: [Java, Python, TypeScript, Dart]
    tags: [java, python, typescript, dart]
  - id: frameworks
    display:
      fr: "Frameworks / Librairies"
      en: "Frameworks / Libraries"
    items: [Spring Boot, React, FastAPI]
    tags: [spring-boot, react, fastapi]
```

The plan includes skills with a bare `- type: skills` section (no `items`); the
renderer always emits **all** categories from `skills.yaml` regardless of the
plan.

---

## `education.yaml` (required)

A list of formations (degrees, certifications) under a top-level `formations`
key.

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `formations` | **yes** | list | Each entry is a formation object. |
| `formations[].id` | **yes** | string | Unique key; referenced by the plan's education section. Used to build a lookup map. |
| `formations[].title` | recommended | `{fr:, en:}` | Degree / certification name. Falls back to the `id`. |
| `formations[].org` | optional | string | Institution. Defaults to `""`. |
| `formations[].dates` | optional | string | Defaults to `""`. |
| `formations[].location` | optional | string | Defaults to `""`. |
| `formations[].description` | optional | `{fr:, en:}` | One-line description. Defaults to `""`. |

### Minimal example

```yaml
formations:
  - id: state-university
    title:
      fr: "Master en Informatique"
      en: "Master's Degree in Computer Science"
    org: "Université Exemple"
    dates: "09/2019 – 06/2024"
    location: Lyon
    description:
      fr: "Spécialisation génie logiciel et systèmes distribués"
      en: "Software engineering and distributed systems specialization"
```

---

## Tags & ATS scoring

> **Experimental:** ATS scoring is an experimental feature. The current
> implementation is a simple tag/keyword matcher that still needs real-world
> testing and improvement — treat scores as a rough signal, and expect the
> mechanics described below to evolve.

Tags are the heart of LINDA's ATS keyword matching
(`linda/cv_engine/scorer.py`). When you run `linda score`:

1. LINDA collects all **block-level `tags`** from every experience and project
   (`_all_tags`), lowercased, into the set of "known tags".
2. It extracts the offer's relevant keywords: words in the offer text that
   match a known tag. It also matches **compound tags** — e.g. the tag
   `spring-boot` matches the phrase `spring boot` in the offer.
3. Each included block scores `matched / total_offer_keywords * 10` (capped at
   10), and a global score is `unique_matched / total * 100`.

Practical implications for how you write tags:

- Use lowercase, hyphenated compound tags (`spring-boot`, `github-actions`) so
  both `spring-boot` and the spaced form `spring boot` match.
- A keyword is only counted if it is present in some block's tags **and** in the
  offer text. Tags that never appear in any offer are harmless; offer keywords
  with no matching tag show up under "uncovered keywords" in the report.
- Only experience/project block `tags` are scored. Per-bullet `tags`, skill
  `tags`, and `weight` are not read by the scorer.

See [plan-format.md](./plan-format.md) for the full agent-driven workflow that
ties `linda list`, `linda score`, and `linda generate` together.
