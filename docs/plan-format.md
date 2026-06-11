# Plan Format (`plan.yaml`)

A **plan** is a small YAML file that turns your reusable
[data blocks](./data-format.md) into one tailored CV. It picks which blocks
appear, in which column, in what order, and which bullets to keep. You typically
keep one plan per job application (e.g. `plan_backend_examplecorp.yaml`).

The CLI takes the plan path explicitly:

```bash
linda generate --plan examples/plan_fr.yaml
linda score    --plan examples/plan_fr.yaml --offer offer.txt
```

## Top-level fields

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `lang` | optional | `fr` \| `en` | Language to render. Defaults to `fr`. Selects the `{fr:, en:}` branch of every text object and the `templates/base_<lang>.typ.j2` template. |
| `offer_context` | optional | string | `"Job Title @ Company"`. Used only to name the output directory and to title the ATS report. Defaults to `"CV"`. |
| `sections` | **yes** | object | Has `left` and `right` lists (the two CV columns). |

### `offer_context` parsing

`linda generate` splits `offer_context` on the **first `@`**:

- text before `@` → job title
- text after `@` → company (defaults to `"Unknown"` if there is no `@`)

Both halves are slugified (non-word chars stripped, spaces → hyphens) and the
output directory becomes:

```
output/<date>-<job-title-slug>-<company-slug>/
```

e.g. `offer_context: "Backend Developer @ ExampleCorp"` with date `2026-06-11`
produces `output/2026-06-11-Backend-Developer-ExampleCorp/`, containing
`cv.typ`, `cv.pdf`, and (if `--offer` was passed) `ats_report.md`.

## Sections and columns

`sections` has two keys, `left` and `right`, each a list of section objects.
The two map to the CV's two-column layout (the FR template renders left at 62%
width, right at 38%). Either list may be empty or omitted.

Each section object has a `type`:

| `type` | `items`? | What it renders |
|--------|----------|-----------------|
| `experiences` | yes | Selected experience blocks, in list order. |
| `projects` | yes | Selected project blocks, in list order. |
| `education` | yes | Selected formations from `education.yaml`, in list order. |
| `skills` | no | **All** categories from `skills.yaml`. `items` is ignored. |

Any other `type` resolves to an empty section (no error).

### `items`

For `experiences`, `projects`, and `education`, `items` is an ordered list of
references:

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `id` | **yes** | string | Must match a block `id` (experience/project) or formation `id`. |
| `bullets` | optional | `all` \| list of ints | Which bullets to include. `all` (default) keeps every bullet; a list like `[0, 2]` keeps those 0-based indexes. Ignored for `education` (formations have no bullets). |

`bullets` example:

```yaml
- id: globex
  bullets: [0]      # keep only the first bullet of the globex block
- id: acme-corp
  bullets: all      # keep every bullet (this is also the default)
```

Out-of-range indexes are silently dropped (`_resolve_bullets` filters
`i < len(all_bullets)`), so `bullets: [0, 5]` on a 2-bullet block yields just
bullet 0.

### How ids are resolved (and what happens to unknown ids)

The renderer (`_resolve_section` in `linda/cv_engine/renderer.py`) builds a
lookup of available blocks and resolves each `item.id` against it:

- **experiences / projects:** `source.get(ref["id"], {})`
- **education:** a map `{formation.id: formation}` built from
  `education.yaml`, then `.get(ref["id"], {})`

An **unknown id does not raise and is not skipped from the layout** — it
resolves to an empty block. Because of the renderer's fallbacks, that empty
block renders with the **id string itself as the title** and no org/dates/bullets
(`title` falls back to `ref["id"]`; `org`, `dates`, `location`, `description`
fall back to `""`; bullets to `[]`). So a typo in an `id` shows up as a stray
entry titled e.g. `acme-crop` rather than an error — check the rendered CV.

The **scorer** behaves differently: in `score_plan`, an item whose `id` is not
found is skipped entirely (`if not item: continue`), so unknown ids simply don't
contribute to the ATS score.

## Complete example

