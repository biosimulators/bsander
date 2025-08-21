# This file contains utility functions to deal with parsing input archives for relevant info
import os
import zipfile

def _extract_pbif_from_zip(archive_path: str, output_dir: str) -> str:
    with zipfile.ZipFile(archive_path) as archive:
        for name in archive.namelist():
            if not name.endswith(".pbif") and not name.endswith(".json"):
                continue
            return archive.extract(name, output_dir)
    raise ValueError(f"Could not locate Process Bigraph Intermediate Format file within archive: {archive_path}")

def _extract_pbif_from_omex(archive_path: str, output_dir: str):
    # At the moment, we're not doing anything complicated...
    return _extract_pbif_from_zip(archive_path, output_dir)

def extract_pbif_from_archive(archive_path: str, output_dir: str):
    if archive_path.endswith(".omex"):
        return _extract_pbif_from_omex(archive_path, output_dir)
    elif archive_path.endswith(".zip"):
        return _extract_pbif_from_zip(archive_path, output_dir)
    else:
        raise Exception(f"Unsupported archive: {archive_path}")

