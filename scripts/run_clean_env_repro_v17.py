#!/usr/bin/env python3
"""Run a clean-environment reproduction check for v1.7."""

from __future__ import annotations

import importlib.metadata as metadata
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / ".clean_env_v17"
REPORT = ROOT / "reports" / "CLEAN_ENV_REPRODUCTION_V17.md"
PACKAGES = [
    "numpy",
    "pandas",
    "matplotlib",
    "scipy",
    "scikit-learn",
    "python-docx",
    "openpyxl",
    "pytest",
    "pillow",
    "tabulate",
]


def run(cmd: list[str], cwd: Path = ROOT, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, env=env)


def main() -> int:
    start = time.time()
    if ENV.exists():
        shutil.rmtree(ENV, ignore_errors=True)
    bundled_python = Path("/Users/zy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3")
    base_python = bundled_python if bundled_python.exists() else Path(sys.executable)
    proc = run([str(base_python), "-m", "venv", str(ENV)])
    if proc.returncode:
        write_report("FAIL", start, [("create venv", proc)])
        return proc.returncode

    py = ENV / "bin" / "python"
    prune_appledouble(ENV)
    steps: list[tuple[str, subprocess.CompletedProcess[str]]] = []
    for label, cmd in [
        ("pip upgrade", [str(py), "-m", "pip", "install", "--upgrade", "pip"]),
        ("pip install", [str(py), "-m", "pip", "install", *PACKAGES]),
        ("minimal example", [str(py), "run_minimal_audit.py"]),
        ("Figure 1", [str(py), "scripts/build_figure1_v2.py"]),
        ("Figure 2", [str(py), "scripts/build_figure2_v2.py"]),
        ("Figure 3", [str(py), "scripts/build_figure3_v2.py"]),
        ("Figure 4", [str(py), "scripts/build_figure4_v2.py"]),
        ("Figure 5", [str(py), "scripts/build_figure5_v2.py"]),
        ("pytest", [str(py), "-m", "pytest", "-q", "tests"]),
    ]:
        cwd = ROOT / "examples" / "minimal_audit" if label == "minimal example" else ROOT
        proc = run(cmd, cwd=cwd)
        steps.append((label, proc))
        prune_appledouble(ENV)
        if proc.returncode:
            write_report("FAIL", start, steps)
            return proc.returncode
    write_report("PASS", start, steps)
    return 0


def installed_versions(py: Path) -> str:
    code = """import importlib.metadata as m
for pkg in ['numpy','pandas','matplotlib','scipy','scikit-learn','python-docx','openpyxl','pytest','pillow','tabulate']:
    try:
        print(f'{pkg}: {m.version(pkg)}')
    except Exception as e:
        print(f'{pkg}: missing ({e})')
"""
    proc = run([str(py), "-c", code])
    return proc.stdout.strip() or proc.stderr.strip()


def prune_appledouble(path: Path) -> None:
    if not path.exists():
        return
    for p in path.rglob("._*"):
        if p.is_file():
            p.unlink()


def file_checks() -> str:
    rows = []
    for rel in [
        "examples/minimal_audit/minimal_audit_table.csv",
        "figures/main/Figure1.png",
        "figures/main/Figure2_v2.png",
        "figures/main/Figure3_v2.png",
        "figures/main/Figure4_v2.png",
        "figures/main/Figure5_v2.png",
    ]:
        p = ROOT / rel
        rows.append(f"- `{rel}`: {'present' if p.exists() and p.stat().st_size else 'missing'}")
    return "\n".join(rows)


def write_report(status: str, start: float, steps: list[tuple[str, subprocess.CompletedProcess[str]]]) -> None:
    py = ENV / "bin" / "python"
    lines = [
        "# Clean-Environment Reproduction v1.7",
        "",
        f"Status: {status}",
        "",
        "## Environment",
        "",
        f"Python executable: `{py}`",
        f"System Python: `{sys.executable}`",
        f"OS: {platform.platform()}",
        "",
        "## Package versions",
        "",
        "```text",
        installed_versions(py) if py.exists() else "environment not created",
        "```",
        "",
        "## Commands and outcomes",
        "",
        "| Step | Return code | Notes |",
        "|---|---:|---|",
    ]
    for label, proc in steps:
        note = (proc.stdout.strip() or proc.stderr.strip()).splitlines()
        snippet = " / ".join(note[-3:]) if note else ""
        snippet = snippet.replace("|", "\\|")[:300]
        lines.append(f"| {label} | {proc.returncode} | {snippet} |")
    lines += [
        "",
        "## Expected output files",
        "",
        file_checks(),
        "",
        f"Wall time seconds: {time.time() - start:.1f}",
        "",
        "Peak memory: not measured.",
        "",
        "Warnings: figure scripts may update timestamped figure QC reports while preserving frozen source tables.",
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
