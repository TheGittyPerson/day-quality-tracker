"""Create an executable shell script as a shortcut to start DQT.

Ensure this is run within the project directory.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def write(path: Path) -> None:
    """Write system-appropriate launcher contents to file."""
    if sys.platform == "win32":
        script_contents = (
            f"@echo off\n"
            f"cd /d \"{PROJECT_ROOT}\"\n"
            f"\"{sys.executable}\" -m dqt\n"
            f"pause\n"  # Keeps terminal open if there is an error
        )
    else:
        script_contents = (
            f"#!/bin/bash\n"
            f"cd \"{PROJECT_ROOT}\"\n"
            f"\"{sys.executable}\" -m dqt\n"
        )

    with open(path, "w", encoding="utf-8") as f:
        f.write(script_contents)


def make_executable(path: Path) -> None:
    """Applies executable permissions on Unix systems (macOS/Linux)."""
    if sys.platform != "win32":
        os.chmod(path, 0o755)


def add_os_extension(name: str) -> str:
    """Returns the correct executable shortcut extension based on OS."""
    path = Path(name)

    if sys.platform == "darwin":
        return str(path.with_suffix(".command"))
    elif sys.platform == "win32":
        return str(path.with_suffix(".cmd"))
    else:
        return str(path.with_suffix(".sh"))


def main() -> None:
    """Create an executable shell script as a shortcut to start DQT."""
    raw_name = input("\nShortcut file name (e.g., launch_dqt): ").strip()
    filename = add_os_extension(raw_name)

    while True:
        d = input(
            f"Directory to create shortcut in (e.g. Desktop): "
            f"{Path.home()}{os.sep}"
        ).strip()
        destdir = Path.home() / d

        if destdir.is_dir():
            dest = destdir / filename
            break
        print("\nERROR: Directory not found. Try again\n")

    print(f"\nCreating script at: {dest}")

    print("Writing contents...")
    write(dest)

    print("Setting permissions...")
    make_executable(dest)

    print("\n✅ \033[32m\033[1mSuccess!\033[0m")
    print(f"Executable shortcut created at: {dest}")
    print(
        "\nYou can now start DQT by simply double-clicking this shortcut file "
        "instead of running it manually from your terminal."
    )


if __name__ == "__main__":
    main()
