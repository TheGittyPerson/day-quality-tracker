import re
import textwrap
from time import sleep

from dqt.styletext import StyleText


def confirm(message: str, confirm_char: str = "y",
            err_msg: str = "Only enter 'y' or 'n'.") -> bool:
    """Prompt the user for confirmation and validate input.
    
    Keep looping until user enters 'y' or 'n'.
    Return whether user input (lowercased) is equal to `confirm_char`.
    """
    while (
            inp := input(f"\n{message} [y/n]: ").strip().lower()
    ) not in ["y", "n"]:
        err(err_msg)
    return inp == confirm_char.lower()


def cont_on_enter(msg: str = "[Press ENTER ↩ to return to main menu]") -> None:
    """Pause the program until the user presses Enter."""
    input(f"\n{msg}")


def err(*message: str, pause: bool = False) -> None:
    """Print formatted error message."""
    prefix = StyleText("\n❌ Error: ").bold().red()
    print(prefix + message[0], *message[1:], sep="\n")
    if pause:
        sleep(1)


def warn(*message: str, pause: bool = False) -> None:
    """Print formatted warning message."""
    prefix = StyleText("\n⚠️ WARNING: ").bold().yellow()
    print(prefix + message[0], *message[1:], sep="\n")
    if pause:
        sleep(1)


def warning(*message: str) -> str:
    """Return a formatted warning message."""
    return str(
        StyleText("⚠️ WARNING: ").bold().yellow() + message[0]
        + "".join(f"\n{msg}" for msg in message[1:])
    )


def log_saved(text: str = "Log saved!") -> None:
    """Print formatted message to inform user that log was saved."""
    print("\n✅ " + StyleText(text).bold().green())
    sleep(1)


def menu(*options: str,
         prompt: str | StyleText | None = "Choose what to do: ") -> str:
    """Display menu prompt and options and collect user input."""
    if prompt is not None:
        print(StyleText(f"\n{prompt}").bold())
    for i, option in enumerate(options, start=1):
        print(StyleText(f"{i})").bold(), option.removeprefix(f"{i}) "))

    opts_count = len(options)

    accepted: list[str] = [str(num) for num in range(1, len(options) + 1)]
    accepted += [
        re.findall(
            r"\[([A-Za-z])]", opt
        )[0].lower()
        for opt in options
        if re.findall(
            r"\[([A-Za-z])]", opt
        )  # ... != []
    ]

    letters_given = any(opt.isalpha() for opt in accepted)
    while (user_input := input("> ").strip().lower()) not in accepted:
        err(
            f"Only enter a number 1~{opts_count}"
            f"{" or the given letters" if letters_given else ""}.\n"
        )
    return user_input


def print_wrapped(text: str, maxcol: int):
    """Print line-wrapped text with a maximum of `maxcol` chars per line."""
    leading_newlines = len(text) - len(text.lstrip("\n"))
    stripped = text.lstrip("\n")

    wrapped = "\n".join(
        textwrap.fill(
            line,
            maxcol,
            replace_whitespace=False,
            drop_whitespace=False,
        )
        for line in stripped.split("\n")
    )
    print("\n" * leading_newlines + wrapped)
