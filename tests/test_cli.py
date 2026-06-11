from click.testing import CliRunner

from linda.cli import cli

DATA_ARGS = ["--data-dir", "examples/data"]


def test_list_shows_experience_ids():
    result = CliRunner().invoke(cli, ["list", *DATA_ARGS])
    assert result.exit_code == 0
    assert "acme-corp" in result.output
    assert "taskflow" in result.output


def test_list_shows_tags():
    result = CliRunner().invoke(cli, ["list", *DATA_ARGS])
    assert "java" in result.output


def test_list_section_headers_are_english():
    result = CliRunner().invoke(cli, ["list", *DATA_ARGS])
    assert result.exit_code == 0
    assert "Experiences" in result.output
    assert "Projects" in result.output
    assert "Education" in result.output


def test_list_fails_with_missing_data_dir():
    result = CliRunner().invoke(cli, ["list", "--data-dir", "examples/does-not-exist"])
    assert result.exit_code != 0
    assert "does-not-exist" in result.output
    assert "--data-dir" in result.output or "LINDA_DATA_DIR" in result.output


def test_score_with_offer_file(tmp_path):
    offer = tmp_path / "offer.txt"
    offer.write_text("We need a Java Spring Boot developer with Kubernetes.")
    result = CliRunner().invoke(
        cli, ["score", "--plan", "examples/plan_fr.yaml", "--offer", str(offer), *DATA_ARGS]
    )
    assert result.exit_code == 0
    assert "/100" in result.output


def test_score_shows_block_ids(tmp_path):
    offer = tmp_path / "offer.txt"
    offer.write_text("We need Java and Kubernetes expertise.")
    result = CliRunner().invoke(
        cli, ["score", "--plan", "examples/plan_fr.yaml", "--offer", str(offer), *DATA_ARGS]
    )
    assert result.exit_code == 0
    assert "acme-corp" in result.output or "taskflow" in result.output
