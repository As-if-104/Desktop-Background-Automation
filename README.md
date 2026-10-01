# Desktop Background Automation

A small Python script that changes your Windows desktop wallpaper every day, with a one-command option to pin a favorite photo and pause the rotation.

## How it works

- The photo is picked from today's date, so each day gets the next photo in your `Wallpapers` folder, and the list wraps around when it reaches the end.
- Running the script several times in one day always gives the same photo.
- `pin` saves your favorite to `state.json` and the script keeps applying it until you `resume`.

## Setup

1. Clone the repo and put your photos (`.jpg`, `.jpeg`, `.png`, `.bmp`) in the `Wallpapers` folder.
2. Make sure Python 3 is installed.
3. Test it:
```
   python wallpaper_rotator.py
```

## Commands

| Command | What it does |
|---|---|
| `python wallpaper_rotator.py` | Apply today's wallpaper |
| `python wallpaper_rotator.py list` | Show photos with numbers |
| `python wallpaper_rotator.py pin 3` | Stop rotating and keep photo #3 (or use a filename) |
| `python wallpaper_rotator.py pin` | Keep today's photo |
| `python wallpaper_rotator.py resume` | Turn daily rotation back on |
| `python wallpaper_rotator.py status` | Show the current mode |

## Run automatically at login (Windows)

Open Command Prompt **as administrator** and run (change the paths to match your PC):

```
schtasks /create /f /tn "WallpaperRotator" /tr "\"C:\Path\To\pythonw.exe\" \"C:\Path\To\wallpaper_rotator.py\"" /sc onlogon
```

Find your `pythonw.exe` path with `where pythonw`. To remove the task later:

```
schtasks /delete /tn "WallpaperRotator"
```

Note: the task runs at login, so it won't fire when you only wake the laptop from sleep.

## Platform support

Works on Windows, macOS, and GNOME-based Linux.
