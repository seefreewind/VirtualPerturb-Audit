from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path

GEARS_NORMAN_URL = "https://dataverse.harvard.edu/api/access/datafile/7458694"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/raw/gears_norman.zip")
    parser.add_argument("--url", default=GEARS_NORMAN_URL)
    args = parser.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(args.url, out)
    print(f"downloaded={out}")
    print(f"sha256={sha256(out)}")


if __name__ == "__main__":
    main()

