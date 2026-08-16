"""
Zips up the project for sharing/submission, excluding installed-dependency folders
(venv, frontend/node_modules), Python bytecode/test caches (__pycache__, .pytest_cache),
the Claude Code project folder (.claude), and the local .env secrets file.

Usage: python scripts/make_project_zip.py [output_path.zip]
Defaults to ../project-3.zip (one level above the project root).
"""
import os
import sys
import zipfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE_ROOT_NAME = "project-3"

EXCLUDED_DIR_NAMES = {"venv", "node_modules", "__pycache__", ".pytest_cache", ".claude"}
EXCLUDED_FILES = {".env"}  # keep .env.example; never bundle the live API key


def should_skip_dir(dirname):
    return dirname in EXCLUDED_DIR_NAMES


def build_zip(output_path):
    file_count = 0
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
        for root, dirs, files in os.walk(PROJECT_ROOT):
            dirs[:] = [d for d in dirs if not should_skip_dir(d)]
            for fname in files:
                if fname in EXCLUDED_FILES:
                    continue
                abs_path = os.path.join(root, fname)
                rel_path = os.path.relpath(abs_path, PROJECT_ROOT)
                arcname = os.path.join(ARCHIVE_ROOT_NAME, rel_path)
                zf.write(abs_path, arcname)
                file_count += 1
    return file_count


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(PROJECT_ROOT), f"{ARCHIVE_ROOT_NAME}.zip"
    )
    n = build_zip(out)
    size_mb = os.path.getsize(out) / (1024 * 1024)
    print(f"Wrote {out} ({n} files, {size_mb:.1f} MB)")
