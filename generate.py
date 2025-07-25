import os
import json
from pathlib import Path
from collections import defaultdict

class Game:
    def __init__(self, name: str, filename: str, extended: bool, romhack: bool):
        self.name = name
        self.filename = filename
        self.extended = extended
        self.romhack = romhack

    def to_dict(self):
        return {
            "name": self.name,
            "filename": self.filename,
            "extended": self.extended,
            "romhack": self.romhack
        }

def scan_roms(base_dirs):
    games_by_system = defaultdict(list)

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

            for root, _, files in os.walk(system_dir):
                for file in files:
                    # Skip .sav and .zip files
                    if file.lower().endswith(('.sav', '.zip')):
                        continue

                    file_path = Path(root) / file
                    if file_path.is_file():
                        name = file_path.stem
                        romhack = 'romhack' in file.lower()
                        game = Game(name=name, filename=file, extended=extended, romhack=romhack)
                        games_by_system[system].append(game)
                        rh_tag = " [ROMHACK]" if romhack else ""
                        print(f"  📄 {file} (Extended: {extended}){rh_tag}")

    return games_by_system

def save_to_json(games_by_system, output_path="games.json"):
    output = {
        system: [game.to_dict() for game in games]
        for system, games in games_by_system.items()
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

def generate_table(games):
    if not games:
        return []

    lines = []
    lines.append("| System | Name | File | Extended | Romhack |")
    lines.append("|--------|------|------|----------|---------|")
    # Sort by system, then by game name
    for game in sorted(games, key=lambda g: (g.system.lower(), g.name.lower())):
        ext = "Yes" if game.extended else "No"
        rh = "Yes" if game.romhack else "No"
        lines.append(f"| {game.system} | {game.name} | {game.filename} | {ext} | {rh} |")
    lines.append("")  # blank line after table
    return lines


def save_to_markdown(games_by_system, output_path="output.md"):
    # Flatten all games from all systems into one list
    all_games = []
    for system, games in games_by_system.items():
        for game in games:
            # Attach system name to each game for table
            game.system = system
            all_games.append(game)

    lines = generate_table(all_games)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    base_dirs = [
        ("~/roms/best", False),
        ("~/roms/best_extended", True)
    ]

    games_by_system = scan_roms(base_dirs)
    save_to_json(games_by_system)
    save_to_markdown(games_by_system)
    print("Games indexed and saved to games.json and output.md")
