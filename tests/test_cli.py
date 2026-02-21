"""Tests for the CLI interface."""

import json
import subprocess
import sys

import pytest


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "src.cli", *args],
        capture_output=True,
        text=True,
    )


class TestSingleMode:
    def test_legacy_flat_args(self):
        result = run_cli("--ccs", "0.86", "--eav", "0.74", "--cpr", "0.58", "--wm", "0.60")
        assert result.returncode == 0
        assert "ECDS Shock Index:" in result.stdout

    def test_single_subcommand(self):
        result = run_cli("single", "--ccs", "0.86", "--eav", "0.74", "--cpr", "0.58", "--wm", "0.60")
        assert result.returncode == 0
        assert "ECDS Shock Index:" in result.stdout
        # Should include risk tier
        assert "risk" in result.stdout.lower()

    def test_single_json_output(self):
        result = run_cli("single", "--ccs", "0.5", "--eav", "0.5", "--cpr", "0.5", "--wm", "0.5", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "shock_index" in data
        assert "risk_tier" in data

    def test_no_args_shows_help(self):
        result = run_cli()
        assert result.returncode != 0


class TestBatchMode:
    def test_batch_stdout(self):
        result = run_cli(
            "batch",
            "--ecds", "data/raw/example_ncqa_ecds.csv",
            "--weights", "data/raw/example_cms_measure_weights.csv",
        )
        assert result.returncode == 0
        assert "Contract Summary" in result.stdout
        assert "Weighted Shock Index" in result.stdout

    def test_batch_csv_output(self, tmp_path):
        out = tmp_path / "scored.csv"
        result = run_cli(
            "batch",
            "--ecds", "data/raw/example_ncqa_ecds.csv",
            "--weights", "data/raw/example_cms_measure_weights.csv",
            "--output", str(out),
        )
        assert result.returncode == 0
        assert out.exists()
        assert "shock_index" in out.read_text()

    def test_batch_json_output(self):
        result = run_cli(
            "batch",
            "--ecds", "data/raw/example_ncqa_ecds.csv",
            "--weights", "data/raw/example_cms_measure_weights.csv",
            "--json",
        )
        assert result.returncode == 0
        # JSON summary should be parseable from the output
        lines = result.stdout.strip().split("\n")
        # Find the JSON block (last lines after the blank line)
        json_start = None
        for i, line in enumerate(lines):
            if line.strip() == "":
                json_start = i + 1
        assert json_start is not None
        json_text = "\n".join(lines[json_start:])
        data = json.loads(json_text)
        assert "weighted_shock_index" in data
