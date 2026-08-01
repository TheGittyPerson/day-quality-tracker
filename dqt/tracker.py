import webbrowser
from datetime import datetime
from types import NoneType

from . import RELEASE_NUM, SEMVER, _REPO_URL
from .manager import Manager
from .json_manager import JSONManager
from .graph import Graph
from .stats import Stats
from .settings_manager import SettingsManager
from .ui_utils import *
from . import shortcut_creator

# Today's date is initialized at the start and used statically to prevent
# confusion if the program is run across midnight
_today: datetime = datetime.today()


class Tracker:
    """Track and visualize day quality ratings in a graph.
    
    This class controls the main menu algorithm/logic.
    """
    
    _CONFIG_KEYS: dict[str, type | tuple[type, ...]] = {
        "min_rating": int,
        "max_rating": int,
        "rating_inp_dp": int,
        "linewrap_maxcol": int,
        "date_format": str,
        "date_format_print": str,
        "clock_format_12": bool,
        "delete_mem_edit_files_after": (int, NoneType),
        "backup_dir_path": (str, NoneType),
        "autofill_json": bool,
    }
    
    def __init__(self):
        """Load saved data, initialize settings and Graph instance."""
        # Initialize settings
        self.min_rating: int = 1  # 1 recommended
        self.max_rating: int = 20  # Even number recommended
        self.rating_inp_dp: int = 2
        self.linewrap_maxcol: int = 70
        
        self.date_format: str = "%d-%m-%Y"
        self.date_format_print: str = "DD-MM-YYYY"
        self.clock_format_12: bool = True
        self.delete_mem_edit_files_after: int | None = 7
        self.backup_dir_path: str | None = None
        self.autofill_json: bool = True
        
        try:
            self.json: JSONManager = JSONManager(self)
        except ValueError as e:
            err(
                f"Something's wrong with the JSON file...",
                f"\"{e}.\"",
                "Please correct the file before starting the program.",
                pause=False
            )
            raise SystemExit()
        
        self.graph: Graph = Graph(self)
        self.manager: Manager = Manager(self)
        self.stats: Stats = Stats(self)
        self.settings: SettingsManager = SettingsManager()

    @property
    def neutral_rating(self) -> int:
        """The neutral, baseline or "middle" rating.
        
        Derived from the floor-division half of ``max_rating``.
        Only rounds down.
        """
        return (self.min_rating + self.max_rating) // 2
    
    def run(self) -> None:
        """Run Day Quality Tracker."""
        self._print_header()

        self.manager.handle_logs_entry()
        
        while True:
            print("\n*❖* —————————————————————————————— *❖*")
            print(
                f"\n🏠 {BOL}{UDL}{BLU}MAIN MENU{RST} " +
                bol("— choose what to do:")
            )

            today_logged = self.json.today_logged()
            t = (f"1) 📝 {"Edit" if today_logged else "Write"} "
                 f"[T]oday's log{"..." if today_logged else ""}")

            match menu(
                t,  # 1) Write/Edit [T]oday's log...
                "2) 🕗 Edit [P]revious log...",
                "3) 📈 View ratings [G]raph",
                "4) 📊 See [S]tats",
                "5) 📂 View [L]ogs...",
                "6) 🔧 [O]pen settings",
                "7) 💾 [B]ack up logs...",
                "8) [M]ore...",
                "9) ⎋ E[x]it",
                prompt=None
            ):

                case "1" | "t":
                    if not self.json.today_logged():
                        if self.json.logs_missed():
                            msg = warning(
                                "\nWriting today's log means you will have "
                                "to enter your missed logs manually in the "
                                "JSON file later.", "Confirm?"
                            )
                            if not confirm(msg):
                                print("\nYou can enter your missed logs by "
                                      "rerunning the program.")
                                continue
                        else:
                            print(bol("\nWriting a new log for today."))

                        self.manager.input_todays_log()
                        continue
                    
                    print(bol("\nToday's log:"))
                    today = _today.strftime(self.date_format)
                    self.json.print_log(
                        date=today,
                        rating=self.json.get_rating(today),
                        memory=self.json.get_memory(today),
                    )

                    match menu(
                        "1) Edit [R]ating",
                        "2) Edit [M]emory entry",
                        "3) Edit [B]oth",
                        "4) [C]ancel -> Main menu",
                    ):
                        case "1" | "r":
                            self.manager.change_todays_rating()
                        case "2" | "m":
                            self.manager.change_todays_memory()
                        case "3" | "b":
                            self.manager.change_todays_rating()
                            self.manager.change_todays_memory()
                        case "4" | "c":
                            continue

                case "2" | "p":
                    if self.json.no_logs():
                        err("You haven't entered any logs yet!")
                        continue
                    if self.json.no_previous_logs():
                        err("You haven't written any previous logs yet other "
                            "than for today!")
                        continue
                    while True:
                        selected_d = self.manager.prompt_date()
                        print(bol("\nSelected log:"))
                        self.json.print_log(
                            date=selected_d,
                            rating=self.json.get_rating(selected_d),
                            memory=self.json.get_memory(selected_d),
                        )
                        
                        match menu(
                            "1) Edit [R]ating",
                            "2) Edit [M]emory entry",
                            "3) Edit [B]oth",
                            "4) Reselect [D]ate",
                            "5) [C]ancel -> Main menu",
                        ):
                            case "1" | "r":
                                self.manager.change_previous_rating(
                                    selected_d
                                )
                            case "2" | "m":
                                self.manager.change_previous_memory(
                                    selected_d
                                )
                            case "3" | "b":
                                self.manager.change_previous_rating(
                                    selected_d
                                )
                                self.manager.change_previous_memory(
                                    selected_d
                                )
                            case "4" | "d":
                                continue
                            case "5" | "c":
                                break
                        break

                case "3" | "g":
                    if self.json.no_logs():
                        err("You haven't entered any logs yet!")
                        continue
                    self.graph.view_ratings_graph()
                    cont_on_enter()
                
                case "4" | "s":
                    self.stats.show_stats()
                    cont_on_enter()
                
                case "5" | "l":
                    match menu(
                        "1) Search by [D]ate",
                        "2) Print [A]ll logs",
                        "3) Open JSON [F]ile in default viewer/editor",
                        "4) [C]ancel -> Main menu",
                    ):
                        case "1" | "d":
                            self.json.search_logs_by_date()
                        case "2" | "a":
                            self.json.print_all_logs()
                            # cont_on_enter called in method. Don't move here.
                        case "3" | "f":
                            self.json.open_json_file()
                            cont_on_enter()
                        case "4" | "c":
                            continue

                case "6" | "o":
                    self.settings.open_file()
                    cont_on_enter()

                case "7" | "b":
                    if self.json.no_logs():
                        err("You haven't entered any logs yet!")
                        continue
                    self.json.backup_json_file()

                case "8" | "m":
                    match menu(
                        "1) 🔗 Create [D]esktop shortcut",
                        "2) 📥 [I]mport logs...",
                        "3) 😻 [V]isit project on GitHub",
                        "4) [C]ancel -> Main menu",
                        prompt="More..."
                    ):
                        case "1" | "d":
                            shortcut_creator.main()
                            # cont on enter in function
                        case "2" | "i":
                            self.json.import_logs()
                        case "3" | "v":
                            success = webbrowser.open(_REPO_URL)
                            if not success:
                                err("Couldn't open webpage.",
                                    "Try pasting this URL in your browser "
                                    f"manually: \n\t{_REPO_URL}")
                                cont_on_enter()
                        case "4" | "c":
                            continue

                case "9" | "x":
                    print("\n*⎋* —————————————————————————————— *⎋*")
                    print("\nBye!")
                    raise SystemExit()

    @staticmethod
    def _print_header() -> None:
        title = f"*--- 📆 Day Quality Tracker {RELEASE_NUM}! 📝 ---*"
        print(bol(ylw(f"\n{title}")))
        semver_str = "~~~ " + SEMVER + " ~~~"
        print(dim(f"{semver_str:^{len(title) + 2}}"))
    
    def configure(self, **configs: int | str | bool | None) -> None:
        """Update configuration options via keyword arguments.

        Must be called before `run()`.
        Raises:
            ValueError: Invalid configuration option
            TypeError: Incorrect type
        """
        for config_name, value in configs.items():
            if config_name not in self._CONFIG_KEYS:
                raise ValueError(
                    f"Invalid configuration option: '{config_name}'"
                )
            expected = self._CONFIG_KEYS[config_name]
            if not isinstance(value, expected):
                expected_name = (
                    expected.__name__
                    if isinstance(expected, type)
                    else " or ".join(t.__name__ for t in expected)
                )
                raise TypeError(
                    f"Expected {expected_name} for configuration "
                    f"'{config_name}', got {type(value).__name__} instead"
                )
            setattr(self, config_name, value)
