from textwrap import dedent
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from dqt.json_manager import JSONManager
from dqt.ui_utils import (
    confirm,
    err,
    invalid_choice,
    log_saved,
    menu,
    print_wrapped
)
from dqt.styletext import StyleText as Txt

if TYPE_CHECKING:
    from tracker import Tracker

_today: datetime = datetime.today()


class Manager:
    """A class to handle user interactions and main menu options."""
    
    def __init__(self, dqt: Tracker):
        self.dqt: Tracker = dqt
        self.json: JSONManager = dqt.json
        
        self.memory_edit_placeholder: str = '{}'
        self.memory_edit_length_diff_alert_threshold: int = 200
    
    def handle_missing_logs(self) -> str | None:
        """Check if any previous days are missing ratings.

        User chooses to enter missing ratings or not. If they do,
        loop through each missing date and prompt rating.
        Return the option the user chose if missed prior dates.
        """
        if self.json.no_logs():  # Ignore for first-time runs (empty dict)
            return None
        
        last_date_str: str = max(self.dqt.json.logs.keys())
        last_date = datetime.strptime(
            last_date_str, self.dqt.date_format
        ).date()
        days_since_last = (_today.date() - last_date).days
        
        if days_since_last <= 1:
            return None

        missing_logs_count = days_since_last - 1
        first_missed_date = last_date + timedelta(days=1)
        last_missed_date = _today.date() - timedelta(days=1)

        first_missed_date_str = first_missed_date.strftime(self.dqt.date_format)
        last_missed_date_str = last_missed_date.strftime(self.dqt.date_format)

        if missing_logs_count == 1:
            print(f"\nYou have 1 missing log for {first_missed_date_str}.")
        else:
            print(
                f"\nYou have {missing_logs_count} missing logs: "
                f"{first_missed_date_str} to {last_missed_date_str}."
            )
        
        while True:
            opts = menu(
                "1) Enter missing logs now",
                "2) Enter missing logs later -> Main menu",
                "3) Skip missing logs -> Enter today's log",
            )
            
            choice = input("> ").strip()
            
            match choice:
                
                case '1':
                    # Get list of missed dates
                    missed_dates = []
                    curr_loop_date = last_date + timedelta(days=1)
                    #                               Exclude today
                    while len(missed_dates) < days_since_last - 1:
                        missed_dates.append(curr_loop_date)
                        curr_loop_date += timedelta(days=1)
                    
                    for date in missed_dates:
                        rating = self._input_rating(
                            f"Enter your rating for {date} "
                            f"({self.dqt.min_rating}~{self.dqt.max_rating}, "
                            f"or '-' to skip): ",
                        )
                        
                        memory = self._input_memory(
                            "Enter a memory entry (leave blank to skip): "
                        )
                        
                        date_str = datetime.strftime(date, self.dqt.date_format)
                        
                        self.json.add(date_str, rating, memory)
                    
                    log_saved("Logs saved!")
                    
                    return choice
                
                case '2':
                    print_wrapped(
                        "\nRestart the program later to enter your missing "
                        "logs! (You can only enter today's log after "
                        "entering the missed logs, unless you choose to skip "
                        "them.)",
                        self.dqt.linewrap_maxcol
                    )
                    
                    return choice
                
                case '3':
                    print_wrapped(
                        "\nYou will have to enter the missed logs later "
                        f"manually in `{self.json.filename}`, unless you "
                        "don't enter today's log yet."
                        "\nYou can open the file by selecting:"
                        "\nMain menu -> 5) View [A]ll logs "
                        "-> 2) [O]pen JSON file in default viewer/editor"
                        "\nMake sure you save any changed before closing "
                        "the file.",
                        self.dqt.linewrap_maxcol
                    )
                    
                    return choice
                
                case _:
                    invalid_choice(opts, False)
                    continue
    
    def input_todays_log(self) -> None:
        """Get today's rating and memory entry if not entered yet.

        Reject if the specified earliest time to collect data has not
        passed yet.
        """
        print("\n*❖* —————————————————————————————— *❖*")
        if datetime.now().time().hour >= self.dqt.min_time:
            if not confirm("Would you like to enter today's log now?"):
                print("\nRerun the program later to enter your log!")
                return
            
            tdys_rating = self._input_rating(
                f"Rate your day from {self.dqt.min_rating} to "
                f"{self.dqt.max_rating}, {self.dqt.neutral_rating} being an "
                f"average day "
                f"\n(enter '-' to skip): "
            )
            
            tdys_memory = self._input_memory(
                f"Enter a memory entry; write a few sentences about your "
                f"day. \nLeave this blank to skip: "
            )
            
            if not tdys_memory:
                print(
                    "\nTo enter your memory entry later: "
                    "\nMain menu -> Edit today's/previous log -> Edit memory"
                )
            
            # Save data
            today = _today.strftime(self.dqt.date_format)
            self.json.add(today, tdys_rating, tdys_memory)
            log_saved()
        
        else:
            # Format time in 12-hour or 24-hour clock
            if self.dqt.clock_format_12:
                hour = self.dqt.min_time % 12 \
                    if self.dqt.min_time % 12 != 0 \
                    else 12
                suffix = 'AM' if self.dqt.min_time < 12 else 'PM'
                formatted_time = f"{hour} {suffix}"
            else:
                formatted_time = str(self.dqt.min_time)
            
            print(f"\nYou can only input today's log after {formatted_time}.")
            print("\nCome back later to enter today's log!")
    
    def change_todays_rating(self) -> None:
        """Prompt the user to change today's rating."""
        self._change_data('today', self.json.rating_kyname)
    
    def change_todays_memory(self) -> None:
        """Prompt the user to change today's memory entry."""
        self._change_data('today', self.json.memory_kyname)
    
    def prompt_prev_date(self) -> str:
        """Prompt the user to enter a previous date."""
        selected_date = ''
        while True:
            inp = input("\nEnter the number of days ago or exact date "
                        f"('{self.dqt.date_format_print}'): ").strip()
            
            # If number of days ago specified, get date
            if inp.isdigit():
                inp = int(inp)
                selected_date = _today - timedelta(days=inp)
                selected_date = selected_date.strftime(self.dqt.date_format)
                print(Txt(f"Date selected: {selected_date}").bold())
            
            # Else, validate date str
            else:
                try:
                    datetime.strptime(inp, self.dqt.date_format)
                except ValueError:
                    err("Enter either a valid date in the format "
                        f"{self.dqt.date_format_print} or a positive "
                        "integer.")
                    continue
                selected_date = inp
            
            # Check if date exists in saved ratings
            try:
                self.json.logs[selected_date]
            except KeyError:
                err(
                    "Rating for specified date not found.",
                    "Ensure you have already entered a "
                    "rating for that date.",
                    "\nTry again."
                )
                continue
            
            break
        return selected_date
    
    def change_previous_rating(self, selected_date: str) -> None:
        """Prompt the user to change a rating from a previous day."""
        self._change_data(selected_date, self.json.rating_kyname)
    
    def change_previous_memory(self, selected_date: str) -> None:
        """Prompt the user to change a memory entry from a previous day."""
        self._change_data(selected_date, self.json.memory_kyname)
    
    def _change_data(self, selected_date: str, changing: str) -> None:
        """Change data for the selected date and update JSON.
        
        If the specified date is the string 'today', today's date (or rather,
        the date specified in the global variable `_today`, which is evaluated
        at the start of runtime) will be used.
        
        Parameter `changing` must be either the rating or memory key name
        specified in JSONManager (raises a ValueError otherwise).
        """
        if changing not in (self.json.rating_kyname, self.json.memory_kyname):
            raise ValueError(
                f"'changing' argument must be '{self.json.rating_kyname}' or "
                f"'{self.json.memory_kyname}'"
            )
        
        if selected_date == 'today':
            selected_date = _today.strftime(self.dqt.date_format)
        
        if changing == self.json.rating_kyname:
            self._change_rating_for_date(selected_date)
        else:
            self._change_memory_for_date(selected_date)
    
    def _change_rating_for_date(self, date: str) -> None:
        """Prompt the user to update a rating for a date and save it."""
        new_rating = self._input_rating(
            f"Enter new rating for {date} "
            f"({self.dqt.min_rating}~{self.dqt.max_rating}): "
        )
        
        self.json.update(date=date, rating=new_rating)
        log_saved("Rating updated and saved!")
    
    def _change_memory_for_date(self, date: str) -> None:
        """Prompt the user to update a memory entry for a date and save it."""
        original_mem = self.json.logs[date][self.json.memory_kyname]
        placeholder = self.memory_edit_placeholder
        
        raw = self._input_memory(dedent(f"""
            Enter new memory entry for {date}.

            To insert your original memory entry into your edit,
            use '{placeholder}'.

            Examples:
              → {placeholder} This is a new sentence.
              → This is a new sentence. {placeholder}
              → This is new. {placeholder} More text.

            (Only the first '{placeholder}' will be replaced.)
        """), False)
        
        new_memory = self._confirm_memory_edit(raw, original_mem, date)
        self.json.update(date=date, memory=new_memory)
        log_saved("Memory entry updated and saved!")
    
    def _confirm_memory_edit(self, raw: str, original: str, date: str) -> str:
        """Validate, preview, and confirm an edited memory entry.

        Handles placeholder resolution, length-difference warnings, and
        final user confirmation. Re-prompts until the user confirms
        the edited entry.
        """

        while True:
            new_memory = self._resolve_memory_edit(raw, original)
            
            if not original.strip() and raw.strip():
                if not confirm(
                        "The original memory entry was empty. Are you sure?"
                ):
                    raw = self._input_memory(
                        f"Enter new memory entry for {date}"
                    )
                    continue
            
            len_diff = len(original) - len(new_memory)
            if len_diff > self.memory_edit_length_diff_alert_threshold:
                if not confirm(
                    "The new memory entry is significantly shorter than "
                    f"the original (by {len_diff} characters). Are you "
                    "sure?"
                ):
                    raw = self._input_memory(
                        f"Enter new memory entry for {date}"
                    )
                    continue
            
            print("\nNew memory entry:")
            print_wrapped(new_memory, self.dqt.linewrap_maxcol)
            
            if confirm("\nConfirm?"):
                break
            
            raw = self._input_memory(
                f"Enter new memory entry for {date}"
            )
        return new_memory
    
    def _resolve_memory_edit(self, mem_input: str, original_mem: str) -> str:
        """Replace the first instance of the placeholder with the original."""
        if self.memory_edit_placeholder in mem_input:
            print("\n(Original memory entry has been inserted into your edit)")
            return mem_input.replace(
                self.memory_edit_placeholder, original_mem, 1
            )
        return mem_input
    
    def _input_rating(self, prompt: str, newline: bool = True) -> float | None:
        """Get and validate user float input."""
        error_msg = (
            f"Please enter a valid number from "
            f"{self.dqt.min_rating} to {self.dqt.max_rating}."
        )
        
        while True:
            raw = input(f"{"\n" if newline else ""}{prompt}").lower().strip()
            
            if raw == '-':
                if confirm(
                    "Are you sure you want to enter an empty (null) rating?"
                ):
                    return None
                continue
            
            try:
                value = float(raw)
            except ValueError:
                err(error_msg)
                continue
            
            if not (self.dqt.min_rating <= value <= self.dqt.max_rating):
                err(error_msg)
                continue
            
            return round(value, self.dqt.rating_inp_dp)
    
    @staticmethod
    def _input_memory(prompt: str, newline: bool = True) -> str:
        """Prompt user for today's memory entry."""
        while True:
            tdys_mem = input(
                f"{"\n" if newline else ""}"
                f"{prompt}"
                f"{"\n" if newline else ""}"
                f"\n->: "
            ).strip()
            
            if not tdys_mem:
                if confirm(
                    "Are you sure you want to enter an empty memory entry?"
                ):
                    return tdys_mem
                continue
            break
        
        return tdys_mem