```yaml
lang: fr
offer_context: "Développeur Backend @ ExampleCorp"
sections:
  left:
    - type: experiences
      items:
        - id: acme-corp
          bullets: all
        - id: globex
          bullets: [0]
    - type: projects
      items:
        - id: taskflow
          bullets: all
        - id: weatherly
          bullets: [0]
  right:
    - type: skills            # no items: renders all skill categories
    - type: education
      items:
        - id: state-university
        - id: cloud-certification
```

---

## Writing plans as an AI agent

This is LINDA's main differentiator: a plan is small, declarative, and built
from a known inventory of blocks, so an AI agent can author a strong,
offer-tailored plan end to end. The recipe:

### 1. Discover the available blocks and their tags

```bash
linda list
```

This prints every experience and project with its `id` and block-level `tags`,
plus formation ids. Example output shape:

```
-- Experiences ------------------------------------------
  acme-corp                    [java, spring-boot, postgresql, kubernetes, backend, api]
    Développeur Backend – Plateforme E-commerce
  globex                       [react, typescript, frontend, ui]
    Développeur Frontend Stagiaire – Outils Internes

-- Projets ----------------------------------------------
  taskflow                     [python, fastapi, react, postgresql, fullstack]
    TaskFlow – Gestionnaire de tâches collaboratif
  ...

-- Formations -------------------------------------------
  state-university
  cloud-certification
```

Use this as your inventory: the `id`s are exactly what you put under `items`,
and the `tags` are what the scorer matches against the offer.

### 2. Ingest and read the offer

Get the offer text (the scorer will tokenize it for you, but you should read it
to judge relevance and ordering). LINDA accepts a file, a URL, or stdin:

```bash
# from a file (.txt, .md, or .pdf)
linda score --plan plan.yaml --offer ./offer.pdf

# from a URL (HTML is stripped to text)
linda score --plan plan.yaml --offer https://example.com/job/123

# from stdin
pbpaste | linda score --plan plan.yaml --offer -
```

### 3. Pick blocks whose tags match, and order by relevance

- Select the experiences/projects whose block `tags` overlap most with the
  offer's keywords. Put the strongest matches **first** in each `items` list —
  order is preserved in the rendered CV.
- Trim weak bullets with `bullets: [..]` to keep the CV focused; per-bullet
  `tags`/`weight` in the data are useful hints for *which* bullets carry the
  offer's keywords, even though the scorer itself only reads block-level tags.
- Set `lang` to match the offer's language, and write a clean
  `offer_context: "Exact Job Title @ Company"`.

A minimal authored plan:

```yaml
lang: en
offer_context: "Backend Developer @ ExampleCorp"
sections:
  left:
    - type: experiences
      items:
        - id: acme-corp        # strongest match: java, spring-boot, kubernetes
          bullets: all
        - id: globex
          bullets: [0]
    - type: projects
      items:
        - id: taskflow
          bullets: all
  right:
    - type: skills
    - type: education
      items:
        - id: state-university
        - id: cloud-certification
```

### 4. Validate coverage with `linda score`

> **Experimental:** the ATS scorer is an experimental feature still under
> testing and improvement. Use the score as a hint to spot missing keywords,
> not as a target to maximize.

```bash
linda score --plan plan.yaml --offer ./offer.txt
```

Read the report:

- **Global score (/100):** share of the offer's matched keywords covered by the
  blocks you included.
- **Per-block lines:** which keywords each block matched.
- **"Uncovered offer keywords":** offer terms no included block covers.

If the score is low or important keywords are uncovered, iterate: swap in a
better-matching block, reorder, or restore bullets that carry the missing
keywords — then re-run `linda score`. (If a keyword has *no* matching tag in any
block, no plan change can cover it; that's a signal to add a tag to the relevant
data block, which lives outside the plan.)

### 5. Generate the final CV

```bash
# render + compile PDF
linda generate --plan plan.yaml

# also emit ats_report.md alongside the PDF
linda generate --plan plan.yaml --offer ./offer.txt

# override the date used in the output dir name
linda generate --plan plan.yaml --date 2026-06-11
```

Output lands in `output/<date>-<job-title>-<company>/` as `cv.typ`, `cv.pdf`,
and optionally `ats_report.md`. PDF compilation shells out to the `typst`
binary, so it must be installed for `generate` (it is **not** needed for `list`
or `score`).
