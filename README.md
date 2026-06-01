# Claude's Platformer

A side-scrolling platformer starring the Claude mascot, built with Python + Pygame.

## Run from source

    python -m pip install -r requirements.txt
    python main.py

## Controls

- **Move:** Arrow keys or A/D
- **Jump:** Space / Up / W (hold for higher)
- **Run:** hold Shift
- **Restart** (on win/game-over): Enter
- **Quit:** Esc

## Build a standalone Windows app

Bundle everything into a single double-clickable `.exe` (no Python needed to run it):

    python -m pip install pyinstaller pillow
    python tools/make_icon.py        # (re)generate the Claude icon -> tools/claude.ico
    python -m PyInstaller --noconfirm --onefile --windowed --name ClaudePlatformer --icon tools/claude.ico --add-data "levels/level1.txt;levels" main.py

The app is produced at `dist/ClaudePlatformer.exe` — copy it anywhere and run it.

Create a desktop shortcut with the icon (PowerShell, from the project root):

    $ws = New-Object -ComObject WScript.Shell
    $sc = $ws.CreateShortcut("$([Environment]::GetFolderPath('Desktop'))\Claude's Platformer.lnk")
    $sc.TargetPath = "$PWD\dist\ClaudePlatformer.exe"
    $sc.IconLocation = "$PWD\dist\ClaudePlatformer.exe,0"
    $sc.Save()

## Tests

    python -m pytest

## Project layout

- `game/` — the engine (loop, physics, level, camera, entities, the `assets.py` art seam)
- `levels/level1.txt` — the level, as an editable ASCII grid
- `tools/make_icon.py` — generates the desktop icon
- `tests/` — unit tests for collision and level parsing
