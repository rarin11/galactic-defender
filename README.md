# Galactic Defender: Boss Rush

A 2D arcade space shooter built from scratch in Python with Pygame. Pilot one of four unique ships, survive waves of meteors and UFOs, and take down multi-phase bosses across three difficulty levels.

## Features
- 4 playable ships with different stats, plus a Super Laser special ability
- Multi-phase boss fights with attack patterns and a health bar
- 3 difficulty levels: Easy, Normal, Hard
- Upgrade shop: fire rate, damage and health, bought with collected diamonds
- User registration and login, progress saved locally to JSON
- Menu system with English and Lithuanian interface, music and fullscreen settings
- Object-oriented design: separate classes for the player, enemies, bosses, projectiles, explosions and UI

## Controls
| Key | Action |
|---|---|
| Arrow keys | Move the ship |
| F | Super Laser (when charged) |
| Esc | Pause / back |
| Mouse | Menus |

## How to run

**Option 1. Windows executable**
Download `GalacticDefender-Windows.zip` from the Releases page, unzip it and run `main.exe`.

**Option 2. From source**
```bash
pip install pygame
python main.py
```
Python 3.10+ is recommended. Run the game from the project folder so that it can find the `assets/` folder.

## Tech stack
Python, Pygame, PyInstaller, JSON

## Notes
Accounts are stored locally in plain text and are for learning purposes only.

## Credits
- Fonts: Bytesized and Jersey 15 (SIL Open Font License)
- Art and sound: a mix of original, AI-generated and free online assets

## Authors
Aysel Taghizade, Vilnius Tech
Ali Zamanov, Vilnius Tech
