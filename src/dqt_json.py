import json
import sys
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import TYPE_CHECKING

from src.ui_utils import confirm, cont_on_enter, err, log_saved, print_wrapped
from src.styletext import StyleText as Txt

if TYPE_CHECKING:
    from tracker import Tracker

_UNSET: object = object()
_today: datetime = datetime.today()


class DQTJSON:
    """A class to manage Day Quality Tracker JSON contents handling."""
    
    def __init__(self, dqt: Tracker):
        """Initialize attributes."""
        self.dqt: Tracker = dqt
        
        self.filedirname: str = 'data'
        self.rootdir: Path = Path(__file__).resolve().parent.parent
        self.filedirpath: Path = self.rootdir / self.filedirname
        self.filename: str = 'dq_logs.json'
        self.filepath: Path = self.filedirpath / self.filename
        self._filename_pre5: str = 'dq_ratings.json'
        self._filepath_pre5: Path = self.rootdir / self._filename_pre5
        
        self.rating_kyname: str = 'rating'
        self.memory_kyname: str = 'memory'
        
        self.json_indent: int = 4
        
        self._touch()
        
        self.logs: dict = self._load_json()
    
    def update(self,
               date: str = None,
               rating: float | None = _UNSET,
               memory: str = _UNSET) -> None:
        """Dump updated logs to JSON file.

        Update with new rating and memory values if provided before dumping.
        Attempted creation of new items will raise a KeyError. Use `add()`
        instead to add a new log.
        """
        if date is None:
            if rating is not _UNSET or memory is not _UNSET:
                raise ValueError("Missing date argument")
            return
        if date not in self.logs:
            raise KeyError(f"Date '{date}' not found")
        if rating is not _UNSET:
            self.logs[date][self.rating_kyname] = rating
        if memory is not _UNSET:
            self.logs[date][self.memory_kyname] = memory
        
        self._dump()
    
    def add(self,
            date: str,
            rating: float | None = None,
            memory: str = '') -> None:
        """Update logs with new log and dump to JSON file.

        Attempted rewrite of previous items will raise a KeyError.
        Use `update()` instead to add a new log.

        It is recommended to explicitly provide both rating and memory
        arguments, even if it is equal to the default value.
        """
        if date in self.logs:
            raise KeyError(f"Log with date '{date}' already exists.")
        
        self.logs[date] = {
            self.rating_kyname: rating,
            self.memory_kyname: memory
        }
        
        self._dump()
    
    def get_rating(self, date: str) -> float | None:
        """Return rating for given date."""
        return self.logs[date][self.rating_kyname]
    
    def get_memory(self, date: str) -> str:
        """Return memory entry for given date."""
        return self.logs[date][self.memory_kyname]
    
    def today_rated(self) -> bool:
        """Check if a rating has been provided for today."""
        today = _today.strftime(self.dqt.date_format)
        return today in self.logs
    
    def print_log(self,
                  date: str = _UNSET,
                  rating: float | None = _UNSET,
                  memory: str = _UNSET,
                  linewrap_memory: bool = False) -> None:
        """Print a formatted log, and represent 'empty' values with text.

        Null (None) ratings are printed as "[No rating]".
        Empty memory entries (empty str) are printed as "[Empty entry]".

        If date is unfilled, it will not be printed.
        If date == 'today', "Today's log:" will be printed at the start.
        Else, f"Date: {date}" will be printed.
        """
        
        # ----- Date -----
        if date is not _UNSET:
            if date == 'today':
                print(Txt("\nToday's log:").bold().yellow())
            else:
                print(Txt(f"Date: ").bold() + date)
        
        # ----- Rating -----
        if rating is not _UNSET:
            if rating is None:
                print(Txt("Rating: ").bold() + "-")
            else:
                print(
                    f"{Txt("Rating:").bold()}",
                    f"{rating:g}/{self.dqt.max_rating}"
                )
        
        # ----- Memory -----
        if memory is not _UNSET:
            if memory:
                print(Txt("Memory:").bold())
                if linewrap_memory:
                    print_wrapped(memory, self.dqt.linewrap_maxcol)
                else:
                    print(memory)
            else:
                print(Txt("Memory: ").bold() + "-")
    
    def print_logs_to_stdout(self) -> None:
        """Print last 30 saved logs.

        The user can choose whether to show the rest of the logs.
        """
        
        def _loop_print(items: list):
            print("\n* —————————————————————————————— *")
            for date, log in items:
                print()
                self.print_log(
                    date=date,
                    rating=log[self.rating_kyname],
                    memory=log[self.memory_kyname],
                    linewrap_memory=True,
                )
            print("\n* —————————————————————————————— *")
        
        print("\nLast 30 logs, most recent last:")
        
        if not self.logs:
            print("\n[No logs found]")
            return
        
        # Convert dictionary items to a list of tuples
        items_list = list(self.logs.items())
        # Get the last 30 items or all items if less than 30
        last_30_items = items_list[-30:]
        
        _loop_print(last_30_items)
        
        if len(items_list) > 30:
            if not confirm("Show the rest of the logs?"):
                return
            
            items_until_last_30th = items_list[:-30]
            
            _loop_print(items_until_last_30th)
        
        cont_on_enter()
    
    def open_json_file(self) -> None:
        """Open the JSON file in the default system application."""
        print("\nOpening JSON file...")
        
        if sys.platform == "win32":
            os.startfile(self.filepath)  # Windows
        elif sys.platform == "darwin":
            subprocess.call(["open", self.filepath])  # macOS
        elif sys.platform.startswith("linux"):
            subprocess.call(["xdg-open", self.filepath])  # Linux
        else:
            print("\nYou will have to open the file manually. "
                  f"\nPath: {self.filepath}")
            print("(Incompatible OS: unable to open the file with the program)")
            return
        
        print(f"File opened in a new window.")
        print("Remember to save changes before closing the file!")
        print("(Rerun the program for changes to take effect)")
        
    def backup_json_file(self) -> None:
        """Create a backup copy of the JSON file in a chosen directory."""
        print_wrapped(
            "\nSometimes an error can occur while the program is running, "
            "which can corrupt or accidentally erase the JSON file where your "
            "logs are stored."
            "\nIt is good practice to back up your logs every once in a while.",
            self.dqt.linewrap_maxcol
        )
        
        if not self._memory_matches_file():
            err(
                "Your logs saved in runtime memory do not match those in the "
                "JSON file.")
            if not confirm("Are you sure you want to continue?"):
                print_wrapped(
                    "Ensure all changes are saved to the JSON file before "
                    "creating a backup file.", self.dqt.linewrap_maxcol)
                print_wrapped(
                    "If you have made changes to the JSON file manually, "
                    "please rerun the program first.", self.dqt.linewrap_maxcol
                )
                return
                
        successful, dst_filepath = self._start_file_backup_process()
        if successful:
            log_saved(
                f"Backup created successfully at '{dst_filepath}'!"
            )
        
    def _start_file_backup_process(self) -> tuple[bool, str | None]:
        """Start the backup JSON prompting and file creation process.
        
        Return success.
        """
        dst = None
        while True:
            dirpath = self._prompt_dirpath(
                "Enter the directory path where you would like to create the "
                "backup file"
            )
            print(f"\nBackup will be saved to:\n{dirpath}")
            filename = self._prompt_filename(
                "Name the backup file "
                "\n(Tip: include a date or number for future reference)"
            )
            chosen_filepath = dirpath / filename
            if not confirm(
                f"Backup file will be created at '{chosen_filepath}'. Confirm?"
            ):
                continue
            
            print("\nCreating backup file...")
            try:
                dst = self._create_json_copy(chosen_filepath, exist_ok=False)
            except FileExistsError:
                if confirm(f"The filename '{filename}' already exists in the "
                           f"directory '{dirpath}'. Overwrite?"):
                    self._create_json_copy(chosen_filepath, exist_ok=True)
                    return True, dst
                continue
            except Exception as e:
                err(
                    "An error occurred while trying to create the backup "
                    "file: ",
                    f"Error message: {e}.",
                    "Try again."
                )
                return False, dst
            else:
                break
        return True, dst
    
    def _create_json_copy(self, target_path: Path, exist_ok: bool) -> str:
        """Create a copy of the JSON file in a chosen directory.
        
        Raise a FileExistsError if the target path already exists.
        """
        if not exist_ok and target_path.exists():
            raise FileExistsError
        return shutil.copy2(self.filepath, target_path)
    
    @staticmethod
    def _prompt_dirpath(prompt: str, from_home_dir: bool = True) -> Path:
        """Prompt and validate directory path input.
        
        If `from_home_dir` is True, the user's path input will be appended to
        the home directory. e.g. If the user inputs "Desktop", the final path
        will be Path("User/username/Desktop").
        """
        home_dir = Path.home() if from_home_dir else None
        while True:
            base = home_dir if from_home_dir else Path('/')
            if from_home_dir:
                dirpath = base / input(f"\n{prompt}: \n{base}").lstrip('/')
            else:
                dirpath = input(f"\n{prompt}: \n{base}")
            if not dirpath.is_dir():
                err(
                    f"Directory '{dirpath}' not found.",
                    "Try again."
                )
                continue
            break
        return dirpath
    
    def _prompt_filename(self, prompt: str) -> str:
        """Prompt and validate file name based on OS."""
        while True:
            filename = input(f"\n{prompt}: ").strip()
            if not filename:
                err("File name must not be empty.", "Try again.")
            if not filename.endswith('.json'):
                filename += '.json'
            
            for ch in self._invalid_filename_chars():
                if ch in filename:
                    err(
                        f"Invalid character '{ch}' in filename '{filename}'",
                        "Try again."
                    )
                    break
            else:
                return filename
    
    @staticmethod
    def _invalid_filename_chars() -> str:
        """Return a list of invalid filename characters based on OS."""
        if os.name == 'nt':  # Windows invalid characters
            invalid = '<>:"/\\|?*'
            # Control characters (0-31)
            invalid += ''.join([chr(i) for i in range(32)])
        else:  # POSIX (Linux, macOS) invalid characters
            invalid = '/\0'
        return invalid
    
    def _memory_matches_file(self, order_matters: bool = True) -> bool:
        """Return if the logs in `self.logs` matches those in the JSON file."""
        file_logs = self._load_raw_json()
        if order_matters:
            return file_logs == self.logs
        return set(file_logs.items()) == set(self.logs.items())
    
    def _touch(self) -> None:
        """Check if JSON file exists, create if not."""
        if not self.filedirpath.exists():
            print(f"\nCreating `{self.filedirname}` directory...")
            self.filedirpath.mkdir()
            print("Success!")
        if not self.filepath.exists():
            if self._filepath_pre5.exists():
                print(f"\nRenaming pre-DQT-5 JSON file...")
                self._filepath_pre5.rename(self.filename)
                print("Moving file...")
                shutil.move(self.filename, self.filedirpath)
                print("Success!")
            else:
                print(f"\nCreating `{self.filename}`...")
                self.filepath.touch()
                print("Success!")
                
    def _load_json(self) -> dict:
        """Load, validate, and normalize JSON log data."""
        contents = self._load_raw_json()
        if not contents:
            return {}
        return self._validate_and_normalize_logs(contents)
    
    def _load_raw_json(self) -> dict:
        """Load raw JSON contents from disk.

        Returns an empty dict if the file does not exist or is empty.
        """
        if not self.filepath.exists():
            return {}
        
        text = self.filepath.read_text().strip()
        if not text:
            return {}
        
        with open(self.filepath, 'r') as file:
            return json.load(file)
    
    def _validate_and_normalize_logs(
            self,
            contents: dict) -> dict[str, dict[str, float | None | str]]:
        """Validate and normalize raw log data.

        - Ensures dates are increasing
        - Ensures rating exists
        - Auto-fills missing memory entries (optional)
        """
        prev_date = None
        validated: dict[str, dict[str, float | None | str]] = {}
        updated = False
        
        for date, value in contents.items():
            
            # ---------- Validate date order ----------
            if prev_date is not None:
                prev_d = datetime.strptime(prev_date, self.dqt.date_format)
                d = datetime.strptime(date, self.dqt.date_format)
                diff = (d - prev_d).days
                if diff < 0:
                    raise ValueError(
                        f"Date '{date}' is older than previous date "
                        f"'{prev_date}'"
                    )
                if diff == 0:
                    raise ValueError(
                        f"Date '{prev_date}' is repeated"
                    )
            
            prev_date = date
            
            # Format:
            # {
            #     "YYYY-MM-DD": {
            #         "rating": 10,
            #         "memory": "This is a memory entry."
            #     }
            # }
            if isinstance(value, dict):
                try:
                    raw_rating = value[self.rating_kyname]
                except KeyError:
                    if not self.dqt.autofill_json:
                        raise KeyError(
                            f"'{self.rating_kyname}' key not found for date "
                            f"'{date}'")
                    raw_rating = None
                    updated = True
                rating = None if raw_rating is None else float(raw_rating)
                try:
                    memory = value[self.memory_kyname]
                except KeyError:
                    if not self.dqt.autofill_json:
                        raise KeyError(
                            f"'{self.memory_kyname}' key not found for date "
                            f"'{date}'")
                    memory = ''
                    updated = True
                
                validated[date] = {
                    self.rating_kyname: rating,
                    self.memory_kyname: memory
                }
                
                continue
            
            else:
                raise ValueError(
                    f"Invalid log format for date '{date}'; "
                    f"must be a valid key-value pair"
                )
        
        if updated:
            self._dump(validated)
        
        return validated
    
    def _dump(self,
              logs: dict[str, dict[str, float | None | str]] = None) -> None:
        """Dump logs to the JSON file.

        If `logs` is None (default), dump the contents of `self.logs`.
        If a logs dict is provided, dump that dict instead.
        
        To prevent data loss, dumping is aborted if the JSON file already
        contains data and the logs to be dumped are empty.
        """
        logs_to_dump = self.logs if logs is None else logs
        raw_json = self._load_raw_json()
        
        # Prevent overwriting existing data with an empty logs dict
        if raw_json and not logs_to_dump:
            print(
                Txt(
                    "\n(The program tried to save an empty logs dict. Logs "
                    "were not saved to prevent data loss. Consider creating a "
                    "copy of your JSON file now, just in case.)"
                ).dim()
            )
            return
        
        with open(self.filepath, "w") as file:
            json.dump(
                logs_to_dump,
                file,
                indent=self.json_indent
            )
    
    def no_logs(self, check_file: bool = True) -> bool:
        """Determine whether there are no logs available.

        Return True if `self.logs` is empty and, if `check_file` is True,
        the JSON log file is also empty.

        If `check_file` is True and `self.logs` is empty but the JSON file
        contains data, the user is prompted to load the data. If the user
        agrees, `self.logs` is populated and False is returned.
        """
        # If only checking in-memory logs
        if not check_file:
            return not self.logs
        
        # If in-memory logs already exist, logs are not empty
        if self.logs:
            return False
        
        # In-memory logs are empty; check the JSON file
        raw_json = self._load_raw_json()
        
        if not raw_json:
            return True
        
        # JSON has data but logs are not loaded
        if confirm(
            "There seems to be unloaded data from the JSON file. "
            "Load now?"
        ):
            self.logs = self._load_json()
            return False
        
        return True
    
    def no_previous_logs(self) -> bool:
        """Return whether there are no previous logs (other than today's)."""
        if len(self.logs) <= 1:
            return True
        return False
    