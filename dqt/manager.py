import os
import platform
import subprocess
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

from dqt.json_manager import JSONManager
from dqt.ui_utils import (
    confirm,
    err,
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

    # For editing within Terminal CLI only
    MEMORY_EDIT_PLACEHOLDER: str = '{}'
    MEMORY_EDIT_LENGTH_DIFF_ALERT_THRESHOLD: int = 200
    
    def __init__(self, dqt: Tracker):
        self.dqt: Tracker = dqt
        self.json: JSONManager = dqt.json
        self.mem_editor = _MemoryEditor(self)

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

        match choice := menu(
            "1) Enter missing logs now",
            "2) Enter missing logs later -> Main menu",
            "3) Skip missing logs -> Enter today's log",
        ):
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

                    memory, _ = self._input_memory(
                        "Enter a memory entry (leave blank to skip): "
                    )

                    date_str = datetime.strftime(date, self.dqt.date_format)

                    self.json.add(date_str, rating, memory)

                log_saved("Logs saved!")

            case '2':
                print_wrapped(
                    "\nRestart the program later to enter your missing "
                    "logs! (You can only enter today's log after "
                    "entering the missed logs, unless you choose to skip "
                    "them.)",
                    self.dqt.linewrap_maxcol
                )

            case '3':
                print_wrapped(
                    "\nYou will have to enter the missed logs later "
                    f"manually in `{self.json.FILENAME}`, unless you "
                    "don't enter today's log yet."
                    "\nYou can open the file by selecting:"
                    "\nMain menu -> 5) View [A]ll logs "
                    "-> 2) [O]pen JSON file in default viewer/editor"
                    "\nMake sure you save any changed before closing "
                    "the file.",
                    self.dqt.linewrap_maxcol
                )

        return choice

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

            tdys_memory, _ = self._input_memory(
                f"Enter a memory entry; write a few sentences about your "
                f"day. \nLeave this blank to skip."
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
        self._change_data('today', self.json.RATING_KYNAME)

    def change_todays_memory(self) -> None:
        """Prompt the user to change today's memory entry."""
        self._change_data('today', self.json.MEMORY_KYNAME)

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
        self._change_data(selected_date, self.json.RATING_KYNAME)

    def change_previous_memory(self, selected_date: str) -> None:
        """Prompt the user to change a memory entry from a previous day."""
        self._change_data(selected_date, self.json.MEMORY_KYNAME)

    def _change_data(self, selected_date: str, changing: str) -> None:
        """Change data for the selected date and update JSON.
        
        If the specified date is the string 'today', today's date (or rather,
        the date specified in the global variable `_today`, which is evaluated
        at the start of runtime) will be used.
        
        Parameter `changing` must be either the rating or memory key name
        specified in JSONManager (raises a ValueError otherwise).
        """
        if changing not in (self.json.RATING_KYNAME, self.json.MEMORY_KYNAME):
            raise ValueError(
                f"'changing' argument must be '{self.json.RATING_KYNAME}' or "
                f"'{self.json.MEMORY_KYNAME}'"
            )

        if selected_date == 'today':
            selected_date = _today.strftime(self.dqt.date_format)

        if changing == self.json.RATING_KYNAME:
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
        original_mem = self.json.logs[date][self.json.MEMORY_KYNAME]

        raw, used_terminal = self._input_memory(
            f"Enter new memory entry for {date}.",
            original_mem,
            terminal_newline=False
        )

        new_memory = self._confirm_memory_edit(
            raw, original_mem, date, used_terminal
        )
        self.json.update(date=date, memory=new_memory)
        log_saved("Memory entry updated and saved!")

    def _confirm_memory_edit(self, raw: str, original: str, date: str,
                             used_terminal: bool = False) -> str:
        """Validate, preview, and confirm an edited memory entry.

        Handles placeholder resolution, length-difference warnings, and
        final user confirmation. Re-prompts until the user confirms
        the edited entry.
        """

        while True:
            if used_terminal:
                new_memory = self._resolve_memory_edit(raw, original)
            else:
                new_memory = raw

            if not original.strip() and raw.strip():
                if not confirm(
                    "The original memory entry was empty. Are you sure?"
                ):
                    raw, _ = self._input_memory(
                        f"Enter new memory entry for {date}.",
                        original
                    )
                    continue

            len_diff = len(original) - len(new_memory)
            if len_diff > self.MEMORY_EDIT_LENGTH_DIFF_ALERT_THRESHOLD:
                if not confirm(
                    "The new memory entry is significantly shorter than "
                    f"the original (by {len_diff} characters). Are you "
                    "sure?"
                ):
                    raw, _ = self._input_memory(
                        f"Enter new memory entry for {date}",
                        original
                    )
                    continue

            print("\nNew memory entry:")
            print_wrapped(new_memory, self.dqt.linewrap_maxcol)

            if confirm("Confirm?"):
                break

            raw, _ = self._input_memory(
                f"Enter new memory entry for {date}",
                original
            )
        return new_memory

    def _resolve_memory_edit(self, mem_input: str, original_mem: str) -> str:
        """Replace the first instance of the placeholder with the original."""
        if self.MEMORY_EDIT_PLACEHOLDER in mem_input:
            print("\n(Original memory entry has been inserted into your edit)")
            return mem_input.replace(
                self.MEMORY_EDIT_PLACEHOLDER, original_mem, 1
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
                    "Are you sure you want to save an empty (null) rating?"
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

    def _input_memory(self,
                      prompt: str,
                      original_mem: str | None = None,
                      terminal_newline: bool = True,
                      write_initial_contents: bool = True) -> tuple[str, bool]:
        """Prompt user for today's memory entry via text editor.

        Fall back to input via Terminal if file fails to open or if an error
        occurs.

        Args:
            prompt (str):
                Prompt shown at start of temp editor text file.
                If using Terminal fallback, shown as printed prompt.
            original_mem (str. optional):
                If the user is to write a new memory entry, this should be
                `None`. Otherwise, if a `str` is given, it means the user is
                editing an existing entry.
            terminal_newline (bool, optional):
                Applies to terminal fallback only. Determines whether to
                print the prompt between two blank lines.
            write_initial_contents (bool):
                Whether to overwrite the file and write initial contents.
                This should be turned off when user content is to be
                preserved after failure and the user must retry, to prevent
                loss of any saved data.

        Returns:
            Return a tuple of the memory entry and whether the fallback was
            used.
        """
        try:
            return (
                self.mem_editor.start_memory_editor(prompt, original_mem),
                False
            )
        except PermissionError as e:
            lineno = traceback.extract_tb(e.__traceback__)[-1].lineno
            err(
                "An error occurred while trying to create or write to the "
                "memory edit text file.",
                f"\n{e.__repr__()} (line {lineno})"
            )
        except UnicodeError as e:
            lineno = traceback.extract_tb(e.__traceback__)[-1].lineno
            err(
                "An error occurred while trying to read or write to the "
                "memory edit text file",
                f"\n{e.__repr__()} (line {lineno})"
            )
        except subprocess.SubprocessError as e:
            lineno = traceback.extract_tb(e.__traceback__)[-1].lineno
            err(
                "An error occurred while trying to open the text editor "
                "application.",
                f"\n{e.__repr__()} (line {lineno})"
            )
        except Exception as e:
            lineno = traceback.extract_tb(e.__traceback__)[-1].lineno
            err(
                "An unexpected error occurred while trying to open, write to, "
                "or read from the memory edit text file",
                f"\n{e.__repr__()} (line {lineno})"
            )

        print(f"\nIf you've made changes to the file, {Txt("DO NOT").bold()} "
              f"close your text editor yet. Copy and paste any text you want "
              f"to save to a safe place.")

        match menu(
            "1) Try starting the editor again",
            "2) Enter your memory entry here in the CLI instead",
            prompt="Choose what to do next: "
        ):
            case '1':
                return self._input_memory(
                    prompt,
                    original_mem,
                    terminal_newline,
                    write_initial_contents
                )
            case '2':
                return (
                    self._input_memory_terminal(prompt, terminal_newline),
                    True
                )
            case _:
                raise RuntimeError(
                    "If you're reading this, something is wrong with "
                    "`ui_utils.menu()`"
                )

    @staticmethod
    def _input_memory_terminal(prompt: str, newline: bool = True) -> str:
        """Prompt user for today's memory entry via CLI (terminal).

        Fall back to input via terminal if file fails to open or if an error
        occurs.
        """
        while True:
            tdys_mem = input(
                f"{"\n" if newline else ""}"
                f"{prompt}"
                f"{"\n" if newline else ""}"
                f"\n->: "
            ).strip()

            if not tdys_mem:
                if confirm(
                    "Are you sure you want to save an empty memory entry?"
                ):
                    return tdys_mem
                continue
            break

        return tdys_mem


class _MemoryEditor:
    """A class to handle memory editing in the text file."""

    FILEDIRNAME: str = 'data'
    FILENAME: str = 'MEMORY_ENTRY_EDIT.txt'
    COMMENT_CHAR: str = '//'
    INITIAL_CONTENTS_TEMPLATE: str = (
        " Lines beginning with '{comment_char}' will be ignored.\n"
        " Memory entries are NOT saved in this file; this is just a "
        "temporary editor that is cleared every time you edit or write a "
        "new memory entry.\n"
        " Remember to *SAVE THIS FILE* (Ctrl + S / ⌘ + S) before closing!\n"
        " Write/edit your memory entry below this line.\n \n"
        " —————————————————————————————————————————————————————————————"
    )

    def __init__(self, manager: Manager):
        self.manager = manager

        rootdir: Path = Path(__file__).resolve().parent.parent
        self.memory_edit_filedirpath: Path =\
            rootdir / self.FILEDIRNAME
        self.memory_edit_filepath: Path =\
            self.memory_edit_filedirpath / self.FILENAME

    def start_memory_editor(self,
                            prompt: str,
                            original_entry: str | None = None,
                            write_initial_contents: bool = True) -> str:
        """Start memory editing process.

        Args:
            prompt (str):
                prompt inserted to top of file as comment
            original_entry (str):
                When `original_contents` is given, it means an existing
                entry is being edited and the string will be inserted into
                the initial contents of the file. Otherwise, it means a new
                entry is being created.
            write_initial_contents (bool):
                Whether to overwrite the file and write initial contents.
                This should be turned off when user content is to be
                preserved after failure and the user must retry, to prevent
                loss of any saved data.

        Return:
            str: new memory entry
        """
        if write_initial_contents:
            self._write_initial_contents(prompt, original_entry)

        while True:
            print("\nOpening memory editor...")
            self._open_memory_edit_file()
            input(
                f"\n[{Txt("Press ENTER").bold()} once you are done editing and "
                f"have {Txt("saved the text file").bold().red()}]"
            )
            contents: list[str] = self._read_text_file()
            comments_removed = self._remove_commented_lines(contents)

            return_msg = self._check_edit(
                comments_removed,
                original_entry.splitlines(keepends=True)
                if original_entry is not None else None,
            )
            if return_msg is None:
                return ''.join(comments_removed).strip()

            if confirm(return_msg):
                return ''.join(comments_removed).strip()

    def _write_initial_contents(self,
                                prompt: str,
                                entry_to_load: str | None = None) -> None:
        """Write initial contents (comments) to file.

        Args:
            prompt (str): Write at the start of file as comment
            entry_to_load (str, optional): Write to end of file

        If editing existing entry (meaning `entry_to_load` is given),
        that will also be inserted at the end of the file.
        """
        initial_contents = (
            f" {prompt}\n \n"
        ) + self.INITIAL_CONTENTS_TEMPLATE

        initial_contents_formatted: str = self._insert_comment_char(
            initial_contents.format(
                comment_char=self.COMMENT_CHAR
            ).splitlines()
        )

        if not initial_contents_formatted.endswith('\n\n'):
            initial_contents_formatted =\
                initial_contents_formatted.rstrip('\n') + '\n\n'

        self.memory_edit_filedirpath.mkdir(parents=True, exist_ok=True)
        with open(self.memory_edit_filepath, 'w', encoding='utf-8',
                  newline='\n') as f:
            f.write(initial_contents_formatted)
            if entry_to_load is not None:
                f.write(entry_to_load)

    def _open_memory_edit_file(self) -> None:
        """Open memory edit file."""
        system_name = platform.system()

        if system_name == 'Windows':
            os.startfile(self.memory_edit_filepath)
        elif system_name == 'Darwin':  # macOS
            subprocess.run(['open', self.memory_edit_filepath], check=True)
        else:  # Linux / Unix
            subprocess.run(['xdg-open', self.memory_edit_filepath], check=True)

    def _insert_comment_char(self, contents: list[str]) -> str:
        """Insert the comment character at the start of each line."""
        return '\n'.join(
            self.COMMENT_CHAR + line
            for line in contents
        )

    def _read_text_file(self) -> list[str]:
        """Read the file and return contents as a list of each line."""
        with open(self.memory_edit_filepath, 'r', encoding='utf-8') as f:
            return f.readlines()

    def _check_edit(
            self,
            contents: list[str],
            original_contents: list[str] | None = None
    ) -> str | None:
        """Check the memory edit entered by the user to prevent data loss.

        When `original_contents` is given, it means an existing entry is
        being edited. Otherwise, it means a new entry is being created.

        Return user warning if the user needs to be warned. Return None if
        passed with no issues.
        """
        if not any(c.strip() for c in contents):
            return (
                "Are you sure you want to save an empty memory entry? (Did "
                "you remember to save [Ctrl + S / ⌘ + S] before closing?)"
            )

        if original_contents is None:
            return None

        len_diff = len(''.join(original_contents)) - len(''.join(contents))
        if len_diff > self.manager.MEMORY_EDIT_LENGTH_DIFF_ALERT_THRESHOLD:
            return (
                f"Your new memory entry is {len_diff} characters shorter "
                "than your original entry. Are you sure you've saved "
                "(Ctrl + S / ⌘ + S) your edit?"
            )

        if '\n'.join(original_contents).strip() == '\n'.join(contents).strip():
            return (
                f"It looks like your edit matches your original entry. "
                "Are you sure you've saved (Ctrl + S / ⌘ + S) your edit?"
            )

        return None

    def _remove_commented_lines(self, contents: list[str]) -> list[str]:
        """Remove all lines starting with the comment char.

        Ignore whitespace and look at first non-whitespace character.
        """
        return [
            line
            for line in contents
            if not line.lstrip().startswith(self.COMMENT_CHAR)
        ]
