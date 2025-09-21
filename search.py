import json
import os
import shutil
import re
from pathlib import Path

# Load config.json
with open("config.json", "r") as f:
    config = json.load(f)

# Expand ~ into home directory
BASE_DIRS = [Path(os.path.expanduser(p)) for p in config["base_dirs"]]

# print("Loaded BASE_DIRS:")
# for d in BASE_DIRS:
#     print(" -", d)

SKIP_EXTENSIONS = {'.png', '.sav', '.zip'}

def get_system_from_path(path: Path) -> str:
    return path.name

def resolve_case_insensitive_path(base_dir: Path, system_folder: str) -> Path | None:
    for candidate in (system_folder, system_folder.lower()):
        candidate_path = base_dir / candidate
        if candidate_path.exists():
            return candidate_path
    return None

def walk_with_depth(path: Path, max_depth: int):
    """Yield files from path up to a certain directory depth."""
    start_depth = len(path.parts)
    for root, dirs, files in os.walk(path):
        current_depth = len(Path(root).parts) - start_depth
        if current_depth > max_depth:
            dirs[:] = []  # prevent deeper walk
            continue
        for f in files:
            yield Path(root) / f

def file_matches(file: Path, term: str) -> bool:
    if file.suffix.lower() in SKIP_EXTENSIONS:
        return False
    if term.lower() == "system":
        return True
    return term.lower() in file.name.lower()

def search_roms(search_term: str, system_folder: str, max_depth: int = 2):
    matches = []
    for base_dir in BASE_DIRS:
        if base_dir.name.lower() == "downloads":
            for root, _, files in os.walk(base_dir):
                for f in files:
                    path = Path(root) / f
                    if file_matches(path, search_term):
                        matches.append(path)
            continue

        start_path = resolve_case_insensitive_path(base_dir, system_folder)

        # Special fallback: PS1 -> PS
        if not start_path and system_folder.upper() == "PS1":
            start_path = resolve_case_insensitive_path(base_dir, "PS")

        if not start_path:
            continue

        for file in walk_with_depth(start_path, max_depth):
            if file_matches(file, search_term):
                matches.append(file)

    return matches

def deep_search_roms(search_term: str, system_folder: str):
    matches = []
    for base_dir in BASE_DIRS:
        system_path = resolve_case_insensitive_path(base_dir, system_folder)
        start_path = system_path.parent if system_path else base_dir

        for root, _, files in os.walk(start_path):
            for f in files:
                path = Path(root) / f
                if file_matches(path, search_term):
                    matches.append(path)

    return matches

def clean_filename(name: str) -> str:
    name = re.sub(r'^\s*\d+\s*[-_]*\s*', '', name)
    stem, ext = name.rsplit('.', 1)

    def preserve_if(match, keep_patterns):
        content = match.group(1).lower()
        return match.group(0) if any(p in content for p in keep_patterns) else ''

    keep_patterns = ['romhack', 'disc']
    stem = re.sub(r'\(([^)]*)\)', lambda m: preserve_if(m, keep_patterns), stem)
    stem = re.sub(r'\[([^]]*)\]', lambda m: preserve_if(m, keep_patterns), stem)
    stem = re.sub(r'\s+', ' ', stem).strip()

    return f"{stem}.{ext}"

def copy_selected_files(selected_indices, files, target_dir: Path):
    for idx in selected_indices:
        try:
            src = files[idx]
            suggested_name = clean_filename(src.name)

            print(f"\nCopy file: '{src.name}'")
            print(f"Suggested name (press Enter to accept): {suggested_name}")
            new_name = input("Or type a new name: ").strip() or suggested_name

            dst = target_dir / new_name
            print(f"Copying '{src.name}' -> '{dst.name}'")
            shutil.copy2(src, dst)
        except IndexError:
            print(f"Invalid selection: {idx + 1}")

def main():
    current_dir = Path.cwd()
    system_folder = get_system_from_path(current_dir)

    print(f"Detected system: {system_folder}\n(based of current directory)")

    while True:
        search_term = input("\nEnter search term (or 'q' to quit): ").strip()
        if search_term.lower() == 'q':
            print("Quitting.")
            break
        if not search_term:
            print("Empty search term, please enter something.")
            continue

        matching_files = search_roms(search_term, system_folder)
        if not matching_files:
            print("No matching files found in normal search. Running deep search...")
            matching_files = deep_search_roms(search_term, system_folder)
            if not matching_files:
                print("No matching files found in deep search either.")
                continue

        print("\nFound files:")
        for i, f in enumerate(matching_files, 1):
            print(f"{i}. {f.name}\n   {f}")

        selected = input("\nEnter file numbers to copy (e.g. 1,2 or 'all'): ").strip().lower()
        if selected == "all":
            selected_indices = list(range(len(matching_files)))
        else:
            selected_indices = [int(x.strip()) - 1 for x in selected.split(",") if x.strip().isdigit()]

        copy_selected_files(selected_indices, matching_files, current_dir)

if __name__ == "__main__":
    main()
