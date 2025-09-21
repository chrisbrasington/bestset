# Rom Best Set Helper

ROM directories can easily grow into the tens or even hundreds of thousands of files, especially if you download complete sets. They can have files with release numbers for weird ordering. 

While it’s nice to have everything preserved, in practice most people only want a curated library of favorites, hidden gems, or romhacks worth playing. 

Sifting through massive folders can be overwhelming and inconvenient when all you want is to quickly find and play a game. That’s why making your own “best set” is so useful: it trims the clutter down to the games that matter to you. 

This tool helps by letting you search across your multiple big ROM directories, pick and rename the ones you want, and copy them into a smaller, personalized collection that’s easier to manage and actually fun to browse.

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