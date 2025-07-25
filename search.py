import os
import shutil
import re
from pathlib import Path

def get_system_from_path(path: Path):
    return path.name

def resolve_case_insensitive_path(base_dir: Path, system_folder: str):
    """
    Try to resolve the system folder in both original and lowercase form.
    """
    direct_path = base_dir / system_folder
    if direct_path.exists():
        return direct_path

    lower_path = base_dir / system_folder.lower()
    if lower_path.exists():
        return lower_path

    return None  # Neither found

def walk_with_depth(path: Path, max_depth: int):
    """Yield files up to a certain depth from a root path."""
    start_depth = len(path.parts)
    for root, dirs, files in os.walk(path):
        current_depth = len(Path(root).parts) - start_depth
        if current_depth > max_depth:
            # Prevent walking deeper
            dirs[:] = []
            continue
        for f in files:
            yield Path(root) / f

def search_roms(search_term, system_folder, max_depth=2):
    base_dirs = [
        Path(os.path.expanduser("~/roms/rg34xx/ROMS")),
        Path(os.path.expanduser("~/roms/miyoo/Roms")),
        Path("/mnt/archive/tertiary/emulation/roms"),
        Path(os.path.expanduser("~/Downloads"))
    ]

    def file_matches(file, term):
        return (
            file.suffix.lower() not in ['.png', '.sav', '.zip'] and
            term.lower() in file.name.lower()
        )

    matches = []
    for base_dir in base_dirs:
        if base_dir == Path(os.path.expanduser("~/Downloads")):
            # search all of ~/Downloads recursively, ignoring system_folder subfolder
            start_path = base_dir
        else:
            start_path = resolve_case_insensitive_path(base_dir, system_folder)
            if not start_path:
                continue

        if base_dir == Path(os.path.expanduser("~/Downloads")):
            # Recursive search in all Downloads
            for root, dirs, files in os.walk(start_path):
                for f in files:
                    file_path = Path(root) / f
                    if file_matches(file_path, search_term):
                        matches.append(file_path)
        else:
            # Limited depth search for others
            for file in walk_with_depth(start_path, max_depth):
                if file_matches(file, search_term):
                    matches.append(file)

    return matches

def deep_search_roms(search_term, system_folder):
    """
    Deep search starting one directory above system folder,
    searching fully recursively.
    """
    base_dirs = [
        Path(os.path.expanduser("~/roms/rg34xx/ROMS")),
        Path(os.path.expanduser("~/roms/miyoo/Roms")),
        Path("/mnt/archive/tertiary/emulation/roms"),
        Path("~/Downloads")
    ]

    def file_matches(file, term):
        return (
            file.suffix.lower() not in ['.png', '.sav'] and
            term.lower() in file.name.lower()
        )

    matches = []
    for base_dir in base_dirs:
        system_path = resolve_case_insensitive_path(base_dir, system_folder)
        if system_path:
            start_path = system_path.parent  # one directory above system folder
        else:
            start_path = base_dir  # fallback: base dir itself

        for root, dirs, files in os.walk(start_path):
            for file in files:
                fpath = Path(root) / file
                if file_matches(fpath, search_term):
                    matches.append(fpath)

    return matches

def clean_filename(name):
    # Remove leading numbers and separators
    name = re.sub(r'^\s*\d+\s*[-_]*\s*', '', name)

    # Split name and extension
    stem, ext = name.rsplit('.', 1)

    # Function to conditionally remove bracketed parts
    def remove_brackets(match):
        content = match.group(1)
        # Keep bracket if it contains 'romhack' (case insensitive)
        if 'romhack' in content.lower():
            return match.group(0)  # keep brackets and content
        else:
            return ''  # remove brackets and content

    # Remove (...) and [...] unless they contain 'romhack'
    stem = re.sub(r'\(([^)]*)\)', remove_brackets, stem)
    stem = re.sub(r'\[([^]]*)\]', remove_brackets, stem)

    # Clean up extra spaces from removals
    stem = re.sub(r'\s+', ' ', stem).strip()

    return stem + '.' + ext

def copy_selected_files(selected_indices, files, target_dir):
    for idx in selected_indices:
        try:
            src = files[idx]
            suggested_name = clean_filename(src.name)

            print(f"\nCopy file: '{src.name}'")
            print(f"Suggested name (press Enter to accept): {suggested_name}")
            new_name = input("Or type a new name: ").strip()

            if new_name == "":
                dst_name = suggested_name
            else:
                dst_name = new_name

            dst = target_dir / dst_name
            print(f"Copying '{src.name}' -> '{dst.name}'")
            shutil.copy2(src, dst)
        except IndexError:
            print(f"Invalid selection: {idx + 1}")

def main():
    current_dir = Path.cwd()
    system_folder = get_system_from_path(current_dir)

    print(f"Detected system: {system_folder}")

    while True:
        while True:
            search_term = input("\nEnter search term (or 'q' to quit): ").strip()
            if search_term.lower() == 'q':
                print("Quitting.")
                return
            if search_term == "":
                print("Empty search term, please enter something.")
                continue
            break

        matching_files = search_roms(search_term, system_folder)

        if not matching_files:
            print("No matching files found in normal search. Running deep search...")
            matching_files = deep_search_roms(search_term, system_folder)
            if not matching_files:
                print("No matching files found in deep search either.")
                continue

        print("\nFound files:")
        for i, f in enumerate(matching_files, 1):
            print(f"{i}. {f.name}")

        selected = input("\nEnter file numbers to copy (e.g. 1,2 or 'all'): ").strip().lower()

        if selected == "all":
            selected_indices = list(range(len(matching_files)))
        else:
            selected_indices = [int(x.strip()) - 1 for x in selected.split(",") if x.strip().isdigit()]

        copy_selected_files(selected_indices, matching_files, current_dir)

if __name__ == "__main__":
    main()
