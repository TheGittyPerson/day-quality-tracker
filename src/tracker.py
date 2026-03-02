from datetime import datetime
from types import NoneType

from src.dqt_json import DQTJSON
from src.manager import Manager
from src.graph import Graph
from src.stats import Stats
from src.ui_utils import cont_on_enter, err, invalid_choice, menu
from src.styletext import StyleText as Txt

_UNSET: object = object()
_today: datetime = datetime.today()


class Tracker:
    """Track and visualize day quality ratings in a graph."""
    
    RELEASE_NUM: int = 5
    SEMVER: str = 'v1.0.1'
    
    _CONFIG_KEYS: dict[str, type | tuple[type, ...]] = {
        'min_time': int,
        'min_rating': int,
        'max_rating': int,
        'rating_inp_dp': int,
        'linewrap_maxcol': int,
        'date_format': str,
        'date_format_print': str,
        'clock_format_12': bool,
        'enable_ansi': (bool, NoneType),
        'autofill_json': bool,
    }
    
    def __init__(self):
        """Load saved data, initialize settings and Graph instance."""
        # Initialize settings
        self.min_time: int = 20  # Earliest hour the of day to enter rating
        self.min_rating: int = 1  # 1 recommended
        self.max_rating: int = 20  # Even number recommended
        self.neutral_rating: int = round(self.max_rating / 2)
        self.rating_inp_dp: int = 2
        self.linewrap_maxcol: int = 70
        
        self.date_format: str = '%Y-%m-%d'
        self.date_format_print: str = "YYYY-MM-DD"
        self.clock_format_12: bool = True
        self.enable_ansi: bool | None = False
        self.autofill_json: bool = True
        
        try:
            self.json: DQTJSON = DQTJSON(self)
        except ValueError as e:
            err(
                f"Something's wrong with '{self.json.filename}'...",
                f"\"{e}.\"",
                "Please correct the file before starting the program.",
                pause=False
            )
            raise SystemExit()
        
        self.graph: Graph = Graph(self)
        self.manager: Manager = Manager(self)
        self.stats: Stats = Stats(self)
    
    def run(self) -> None:
        """Run Day Quality Tracker."""
        Txt.set_ansi(self.enable_ansi)
        
        title = f"*--- 📆 Day Quality Tracker {self.RELEASE_NUM}! 📈 ---*"
        print(
            Txt(
                f"\n{title}"
            ).bold().yellow()
        )
        semver_str = "~~~ " + self.SEMVER + " ~~~"
        print(Txt(f"{semver_str:^{len(title) + 2}}").dim())
        
        choice = self.manager.handle_missing_logs()
        
        if choice in ['1', '3', None]:
            if not self.json.today_rated():
                self.manager.input_todays_log()
        
        while True:
            print("\n*❖* —————————————————————————————— *❖*")
            print(
                f"🏠 {Txt("MAIN MENU").blue().underline().bold()} "
                f"{Txt("— choose what to do:").bold()}"
            )
            opts = menu(
                "1) 📈 View ratings [G]raph",
                "2) 📝 Edit [T]oday's log...",
                "3) 🕗 Edit [P]revious log...",
                "4) 📊 See [S]tats",
                "5) 📂 View [A]ll logs...",
                "6) 💾 [B]ack up logs...",
                "7) E[x]it",
                title=None
            )
            
            match input("> ").lower().strip():
                case '1' | 'g':
                    if self.json.no_logs():
                        err("You haven't entered any logs yet!")
                        continue
                    self.graph.view_ratings_graph()
                    if not self.graph.graph_show_block:
                        cont_on_enter()
                        self.graph.close()
                    else:
                        print("\nGraph closed.")
                
                case '2' | 't':
                    if not self.json.today_rated():
                        err("You haven't entered today's log yet!")
                        continue
                    
                    print(Txt("\nToday's log:").bold())
                    today = _today.strftime(self.date_format)
                    self.json.print_log(
                        date=today,
                        rating=self.json.get_rating(today),
                        memory=self.json.get_memory(today),
                    )
                    
                    while True:
                        opts = menu(
                            "1) Edit [R]ating",
                            "2) Edit [M]emory entry",
                            "3) Edit [B]oth",
                            "4) [C]ancel -> Main menu",
                        )
                        
                        match input("> ").strip().lower():
                            case '1' | 'r':
                                self.manager.change_todays_rating()
                            case '2' | 'm':
                                self.manager.change_todays_memory()
                            case '3' | 'b':
                                self.manager.change_todays_rating()
                                self.manager.change_todays_memory()
                            case '4' | 'c':
                                break
                            case _:
                                invalid_choice(opts)
                                continue
                        break
                
                case '3' | 'p':
                    if self.json.no_logs():
                        err("You haven't entered any logs yet!")
                        continue
                    if self.json.no_previous_logs():
                        err("You haven't entered any previous logs yet other "
                            "than today's!")
                        continue
                    while True:
                        selected_d = self.manager.prompt_prev_date()
                        print(Txt("\nSelected log:").bold())
                        self.json.print_log(
                            date=selected_d,
                            rating=self.json.get_rating(selected_d),
                            memory=self.json.get_memory(selected_d),
                        )
                        
                        while True:
                            opts = menu(
                                "1) Edit [R]ating",
                                "2) Edit [M]emory entry",
                                "3) Edit [B]oth",
                                "4) Reselect [D]ate",
                                "5) [C]ancel -> Main menu",
                            )
                            
                            choice = input("> ").strip().lower()
                            match choice:
                                case '1' | 'r':
                                    self.manager.change_previous_rating(
                                        selected_d
                                    )
                                case '2' | 'm':
                                    self.manager.change_previous_memory(
                                        selected_d
                                    )
                                case '3' | 'b':
                                    self.manager.change_previous_rating(
                                        selected_d
                                    )
                                    self.manager.change_previous_memory(
                                        selected_d
                                    )
                                case '4' | 'd':
                                    break
                                case '5' | 'c':
                                    break
                                case _:
                                    invalid_choice(opts)
                                    continue
                            break
                        
                        if choice in ['4', 'd']:
                            continue
                        break
                
                case '4' | 's':
                    self.stats.show_stats()
                    cont_on_enter()
                
                case '5' | 'a':
                    while True:
                        opts = menu(
                            "1) [P]rint logs to standard output",
                            "2) [O]pen JSON file in default viewer/editor",
                            "3) [C]ancel -> Main menu",
                        )
                        
                        choice = input("> ").strip().lower()
                        match choice:
                            case '1' | 'p':
                                self.json.print_logs_to_stdout()
                            case '2' | 'o':
                                self.json.open_json_file()
                                cont_on_enter()
                            case '3' | 'c':
                                break
                            case _:
                                invalid_choice(opts)
                                continue
                        break
                
                case '6' | 'b':
                    if self.json.no_logs():
                        err("You haven't entered any logs yet!")
                        continue
                    self.json.backup_json_file()
                
                case '7' | 'x':
                    print("\n*⎋* —————————————————————————————— *⎋*")
                    print("\nBye!")
                    raise SystemExit()
                
                case _:
                    invalid_choice(opts)
    
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
