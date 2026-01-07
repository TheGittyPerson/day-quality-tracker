import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from day_quality_tracker import DayQualityTracker


class DQTJSON:
    """A class to manage Day Quality Tracker JSON contents handling."""

    def __init__(self, dqt: DayQualityTracker):
        self.dqt = dqt
        self.date_format = self.dqt.date_format

        self.parent_dir = Path(__file__).resolve().parent
        self.json_name = 'dq_logs.json'
        self.json_name_pre5 = 'dq_ratings.json'
        self.json_path = self.parent_dir / self.json_name
        self.json_path_pre5 = self.parent_dir / self.json_name_pre5

        self.saved_ratings = self._load_json()

    def touch(self) -> None:
        """Check if JSON file exists."""
        if not self.json_path.exists():
            if self.json_path_pre5.exists():
                self.json_path_pre5.rename(self.json_name)
            else:
                self.json_path.touch()

    def update(self):
        """Dump updated `saved_ratings` dict to JSON file."""
        if not self.json_path.exists():
            self.json_path.touch()

        with open(self.json_path, 'w') as json_file:
            json.dump(self.saved_ratings, json_file, indent=4)

    def _load_json(self) -> dict:
        """Load JSON file contents and return dict."""
        if not self.json_path.exists():
            self.json_path.touch()

        if not self.json_path.read_text():
            return {}
        with open(self.json_path, 'r') as file:
            contents = json.load(file)
        return {
            k: float(v) for k, v in contents.items()
        }
