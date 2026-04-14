import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tracker import Tracker


class SettingsManager:
    """A class to manage the settings file."""
    
    def __init__(self, dqt: Tracker):
        """Initialize the settings manager."""
        self.dqt = dqt
        