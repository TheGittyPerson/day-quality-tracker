__name__ = "dqt"
__package__ = "dqt"
__master_version__ = 5
__version__ = "v1.4.1"
__author__ = "Morpheus"

_REPO_URL = "https://github.com/TheGittyPerson/day-quality-tracker"

from .tracker import Tracker
from .manager import Manager
from .json_manager import JSONManager
from .graph import Graph
from .stats import Stats
from .settings_manager import SettingsManager
from . import ui_utils, shortcut_creator

__all__ = [
    "Tracker", "Manager", "JSONManager", "Graph", "Stats", "SettingsManager"
]
