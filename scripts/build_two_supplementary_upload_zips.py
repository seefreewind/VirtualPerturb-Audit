#!/usr/bin/env python3
"""Build two upload zips: supplementary document/images and supplementary tables."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "submission"
SRC = BASE / "supplementary_upload"
DOC_IMG_DIR = BASE / "supplementary_document_and_images"
TABLE_DIR = BASE / "supplementary_tables"

DOC_IMAGE_FILES = [
    "Supplementary_Information.docx",
    "Supplementary_Information.md",
    "Supplementary_Figure_S1_phase2c_endpoint_heatmap.pdf",
    "Supplementary_Figure_S1_phase2c_endpoint_heatmap.png",
    "Supplementary_Figure_S2_phase2c_retrieval_rank_distribution.pdf",
    "Supplementary_Figure_S2_phase2c_retrieval_rank_distribution.png",
    "Supplementary_Figure_S3_state_matched_leave_one_out.pdf",
    "Supplementary_Figure_S3_state_matched_leave_one_out.png",
]

TABLE_FILES = [
    "Key_Resources_Table.xlsx",
    "Source_Data_Manifest.tsv",
    "SUPPLEMENTARY_UPLOAD_MANIFEST.tsv",
]


def reset_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for item in path.iterdir():
        if item.is_file():
            item.unlink()


def copy_group(names: list[str], dst_dir: Path) -> None:
    reset_dir(dst_dir)
    for name in names:
        src = SRC / name
        if not src.exists():
            raise FileNotFoundError(src)
        shutil.copy2(src, dst_dir / name)


def zip_dir(src_dir: Path, zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(src_dir.iterdir()):
            if path.is_file() and not path.name.startswith("._") and path.name != ".DS_Store":
                archive.write(path, arcname=path.name)


def main() -> None:
    copy_group(DOC_IMAGE_FILES, DOC_IMG_DIR)
    copy_group(TABLE_FILES, TABLE_DIR)
    doc_zip = BASE / "Supplementary_Document_and_Images.zip"
    table_zip = BASE / "Supplementary_Tables.zip"
    zip_dir(DOC_IMG_DIR, doc_zip)
    zip_dir(TABLE_DIR, table_zip)
    print(doc_zip)
    print(table_zip)


if __name__ == "__main__":
    main()
