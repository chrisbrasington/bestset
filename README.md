# Game Search and Generate Tools

This repository contains two Python scripts to help manage your game collection:

## `search.py` — Interactive Game Finder and Copier

* Detects your current game system folder (e.g., `GBA`).
* Lets you search for games by name across multiple predefined game directories.
* Shows matching files with a numbered list.
* Lets you select which games to copy to your current directory.
* Suggests cleaned filenames by removing leading numbers and unnecessary brackets, but preserves `[romhack]` tags.
* Allows renaming files interactively before copying.
* Runs in a loop until you quit.

### Usage

```bash
python search.py
```

Follow on-screen prompts to search, select, rename, and copy games.

---

## `generate.py` — Game Collection Scanner and Report Generator

* Scans your game directories recursively to index all games.
* Detects if a game is a romhack (filename contains “romhack”).
* Organizes games by system and whether they are standard or extended collections.
* Saves the indexed data as JSON (`games.json`).
* Generates a Markdown report (`output.md`) listing games and rom hacks per system.

### Usage

```bash
python generate.py
```

---

## Notes

* Both scripts use hardcoded paths - adjust these in the scripts if needed.
* Filenames are cleaned and managed smartly during copying and generating reports.