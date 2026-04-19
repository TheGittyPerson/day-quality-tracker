import os
import sys
import subprocess
from pathlib import Path

from ui_utils import err


class SettingsManager:
    """A class to manage the settings file."""
    
    def __init__(self):
        """Initialize the settings manager."""
        self.filename: str = 'settings.py'
        rootdir: Path = Path(__file__).resolve().parent.parent
        self.settings_path: Path = rootdir / Path(self.filename)
        
    def open_file(self):
        """Open the settings file."""
        if not self.settings_path.exists():
            err("Could not find settings file.")
            return
        
        try:
            if sys.platform == 'win32':
                os.startfile(self.settings_path)  # Windows
            elif sys.platform == 'darwin':
                result = subprocess.call(['open', self.settings_path])
                if result != 0:
                    raise RuntimeError(
                        f"`open` exited with status code {result}"
                    )
            elif sys.platform.startswith('linux'):
                result = subprocess.call(['xdg-open', self.settings_path])
                if result != 0:
                    raise RuntimeError(
                        f"`xdg-open` exited with status code {result}"
                    )
            else:
                print("\nYou will have to open the file manually. "
                      f"\nPath: {self.settings_path}")
                print(
                    "(Incompatible OS: unable to open the file with the "
                    "program)"
                )
                return
        except (OSError, RuntimeError) as exc:
            err("Could not open settings file automatically.")
            print(f"\nPath: {self.settings_path}")
            print(exc)
            return

        print(f"File opened in a new window.")
        print("Remember to save changes before closing the file!")
        print("(Rerun the program for changes to take effect)")
