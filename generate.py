import os
import json
import re
from pathlib import Path
from collections import defaultdict

class Game:
    def __init__(self, system: str, name: str, filenames: list, extended: bool, romhack: bool):
        self.system = system
        self.name = name
        self.filenames = filenames
        self.extended = extended
        self.romhack = romhack

    def to_dict(self):
        return {
            "system": self.system,
            "name": self.name,
            "filenames": self.filenames,
            "extended": self.extended,
            "romhack": self.romhack
        }

def scan_roms(base_dirs):
    games_by_system = defaultdict(list)

    disc_pattern_sq = re.compile(r"^(.*)\s\[(Disc\d+of\d+)\]$", re.IGNORECASE)
    disc_pattern_paren = re.compile(r"^(.*)\s\((Disc\s*\d+)\)$", re.IGNORECASE)

    for base_dir, extended in base_dirs:
        base_path = Path(os.path.expanduser(base_dir))
        label = "EXTENDED" if extended else "STANDARD"

        if not base_path.exists():
            print(f"⚠️  Base path not found: {base_path}")
            continue

        for system_dir in base_path.iterdir():
            if not system_dir.is_dir():
                continue
            system = system_dir.name
            print(f"\n🔎 Scanning system: {system} ({label})")

            grouped_games = defaultdict(lambda: {"files": [], "extended": extended, "romhack": False})

            for root, _, files in os.walk(system_dir):
                for file in files:
                    if file.lower().endswith(('.sav', '.zip')):
                        continue

                    file_path = Path(root) / file
                    if file_path.is_file():
                        romhack = 'romhack' in file.lower()
                        stem = file_path.stem

                        match = disc_pattern_sq.match(stem)
                        if not match:
                            match = disc_pattern_paren.match(stem)

                        if match:
                            base_name = match.group(1).strip()
                            grouped_games[base_name]["files"].append(file)
                            grouped_games[base_name]["romhack"] = grouped_games[base_name]["romhack"] or romhack
                        else:
                            grouped_games[stem]["files"].append(file)
                            grouped_games[stem]["romhack"] = grouped_games[stem]["romhack"] or romhack

            for base_name, data in grouped_games.items():
                files = data["files"]
                extended = data["extended"]
                romhack = data["romhack"]

                game = Game(system=system, name=base_name, filenames=files, extended=extended, romhack=romhack)
                games_by_system[system].append(game)

                rh_tag = " [ROMHACK]" if romhack else ""
                print(f"  📄 {base_name} ({len(files)} file{'s' if len(files) != 1 else ''}) (Extended: {extended}){rh_tag}")

    return games_by_system

def generate_table(games):
    if not games:
        return []

    lines = []
    lines.append("| System | Name | Files | Romhack |")
    lines.append("|--------|------|-------|---------|")

    for game in sorted(games, key=lambda g: (g.system.lower(), g.name.lower())):
        ext = "Yes" if game.extended else "No"
        rh = "Yes" if game.romhack else "No"
        files_joined = ", ".join(game.filenames)
        lines.append(f"| {game.system} | {game.name} | {files_joined} | {rh} |")

    lines.append("")
    return lines

def save_to_json(games_by_system, output_path="games.json"):
    output = {
        system: [game.to_dict() for game in games]
        for system, games in games_by_system.items()
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

def save_to_markdown(games_by_system, output_path):
    script_dir = os.path.dirname(output_path)

    all_games = []
    for system, games in games_by_system.items():
        all_games.extend(games)

    # Save combined output.md
    combined_lines = generate_table(all_games)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(combined_lines))

    # Save one file per system in script_dir
    for system, games in games_by_system.items():
        lines = generate_table(games)
        file_name = os.path.join(script_dir, f"{system}.md")
        with open(file_name, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

if __name__ == "__main__":
    # find the config.json in the same directory as generate.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.json")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    target_dirs = config.get("TARGET_DIRS", [])
    extended_dirs = config.get("EXTENDED_TARGET_DIRS", [])

    # build base_dirs in the same structure you had before
    base_dirs = [(d, False) for d in target_dirs] + [(d, True) for d in extended_dirs]

    print("Base dirs loaded from config.json:")
    for path, is_extended in base_dirs:
        print(f"  {path} (extended={is_extended})")
        
    games_by_system = scan_roms(base_dirs)

    # save everything into script_dir
    save_to_json(games_by_system, os.path.join(script_dir, "games.json"))
    save_to_markdown(games_by_system, os.path.join(script_dir, "output.md"))
    print("✅ Games saved to games.json, output.md, and per-system markdown files.")