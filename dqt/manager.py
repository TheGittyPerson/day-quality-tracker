import os
import platform
import subprocess
import traceback
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Literal, TYPE_CHECKING, overload

from dqt.json_manager import JSONManager
from dqt.ui_utils import (
    confirm,
    err,
    log_saved,
    menu,
    print_wrapped,
    warn,
    warning,
)
from dqt.styletext import StyleText as Txt

if TYPE_CHECKING:
    from tracker import Tracker

# Today's date is initialized at the start and used statically to prevent
# confusion if the program is run across midnight
_today: datetime = datetime.today()


class Manager:
    """A class to handle user interactions and main menu options."""

    # For editing within Terminal CLI only
    MEMORY_EDIT_PLACEHOLDER: str = "{}"
    MEMORY_EDIT_LENGTH_DIFF_ALERT_THRESHOLD: int = 200
    
    def __init__(self, dqt: Tracker):
        self.dqt: Tracker = dqt
        self.json: JSONManager = dqt.json
        self.mem_editor = _MemoryEditor(self)

    def handle_logs_entry(self) -> None:
        """Handle entry of missing logs.

        This should be called before entering the main menu loop.

        User chooses to enter missing logs or not. If they do,
        loop through each missing date and prompt a log.
        Return the option the user chose if missed prior dates.

        - "1" = Enter missing logs now
        - "2" = Enter missing logs later -> Main menu
        - "3" = Skip missing logs -> Enter today's log
        """
        if (last_log_date := self._report_missing_logs()) is not None:
            match menu(
                "1) Write missing logs [N]ow",
                "2) Write missing logs [L]ater -> Main menu",
            ):
                case "1" | "n":
                    self._input_missing_logs(last_log_date)
                case "2" | "l":
                    print_wrapped(
                        "\nRestart the program later to write your missing "
                        "logs! (Writing today's log before doing this means "
                        "you'll need to enter your missing logs manually in "
                        f"{self.json.filepath})",
                        self.dqt.linewrap_maxcol
                    )
                    return

    def _report_missing_logs(self) -> date | None:
        """Check and report if any previous days are missing logs.

        **IGNORES intentionally skipped logs**, AKA dates without a log
        but the following dates of which do.

        Returns:
            ``None`` if no missed logs. Otherwise, return ``date`` object of
            the last log. Plug this value into ``enter_missing_logs()``.
        """
        if self.json.no_logs():  # Ignore for first-time runs
            return None

        log_dates = [
            datetime.strptime(d, self.dqt.date_format).date()
            for d in self.json.logs.keys()
        ]
        last_date = max(log_dates)
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
            return last_date
        else:
            print(
                f"\nYou have {missing_logs_count} missing logs: "
                f"{first_missed_date_str} to {last_missed_date_str}."
            )
            return last_date

    def _input_missing_logs(self, last_log_date: date) -> None:
        """Prompt for all missing logs in a loop.
        
        Args:
            last_log_date (date): Date of most recent log
        """
        # Get list of missed dates
        days_since_last = (_today.date() - last_log_date).days

        missed_dates: list[date] = []
        curr_loop_date = last_log_date + timedelta(days=1)
        #                               Exclude today
        while len(missed_dates) < days_since_last - 1:
            missed_dates.append(curr_loop_date)
            curr_loop_date += timedelta(days=1)

        for d in missed_dates:
            rating = self._input_rating(
                f"Enter your rating for {d} "
                f"({self.dqt.min_rating}~{self.dqt.max_rating}, or '-' for a "
                "null rating. 's' to permanently skip this day): ",
            )

            if rating == "SKIP":
                print(
                    f"\nSkipped log for {d}. You can enter this log manually "
                    "in the JSON file later (avoid doing this while the "
                    "program is running)."
                )
                continue

            new_file = True
            while True:
                memory, _ = self._input_memory(
                    "Write a memory entry (leave blank to skip): ",
                    new_file=new_file,
                )

                if self._confirm_memory_final(memory):
                    break
                new_file = False

            date_str = d.strftime(self.dqt.date_format)

            self.json.add(date_str, rating, memory)

        log_saved("Logs saved!")

    def input_todays_log(self) -> None:
        """Prompt for today's rating and memory entry if not entered yet."""
        tdys_rating = self._input_rating(
            f"Rate your day from {self.dqt.min_rating} to "
            f"{self.dqt.max_rating}, {self.dqt.neutral_rating} being an "
            f"average day "
            f"\n(enter '-' to skip, 'c' to cancel today's log entry): ",
            skip_char='c'
        )

        if tdys_rating == "SKIP":
            return

        new_file = True
        while True:
            tdys_memory, _ = self._input_memory(
                f"Write a memory entry; enter a few sentences about your "
                f"day. \nLeave this blank to skip.",
                new_file
            )

            if not tdys_memory:
                print(
                    "\nTo write your memory entry later: "
                    "\nMain menu -> Edit today's/previous log "
                    "-> Edit memory"
                )
                break

            if self._confirm_memory_final(tdys_memory):
                break
            new_file = False

        # Save data
        today = _today.strftime(self.dqt.date_format)
        self.json.add(today, tdys_rating, tdys_memory)
        log_saved()

    def change_todays_rating(self) -> None:
        """Prompt the user to change today's rating."""
        self._change_data("today", self.json.RATING_KYNAME)

    def change_todays_memory(self) -> None:
        """Prompt the user to change today's memory entry."""
        self._change_data("today", self.json.MEMORY_KYNAME)

    def prompt_date(self,
                    prompt: str | None = None,
                    starting_date: str | datetime = _today,
                    backwards_offset: bool = True) -> str:
        """Prompt the user to enter a date for a log.

        Reject dates for logs that do not exist.

        Args:
            prompt (str, optional): prompt to show
            starting_date (datetime):
                If the user enters an integer to specify the numbers days of
                days ago, this date is used. e.g., ``2`` -> 2 days
                before this date. Defaults to today's date. If the
                user enters ``0``, this date is returned. A negative number
                returns a *later* date from this date.
            backwards_offset (bool, optional):
                If ``True``, a positive integer input would return an earlier
                log (date before ``starting_date``), and a later log for a
                negative number, instead of the other way round.
        """
        if isinstance(starting_date, str):
            starting_date: datetime = datetime.strptime(
                starting_date, self.dqt.date_format
            )

        selected_date: str = ""
        while True:
            inp = input(
                "\nEnter the number of days ago or exact date "
                f"('{self.dqt.date_format_print}'): "
                if prompt is None else "\n" + prompt
            ).strip()

            # If number of days ago/later specified, get date
            if inp.isdigit():
                inp = int(inp)
                try:
                    if backwards_offset:
                        selected_dateobj = starting_date - timedelta(days=inp)
                    else:
                        selected_dateobj = starting_date + timedelta(days=inp)
                except OverflowError:
                    err(
                        "Date out of range.",
                        "\nTry again."
                    )
                    continue
                selected_date = selected_dateobj.strftime(self.dqt.date_format)
                print(Txt(f"Date selected: {selected_date}").bold())

            # Else, validate date str
            else:
                try:
                    datetime.strptime(inp, self.dqt.date_format)
                except ValueError:
                    err("Enter either a valid date in the format "
                        f"{self.dqt.date_format_print} or an integer.")
                    continue
                selected_date = inp

            # Check if date exists in saved ratings
            try:
                self.json.logs[selected_date]
            except KeyError:
                err(
                    "Rating for specified date not found.",
                    "Ensure you have already entered a rating for that date.",
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
        
        If the specified date is the string "today", today's date (or rather,
        the date specified in the global variable ``_today``, which is
        evaluated at the start of runtime) will be used.
        
        Parameter ``changing`` must be either the rating or memory key name
        specified in JSONManager (raises a ValueError otherwise).
        """
        if changing not in (self.json.RATING_KYNAME, self.json.MEMORY_KYNAME):
            raise ValueError(
                f"'changing' argument must be '{self.json.RATING_KYNAME}' or "
                f"'{self.json.MEMORY_KYNAME}'"
            )

        if selected_date == "today":
            selected_date = _today.strftime(self.dqt.date_format)

        if changing == self.json.RATING_KYNAME:
            self._change_rating_for_date(selected_date)
        else:
            self._change_memory_for_date(selected_date)

    def _change_rating_for_date(self, _date: str) -> None:
        """Prompt the user to update a rating for a date and save it."""
        new_rating = self._input_rating(
            f"Enter new rating for {_date} "
            f"({self.dqt.min_rating}~{self.dqt.max_rating}): "
        )

        self.json.update(date=_date, rating=new_rating)
        log_saved("Rating updated and saved!")

    def _change_memory_for_date(self, _date: str) -> None:
        """Prompt the user to update a memory entry for a date and save it."""
        original_mem = self.json.get_memory(_date)

        new_file = True
        while True:
            raw, used_terminal = self._input_memory(
                f"Write new memory entry for {_date}.",
                new_file,
                original_mem,
                terminal_newline=False
            )

            if used_terminal:
                new_entry = self._resolve_memory_edit(raw, original_mem)
            else:
                new_entry = raw

            # The following 2 conditions MUST check for `not ...` and
            # continue instead of excluding `not` and using breaks.

            if used_terminal and not self._check_memory_edit(
                    new_entry, original_mem
            ):
                new_file = False
                continue

            if not self._confirm_memory_final(new_entry):
                new_file = False
                continue

            break

        self.json.update(date=_date, memory=new_entry)
        log_saved("Memory entry updated and saved!")

    def _check_memory_edit(self, entry: str, original: str) -> bool:
        """Check for length differences between the new and original entry.

        Note: USE IF THE ENTRY IS ENTERED FROM TERMINAL ONLY. The memory editor
        has its own check (see ``_MemoryEditor`` class).

        Checks:
            - whether length difference is higher than the specified threshold
            (see attribute).
            - whether entry is the same as the original

        Prompt the user for confirmation. Return ``True`` if there are no
        issues, or if the user chooses to ignore the warning.

        Return whether the user confirms their entry. Return ``False`` if the
        user wishes to rewrite their entry.
        """
        len_diff = len(original) - len(entry)
        word_diff = len(original.split()) - len(entry.split())
        if len_diff > self.MEMORY_EDIT_LENGTH_DIFF_ALERT_THRESHOLD:
            return confirm(
                warning(
                    f"Your new memory entry is {len_diff} characters "
                    f"({word_diff} words) shorter than your original entry. "
                    f"Are you sure?"
                )
            )

        if entry.strip() == original.strip():
            return confirm(
                warning(
                    "It looks like your edit matches your original entry. "
                    "Are you sure?"
                )
            )

        return True

    def _confirm_memory_final(self, entry: str):
        """Show the user their new entry for confirmation.

        Use as confirmation right before saving (at the end of memory entry
        pipelines)
        """
        print(Txt("\nNew memory entry:\n").bold())
        print_wrapped(entry, self.dqt.linewrap_maxcol)

        if not (confirmed := confirm("Confirm?")):
            print("\nTrying again.")

        return confirmed

    def _resolve_memory_edit(self, mem_input: str, original_mem: str) -> str:
        """Replace the first instance of the placeholder with the original."""
        if self.MEMORY_EDIT_PLACEHOLDER in mem_input:
            print("\n(Original memory entry has been inserted into your edit)")
            return mem_input.replace(
                self.MEMORY_EDIT_PLACEHOLDER, original_mem, 1
            )
        return mem_input

    @overload
    def _input_rating(self, prompt: str, newline: bool = True,
                      skip_char: None = None) -> float | None: ...

    @overload
    def _input_rating(
            self, prompt: str, skip_char: str, newline: bool = True,
    ) -> float | None | Literal["SKIP"]: ...

    def _input_rating(
            self,
            prompt: str,
            newline: bool = True,
            skip_char: str | None = None
    ) -> float | None | Literal["SKIP"]:
        """Get and validate user float input.

        If ``skip_char`` is not ``None``, the user can choose to enter
        ``skip_char`` to indicate that they want to skip an entire log entry for
        the day, including memory entry. Return "SKIP" in that case.

        Args:
            prompt (str): Input prompt
            newline (bool, optional): Add a newline before the prompt if True
            skip_char (str, optional):
                The string a user can enter to indicate that they want to skip
                an entire log entry for the day, including memory entry.
                "SKIP" if returned is they choose. If ``None``, this is not
                allowed and will prompt the user to try again if they don't
                enter a number.
        """
        error_msg = (
            f"Please enter a valid number from {self.dqt.min_rating} "
            f"to {self.dqt.max_rating}"
        ) + (f" or '{skip_char}'." if skip_char is not None else "")

        while True:
            raw = input(f"{"\n" if newline else ""}{prompt}").lower().strip()

            if raw == "-":
                if confirm(
                    "Are you sure you want to save an empty (null) rating?"
                ):
                    return None
                continue

            if skip_char is not None and raw == skip_char:
                return "SKIP"

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
                      new_file: bool,
                      original_mem: str | None = None,
                      terminal_newline: bool = True) -> tuple[str, bool]:
        """Prompt user for a memory entry via the text editor.

        Fall back to input via Terminal if file fails to open or if an error
        occurs.

        Args:
            prompt (str):
                Prompt shown at start of temp editor text file.
                If using Terminal fallback, shown as printed prompt.
            new_file (bool):
                Whether to create and seed a new temp editor file. Set this to
                ``False`` only when retrying after a failure, so the previous
                temp file path and any saved user draft are preserved.
            original_mem (str. optional):
                If the user is to write a new memory entry, this should be
                ``None``. Otherwise, if a ``str`` is given, it means the user is
                editing an existing entry.
            terminal_newline (bool, optional):
                Applies to terminal fallback only. Determines whether to
                print the prompt between two blank lines.

        Returns:
            Return a tuple of the memory entry and whether the fallback was
            used.
        """
        try:
            return (
                self.mem_editor.start_memory_editor(
                    prompt,
                    original_mem,
                    new_file
                ),
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

        warn(
            f"\nIf you've made changes to the file, {Txt("DO NOT").bold()} "
            "close your text editor yet. Copy and paste any text you want "
            "to save to a safe place."
        )

        match menu(
            "1) Try starting the editor again",
            "2) Write your memory entry here in the CLI instead",
            prompt="Choose what to do next: "
        ):
            case "1":
                return self._input_memory(
                    prompt,
                    new_file=False,
                    original_mem=original_mem,
                    terminal_newline=terminal_newline,
                )
            case "2":
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
        """Prompt user for a memory entry via CLI (terminal).

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
    """A class to handle memory editing through temporary text files."""

    FILEDIRNAME: str = "data"
    FILENAME_PREFIX: str = "MEM_ENTRY_EDIT"
    COMMENT_CHAR: str = "//"
    INITIAL_CONTENTS_TEMPLATE: str = (
        "Lines beginning with '{comment_char}' will be ignored.\n"
        "Memory entries are NOT permanently saved in this file; this is just "
        "a temporary file for this entry.\n"
        "Remember to *SAVE THIS FILE* (Ctrl + S / ⌘ + S) before closing!\n"
        "Write/edit your memory entry below this line.\n\n"
        "—————————————————————————————————————————————————————————————"
    )
    FILE_TIMESTAMP_FORMAT: str = "%Y%m%d_%H%M%S_%f"

    def __init__(self, manager: Manager):
        self.manager = manager

        rootdir: Path = Path(__file__).resolve().parent.parent
        self.memory_edit_filedirpath: Path =\
            rootdir / self.FILEDIRNAME
        # Set when a temp edit file is created; reused during retry flows.
        self.memory_edit_filepath: Path = Path()

    def start_memory_editor(self,
                            prompt: str,
                            original_entry: str | None = None,
                            new_file: bool = True) -> str:
        """Start memory editing process.

        Args:
            prompt (str):
                prompt inserted to top of file as comment
            original_entry (str):
                When ``original_contents`` is given, it means an existing
                entry is being edited and the string will be inserted into
                the initial contents of the file. Otherwise, it means a new
                entry is being created.
            new_file (bool):
                Whether to create a fresh timestamped temp file and write its
                initial contents. Set this to ``False`` only when retrying
                after a failure, so the existing temp file path and any saved
                user draft are preserved.

        Return:
            str: new memory entry
        """
        if new_file:
            self._delete_files()
            self.memory_edit_filepath = self._new_memory_edit_filepath()

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
                return "".join(comments_removed).strip()

            if confirm(return_msg):
                return "".join(comments_removed).strip()

    def _delete_files(self) -> None:
        """Delete stale timestamped memory edit files."""
        older_than: int | None = self.manager.dqt.delete_mem_edit_files_after
        if older_than is None or not self.memory_edit_filedirpath.exists():
            return

        for filepath in self.memory_edit_filedirpath.glob(
            f"{self.FILENAME_PREFIX}_*.txt"
        ):
            if not filepath.is_file() or filepath == self.memory_edit_filepath:
                continue

            timestamp: str = filepath.stem.removeprefix(
                f"{self.FILENAME_PREFIX}_"
            )
            try:
                created_at: datetime = datetime.strptime(
                    timestamp,
                    self.FILE_TIMESTAMP_FORMAT
                )
            except ValueError:
                continue

            time_diff = datetime.now() - created_at
            if time_diff > timedelta(days=older_than):
                try:
                    filepath.unlink(missing_ok=True)
                except OSError:
                    continue

    def _write_initial_contents(self,
                                prompt: str,
                                entry_to_load: str | None = None) -> None:
        """Write prompt comments and optional existing entry to the temp file.

        Args:
            prompt (str): Written at the start of the file as comments.
            entry_to_load (str, optional): Written to the end of the file.

        If editing existing entry (meaning ``entry_to_load`` is given),
        that will also be inserted at the end of the file.
        """
        initial_contents = f"{prompt}\n\n" + self.INITIAL_CONTENTS_TEMPLATE

        initial_contents_formatted: str = self._insert_comment_char(
            initial_contents.format(
                comment_char=self.COMMENT_CHAR
            ).splitlines()
        )

        if not initial_contents_formatted.endswith("\n\n"):
            initial_contents_formatted =\
                initial_contents_formatted.rstrip("\n") + "\n\n"

        self.memory_edit_filedirpath.mkdir(parents=True, exist_ok=True)
        with open(self.memory_edit_filepath, "w", encoding="utf-8",
                  newline="\n") as f:
            f.write(initial_contents_formatted)
            if entry_to_load is not None:
                f.write(entry_to_load)

    def _open_memory_edit_file(self) -> None:
        """Open the active temp memory edit file."""
        system_name = platform.system()

        if system_name == "Windows":
            os.startfile(self.memory_edit_filepath)
        elif system_name == "Darwin":  # macOS
            subprocess.run(["open", self.memory_edit_filepath], check=True)
        else:  # Linux / Unix
            subprocess.run(["xdg-open", self.memory_edit_filepath], check=True)

    def _insert_comment_char(self,
                             contents: list[str],
                             space_after_char: bool = True) -> str:
        """Insert the comment character at the start of each line."""
        return "\n".join(
            self.COMMENT_CHAR + (" " if space_after_char else "") + line
            for line in contents
        )

    def _read_text_file(self) -> list[str]:
        """Read the active temp file and return its lines."""
        with open(self.memory_edit_filepath, "r", encoding="utf-8") as f:
            return f.readlines()

    def _new_memory_edit_filepath(self) -> Path:
        """Build a unique timestamped path for a new temp editor file."""
        timestamp = datetime.now().strftime(self.FILE_TIMESTAMP_FORMAT)
        return (self.memory_edit_filedirpath
                / f"{self.FILENAME_PREFIX}_{timestamp}.txt")

    def _check_edit(
            self,
            contents: list[str],
            original_contents: list[str] | None = None
    ) -> str | None:
        """Check the memory edit written by the user to prevent data loss.

        When ``original_contents`` is given, it means an existing entry is
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

        original_contents = "".join(original_contents)
        contents = "".join(contents)
        len_diff = len(original_contents) - len(contents)
        word_diff = len(original_contents.split()) - len(contents.split())
        if len_diff > self.manager.MEMORY_EDIT_LENGTH_DIFF_ALERT_THRESHOLD:
            return (
                f"Your new memory entry is {len_diff} characters ({word_diff} "
                "words) shorter than your original entry. Are you sure "
                "you've saved (Ctrl + S / ⌘ + S) your edit?"
            )

        if original_contents.strip() == contents.strip():
            return (
                "It looks like your edit matches your original entry. "
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
