# LINDA

**The plan, not the copy.** Write your career data **once** as modular YAML
blocks; describe each job application as a small, versionable `plan.yaml` that
selects and orders those blocks; get a typeset PDF via
[Typst](https://typst.app) — with experimental ATS keyword scoring against a
target job offer and bilingual (`fr` / `en`) output.

Most CV generators make you duplicate and edit one monolithic file per
application. LINDA keeps a single source of truth and makes tailoring a
30-line, diffable plan.

LINDA makes **no LLM calls of its own**. It is a deterministic, scriptable engine
designed to be driven either by hand or — and this is the point — by an **AI agent**
(e.g. Claude Code) that reads a job offer, picks the most relevant blocks, writes
a tailored plan, and calls `linda generate`. Same plan, same PDF, every time:
your data never leaves your machine, and the agent can only *select* from blocks
you wrote — it has nothing to fabricate with.

## Features

- **Modular data blocks** — keep every experience, project, skill, and education
  entry in its own YAML file; reuse them across applications.
- **Plan-driven assembly** — a single `plan.yaml` selects which blocks (and which
  bullets) appear, in which column, for a given application.
- **ATS scoring** *(experimental)* — score a plan against a job offer (file, URL,
  or stdin) and get a keyword-coverage report before you send anything. The current
  scorer is a simple tag/keyword matcher; it still needs real-world testing and
  improvement, so treat scores as a rough signal, not a verdict.
- **Typst → PDF** — clean, typeset PDFs via Jinja2-generated Typst templates.
- **Bilingual** — every text field carries `fr` and `en`; pick the language per plan.
- **AI-agent friendly** — no hidden model calls, a stable CLI, and a plain-text
  data model an agent can read and write directly.

## Why LINDA?

- **The plan, not the copy.** Most workflows tailor a CV by duplicating one
  monolithic file (or a whole template) per application and editing it. LINDA
  separates the *data* (modular blocks, written once) from the *plan* (one
  small, diffable file per application). Your applications become a folder of
  30-line plans instead of a pile of diverging copies.
- **Pure data, not markup.** Content lives in plain YAML, not in LaTeX/Typst
  code — so a script or an AI agent can read, select, and reorder it safely
  without touching the typesetting.
- **Deterministic and local.** No embedded LLM calls: the same plan always
  produces the same PDF, nothing is sent to any API, and an agent driving LINDA
  can only *select* from blocks you wrote — fabricated experience is
  structurally impossible.
- **Typeset quality, instant builds.** Typst compiles in milliseconds with no
  TeX distribution to install, while keeping real typography in the output.

## Prerequisites

- **Python ≥ 3.12**
- **[Typst](https://typst.app) CLI** available on your `PATH` (used to compile PDFs)
- **[uv](https://docs.astral.sh/uv/)** for installation and environment management

## Install

As a tool (recommended for end users):

```bash
uv tool install linda-cv
```

The installed command is `linda` (the package is named `linda-cv` on PyPI).

For development (clones the repo and syncs the environment):

```bash
git clone https://github.com/MysteurJim/linda-cv.git
cd linda-cv
uv sync
```

## Quickstart

The repository ships with fictional example data under `examples/`.

List the available blocks:

```bash
linda list --data-dir examples/data
```

Score a plan against a job offer — a saved `offer.txt`, a URL, or `-` for stdin
(*experimental feature*):

```bash
linda score --plan examples/plan_fr.yaml --offer offer.txt --data-dir examples/data
```

Generate the CV (`.typ` + `.pdf`):

```bash
linda generate \
  --plan examples/plan_fr.yaml \
  --data-dir examples/data \
  --templates-dir templates \
  --output-dir output
```

### Configuration via environment variables

Each directory option has an environment-variable equivalent, so you can set them
once instead of passing them on every call:

| Option            | Environment variable   | Default      |
| ----------------- | ---------------------- | ------------ |
| `--data-dir`      | `LINDA_DATA_DIR`       | `cv/data`    |
| `--templates-dir` | `LINDA_TEMPLATES_DIR`  | `templates`  |
| `--output-dir`    | `LINDA_OUTPUT_DIR`     | `output`     |

```bash
export LINDA_DATA_DIR=examples/data
export LINDA_TEMPLATES_DIR=templates
export LINDA_OUTPUT_DIR=output
linda generate --plan examples/plan_fr.yaml
```

## How it works

LINDA runs a simple, deterministic pipeline:

```
load  →  score  →  render  →  compile
```

1. **load** — read all data blocks from the data directory and the selected `plan.yaml`.
2. **score** *(optional, experimental)* — measure the plan's keyword coverage
   against a job offer.
3. **render** — fill a Jinja2 → Typst template with the planned blocks and language.
4. **compile** — invoke the Typst CLI to produce the final PDF (plus an optional
   `ats_report.md`).

## Using with AI agents

LINDA is built to be the "hands" of an AI agent that tailors a CV to a specific
job. A typical agent loop looks like this:

1. **Ingest the offer.** The agent reads the job description (pasted text, a file,
   or a URL).
2. **Discover blocks.** It runs `linda list` to enumerate the available
   experiences, projects, skills, and education entries — each with its tags.
3. **Pick and order blocks.** It selects the most relevant blocks (and even
   individual bullets) for the offer and decides the language.
4. **Write a plan.** It emits a `plan.yaml` describing the selection:

   ```yaml
   lang: en
   offer_context: "Backend Developer @ ExampleCorp"
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
     right:
       - type: skills
       - type: education
         items:
           - id: state-university
           - id: cloud-certification
   ```

5. **Validate and generate.** It runs `linda score` to check keyword coverage
   (an experimental heuristic — use it as a hint, not a target to maximize),
   adjusts the plan if needed, then runs `linda generate` to produce the PDF.

Because LINDA itself never calls a model, the agent stays fully in control of the
editorial decisions while LINDA handles the deterministic assembly and typesetting.

## Data model

Data lives as small YAML blocks, and a `plan.yaml` decides how they are assembled.

- **identity** — name, title, summary, contact (single `identity.yaml`).
- **experiences** — one file per job, each with tagged, weighted bullets.
- **projects** — one file per project, same structure as experiences.
- **skills** — categorized skill lists with tags.
- **education** — degrees and certifications.

Every human-readable text field is bilingual (`fr` / `en`); bullets carry `tags`
and a `weight` as authoring metadata (today only block-level `tags` feed the
experimental ATS scorer). A block looks like this:

```yaml
id: acme-corp
title:
  fr: "Développeur Backend – Plateforme E-commerce"
  en: "Backend Developer – E-commerce Platform"
org: ACME Corp
dates: "03/2024 – présent"
tags: [java, spring-boot, postgresql, kubernetes, backend, api]
bullets:
  - text:
      fr: "Conception et développement d'APIs REST en Java Spring Boot"
      en: "Designed and built REST APIs in Java Spring Boot"
    tags: [java, spring-boot, api, backend]
    weight: 1.0
```

The `plan.yaml` then references blocks by `id`, chooses which `bullets` to keep
(`all` or a list of indices), and lays them out across `left` / `right` columns.

For the full reference, see [`docs/data-format.md`](docs/data-format.md) and
[`docs/plan-format.md`](docs/plan-format.md).

## Project layout

```
.
├── linda/            # CLI and the cv_engine pipeline (loader, scorer, renderer, compiler, ingestor)
├── templates/        # Jinja2 → Typst templates (base_fr.typ.j2, base_en.typ.j2)
├── examples/         # Fictional example data blocks and plans
│   ├── data/         #   identity, experiences/, projects/, skills, education
│   ├── plan_fr.yaml
│   └── plan_en.yaml
├── docs/             # Data and plan format reference
├── tests/            # Test suite
└── output/           # Generated .typ / .pdf artifacts (default output dir)
```

## Development

```bash
uv sync          # install dependencies (including the dev group)
uv run pytest    # run the test suite
uv run ruff check # lint
```

## License

[MIT](LICENSE) © 2026 Jimmy Fabre
