import os
import sys
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tracker import Tracker


class SettingsManager:
    """A class to manage the settings file."""
    
    def __init__(self, dqt: Tracker):
        """Initialize the settings manager."""
        self.dqt = dqt

        self.filename: str = 'settings.py'
        rootdir: Path = Path(__file__).resolve().parent.parent
        self.settings_path: Path = rootdir / Path(self.filename)
        
    def open_file(self):
        """Open the settings file."""
        if sys.platform == "win32":
            os.startfile(self.settings_path)  # Windows
        elif sys.platform == "darwin":
            subprocess.call(["open", self.settings_path])  # macOS
        elif sys.platform.startswith("linux"):
            subprocess.call(["xdg-open", self.settings_path])  # Linux
        else:
            print("\nYou will have to open the file manually. "
                  f"\nPath: {self.settings_path}")
            print("(Incompatible OS: unable to open the file with the program)")
            return

        print(f"File opened in a new window.")
        print("Remember to save changes before closing the file!")
        print("(Rerun the program for changes to take effect)")
