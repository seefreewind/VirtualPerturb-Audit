from __future__ import annotations

import subprocess
import sys


def main():
    subprocess.run([sys.executable, "scripts/audit_norman_dataset.py"], check=True)
    subprocess.run([sys.executable, "scripts/audit_norman_geo_metadata.py"], check=True)
    subprocess.run([sys.executable, "scripts/run_baseline_pilot.py"], check=True)
    subprocess.run([sys.executable, "scripts/run_falsification_pilot.py"], check=True)
    subprocess.run([sys.executable, "scripts/build_figures.py"], check=True)
    subprocess.run([sys.executable, "scripts/build_tables.py"], check=True)


if __name__ == "__main__":
    main()
