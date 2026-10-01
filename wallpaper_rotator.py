"""
Daily wallpaper rotator (Windows / macOS / Linux-GNOME).

Setup: put your photos in a folder named "wallpapers" next to this file.

Commands:
  python wallpaper_rotator.py            -> apply today's wallpaper (respects pin)
  python wallpaper_rotator.py list       -> show photos with numbers
  python wallpaper_rotator.py pin 3      -> stop rotating, keep photo #3 (or a filename)
  python wallpaper_rotator.py pin        -> keep whatever today's photo is
  python wallpaper_rotator.py resume     -> start daily rotation again
  python wallpaper_rotator.py status     -> show current mode
"""
import argparse
import ctypes
import json
import platform
import subprocess
import sys
from datetime import date
from pathlib import Path

BASE = Path(__file__).resolve().parent
FOLDER = BASE / "wallpapers"
STATE_FILE = BASE / "state.json"
EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


# ---------- 1. Finding the photos ----------
def get_images():
    if not FOLDER.exists():
        sys.exit(f"Folder not found: {FOLDER}\nCreate it and put your photos inside.")
    images = sorted(p for p in FOLDER.iterdir() if p.suffix.lower() in EXTENSIONS)
    if not images:
        sys.exit(f"No images found in {FOLDER}")
    return images


# ---------- 2. Remembering the pin ----------
def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"pinned": None}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ---------- 3. Today's pick ----------
def todays_image(images):
    # Same date -> same photo; next day -> next photo; wraps around at the end.
    return images[date.today().toordinal() % len(images)]


# ---------- 4. Setting the wallpaper (per OS) ----------
def set_wallpaper(path: Path):
    path = str(path.resolve())
    system = platform.system()

    if system == "Windows":
        # SPI_SETDESKWALLPAPER = 20, flags 3 = update ini file + notify apps
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)

    elif system == "Darwin":  # macOS
        script = (
            'tell application "System Events" to tell every desktop '
            f'to set picture to "{path}"'
        )
        subprocess.run(["osascript", "-e", script], check=True)

    elif system == "Linux":  # GNOME
        uri = Path(path).as_uri()
        for key in ("picture-uri", "picture-uri-dark"):
            subprocess.run(
                ["gsettings", "set", "org.gnome.desktop.background", key, uri],
                check=True,
            )
    else:
        sys.exit(f"Unsupported OS: {system}")


# ---------- 5. Commands ----------
def cmd_run(images, state):
    if state["pinned"]:
        pinned = FOLDER / state["pinned"]
        if pinned.exists():
            set_wallpaper(pinned)
            print(f"Pinned wallpaper kept: {pinned.name}")
            return
        print("Pinned file is missing - falling back to rotation.")
    choice = todays_image(images)
    set_wallpaper(choice)
    print(f"Today's wallpaper: {choice.name}")


def cmd_list(images, state):
    for i, img in enumerate(images, 1):
        marks = []
        if img.name == state["pinned"]:
            marks.append("pinned")
        if img == todays_image(images):
            marks.append("today's pick")
        print(f"{i}. {img.name}  {'(' + ', '.join(marks) + ')' if marks else ''}")


def cmd_pin(images, state, target):
    if target is None:
        chosen = todays_image(images)
    elif target.isdigit() and 1 <= int(target) <= len(images):
        chosen = images[int(target) - 1]
    else:
        matches = [p for p in images if p.name.lower() == target.lower()]
        if not matches:
            sys.exit(f"No photo matches '{target}'. Try: list")
        chosen = matches[0]
    state["pinned"] = chosen.name
    save_state(state)
    set_wallpaper(chosen)
    print(f"Rotation OFF. Pinned: {chosen.name}")


def cmd_resume(images, state):
    state["pinned"] = None
    save_state(state)
    cmd_run(images, state)
    print("Rotation ON.")


def cmd_status(images, state):
    if state["pinned"]:
        print(f"Rotation OFF - pinned to {state['pinned']}")
    else:
        print(f"Rotation ON - today's pick: {todays_image(images).name}")


def main():
    parser = argparse.ArgumentParser(description="Daily wallpaper rotator")
    parser.add_argument("command", nargs="?", default="run",
                        choices=["run", "list", "pin", "resume", "status"])
    parser.add_argument("target", nargs="?", help="photo number or filename (for pin)")
    args = parser.parse_args()

    images, state = get_images(), load_state()
    if args.command == "run":
        cmd_run(images, state)
    elif args.command == "list":
        cmd_list(images, state)
    elif args.command == "pin":
        cmd_pin(images, state, args.target)
    elif args.command == "resume":
        cmd_resume(images, state)
    elif args.command == "status":
        cmd_status(images, state)


if __name__ == "__main__":
    main()