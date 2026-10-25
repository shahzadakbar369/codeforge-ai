"""Copies data files (for example data.csv) from each dev program folder into the folder
that holds its generated Python, because migrated code reads its data file next to itself,
just as the legacy PHP read it from its own folder. Without this, such programs fail with
"File not found" even when the translation is fine.

Skipped: .php files, inputs/outputs JSON files and .gitkeep.

Usage:
    python tools/sync_data_files.py        # all dev programs, baseline and repair folders
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEV_DIR = ROOT / "datasets" / "dev"
SKIP_NAMES = {"inputs.json", "outputs.json", "repair_inputs.json", "repair_outputs.json", ".gitkeep"}


def sync_data_files(program_dir, dest_dir):
    """Copy data files from program_dir into dest_dir (which must exist). Returns the names copied."""
    dest_dir, copied = Path(dest_dir), []
    if not dest_dir.exists():
        return copied
    for p in sorted(Path(program_dir).iterdir()):
        if p.is_file() and p.suffix.lower() != ".php" and p.name not in SKIP_NAMES:
            shutil.copy2(p, dest_dir / p.name)
            copied.append(p.name)
    return copied


def main():
    for folder in sorted(p for p in DEV_DIR.iterdir() if p.is_dir()):
        for kind in ("baseline", "repair"):
            copied = sync_data_files(folder, ROOT / "results" / kind / folder.name)
            if copied:
                print(f"{kind}/{folder.name}: copied {', '.join(copied)}")


if __name__ == "__main__":
    main()
