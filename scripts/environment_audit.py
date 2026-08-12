from __future__ import annotations

import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import psutil


PACKAGES = ["torch", "scanpy", "anndata", "numpy", "scipy", "sklearn", "pandas"]


def run(cmd):
    try:
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True).strip()
    except Exception as exc:
        return f"UNAVAILABLE: {exc}"


def package_version(name: str) -> str:
    try:
        mod = __import__(name)
        return getattr(mod, "__version__", "UNKNOWN")
    except Exception as exc:
        return f"UNAVAILABLE: {exc}"


def main():
    lines = [
        "# Environment Report",
        "",
        f"Audit timestamp UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Hardware and OS",
        "",
        f"- OS: {platform.platform()}",
        f"- Kernel: {run(['uname', '-a'])}",
        f"- CPU: {run(['sysctl', '-n', 'machdep.cpu.brand_string'])}",
        f"- RAM: {psutil.virtual_memory().total / (1024 ** 3):.2f} GiB",
        f"- GPU: {'UNAVAILABLE: nvidia-smi not found' if shutil.which('nvidia-smi') is None else run(['nvidia-smi'])}",
        f"- CUDA: {'UNAVAILABLE: nvidia-smi not found' if shutil.which('nvidia-smi') is None else 'see nvidia-smi output'}",
        "",
        "## Python",
        "",
        f"- `python`: {run(['zsh', '-lc', 'python --version'])}",
        f"- `python3`: {run(['python3', '--version'])}",
        "",
        "## Key Packages",
        "",
        "| Package | Version |",
        "|---|---|",
    ]
    for pkg in PACKAGES:
        lines.append(f"| {pkg} | {package_version(pkg)} |")
    lines.extend([
        "",
        "## pip freeze",
        "",
        "```text",
        run(["python3", "-m", "pip", "freeze"]),
        "```",
    ])
    Path("environment/environment_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

