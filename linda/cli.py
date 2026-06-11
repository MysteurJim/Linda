from datetime import date
from pathlib import Path

import click

from linda.cv_engine.compiler import compile_pdf, make_output_dir, write_ats_report, write_typ
from linda.cv_engine.ingestor import ingest_offer
from linda.cv_engine.loader import load_all, load_plan
from linda.cv_engine.renderer import render_cv
from linda.cv_engine.scorer import generate_ats_report, score_plan

DEFAULT_DATA_DIR = "cv/data"
DEFAULT_TEMPLATES_DIR = "templates"
DEFAULT_OUTPUT_DIR = "output"


def _require_data_dir(data_dir: Path) -> None:
    """Exit with a clear error if the data directory does not exist."""
    if not data_dir.is_dir():
        raise click.UsageError(
            f"Data directory not found: {data_dir}\n"
            f"Provide a valid path with --data-dir or the LINDA_DATA_DIR environment variable."
        )


data_dir_option = click.option(
    "--data-dir",
    "data_dir",
    default=DEFAULT_DATA_DIR,
    envvar="LINDA_DATA_DIR",
    show_default=True,
    type=click.Path(),
    help="Directory containing CV data (identity, experiences, projects, skills, education).",
)
templates_dir_option = click.option(
    "--templates-dir",
    "templates_dir",
    default=DEFAULT_TEMPLATES_DIR,
    envvar="LINDA_TEMPLATES_DIR",
    show_default=True,
    type=click.Path(),
    help="Directory containing Typst Jinja2 templates.",
)
output_dir_option = click.option(
    "--output-dir",
    "output_dir",
    default=DEFAULT_OUTPUT_DIR,
    envvar="LINDA_OUTPUT_DIR",
    show_default=True,
    type=click.Path(),
    help="Directory where generated CVs are written.",
)


@click.group()
def cli():
    """LINDA — Modular Typst CV Generator."""


@cli.command("list")
@data_dir_option
def cmd_list(data_dir):
    """List all available blocks with IDs and tags."""
    data_dir = Path(data_dir)
    _require_data_dir(data_dir)
    data = load_all(data_dir)

    click.echo("-- Experiences ------------------------------------------")
    for exp_id, exp in data["experiences"].items():
        click.echo(f"  {exp_id:<28} [{', '.join(exp.get('tags', []))}]")
        click.echo(f"    {exp.get('title', {}).get('fr', '')}")

    click.echo("\n-- Projects ---------------------------------------------")
    for pid, proj in data["projects"].items():
        click.echo(f"  {pid:<28} [{', '.join(proj.get('tags', []))}]")
        click.echo(f"    {proj.get('title', {}).get('fr', '')}")

    click.echo("\n-- Education --------------------------------------------")
    for f in data["education"].get("formations", []):
        click.echo(f"  {f['id']}")


@cli.command("score")
@click.option("--plan", "plan_path", required=True, type=click.Path(), help="Path to plan.yaml")
@click.option("--offer", "offer_source", required=True,
              help="Offer source: file path, URL, or '-' for stdin")
@data_dir_option
def cmd_score(plan_path, offer_source, data_dir):
    """Score the plan against a job offer and print the ATS report (experimental)."""
    data_dir = Path(data_dir)
    _require_data_dir(data_dir)
    data = load_all(data_dir)
    plan = load_plan(Path(plan_path))
    offer_text = ingest_offer(offer_source)
    report_data = score_plan(plan, data, offer_text)
    click.echo(generate_ats_report(report_data))


@cli.command("generate")
@click.option("--plan", "plan_path", required=True, type=click.Path(), help="Path to plan.yaml")
@click.option("--offer", "offer_source", default=None,
              help="Optional offer source to include an ATS report (experimental) in output")
@click.option("--date", "gen_date", default=None, help="Override date YYYY-MM-DD (default: today)")
@data_dir_option
@templates_dir_option
@output_dir_option
def cmd_generate(plan_path, offer_source, gen_date, data_dir, templates_dir, output_dir):
    """Generate CV .typ, .pdf (and optional ats_report.md) from plan.yaml."""
    data_dir = Path(data_dir)
    templates_dir = Path(templates_dir)
    output_dir = Path(output_dir)
    _require_data_dir(data_dir)
    data = load_all(data_dir)
    plan = load_plan(Path(plan_path))

    today = gen_date or str(date.today())
    context = plan.get("offer_context", "CV")
    parts = context.split("@")
    job_title = parts[0].strip()
    company = parts[1].strip() if len(parts) > 1 else "Unknown"

    out_dir = make_output_dir(output_dir, job_title, company, today)

    click.echo(f"Rendering ({plan.get('lang', 'fr')})...")
    typ_content = render_cv(plan, data, templates_dir)
    typ_path = write_typ(out_dir, typ_content)
    click.echo(f"  {typ_path}")

    click.echo("Compiling PDF...")
    try:
        pdf_path = compile_pdf(typ_path)
        click.echo(f"  {pdf_path}")
    except RuntimeError as e:
        click.echo(f"Compilation failed: {e}", err=True)
        raise SystemExit(1)

    if offer_source:
        offer_text = ingest_offer(offer_source)
        report_data = score_plan(plan, data, offer_text)
        ats_path = write_ats_report(out_dir, generate_ats_report(report_data))
        click.echo(f"  {ats_path}  (score: {report_data['global_score']}/100)")

    click.echo(f"\nOutput: {out_dir}/")
