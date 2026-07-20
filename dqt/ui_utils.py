import re
import textwrap
from time import sleep
from typing import Any

__all__: list[str] = [
    "RST", "BLD", "DIM", "ITA", "UDL", "RED", "GRN", "YLW", "BLU", "MGT",
    "CYN", "WHT", "bld", "dim", "ita", "udl", "red", "grn", "ylw", "blu",
    "mgt", "cyn", "wht", "confirm", "cont_on_enter", "err", "warn",
    "warning", "report_success", "menu", "print_wrapped"
]


def confirm(message: str, confirm_char: str = "y",
            err_msg: str = "Only enter 'y' or 'n'.") -> bool:
    """Prompt the user for confirmation and validate input.
    
    Keep looping until user enters 'y' or 'n'.
    Return whether user input (lowercased) is equal to ``confirm_char``.
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
    prefix = bld(red("\n❌ Error: "))
    print(prefix + message[0], *message[1:], sep="\n")
    if pause:
        sleep(1)


def warn(*message: str, pause: bool = False) -> None:
    """Print formatted warning message."""
    prefix = bld(ylw("\n⚠️ WARNING: "))
    print(prefix + message[0], *message[1:], sep="\n")
    if pause:
        sleep(1)


def warning(*message: str) -> str:
    """Return a formatted warning message."""
    return str(
        bld(ylw("⚠️ WARNING: ")) + message[0]
        + "".join(f"\n{msg}" for msg in message[1:])
    )


def report_success(text: str, pause: bool = True) -> None:
    """Print formatted message indicating success."""
    print("\n✅ " + bld(grn(text)))
    if pause:
        sleep(1)


def menu(*options: str, prompt: str | None = "Choose what to do: ") -> str:
    """Display menu prompt and options and collect user input."""
    print(bld(f"\n{prompt}" if prompt else ""))
    for i, option in enumerate(options, start=1):
        print(bld(f"{i})"), option.removeprefix(f"{i}) "))

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
    """Print line-wrapped text with a maximum of ``maxcol`` chars per line."""
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


# -------- ANSI escape codes and functions for rich text ------- #

RST = "\033[0m"

BLD = "\033[1m"
DIM = "\033[2m"
ITA = "\033[3m"
UDL = "\033[4m"

RED = "\033[31m"
GRN = "\033[32m"
YLW = "\033[33m"
BLU = "\033[34m"
MGT = "\033[35m"
CYN = "\033[36m"
WHT = "\033[37m"


def bld(obj: Any) -> str:
    """Return bolded string representation of the object."""
    return f"{BLD}{obj}{RST}"


def dim(obj: Any) -> str:
    """Return dimmed string representation of the object."""
    return f"{DIM}{obj}{RST}"


def ita(obj: Any) -> str:
    """Return italicized string representation of the object."""
    return f"{ITA}{obj}{RST}"


def udl(obj: Any) -> str:
    """Return underlined string representation of the object."""
    return f"{UDL}{obj}{RST}"


def red(obj: Any) -> str:
    """Wrap the object in a red ANSI text escape sequence."""
    return f"{RED}{obj}{RST}"


def grn(obj: Any) -> str:
    """Wrap the object in a green ANSI text escape sequence."""
    return f"{GRN}{obj}{RST}"


def ylw(obj: Any) -> str:
    """Wrap the object in a yellow ANSI text escape sequence."""
    return f"{YLW}{obj}{RST}"


def blu(obj: Any) -> str:
    """Wrap the object in a blue ANSI text escape sequence."""
    return f"{BLU}{obj}{RST}"


def mgt(obj: Any) -> str:
    """Wrap the object in a magenta ANSI text escape sequence."""
    return f"{MGT}{obj}{RST}"


def cyn(obj: Any) -> str:
    """Wrap the object in a cyan ANSI text escape sequence."""
    return f"{CYN}{obj}{RST}"


def wht(obj: Any) -> str:
    """Wrap the object in a white ANSI text escape sequence."""
    return f"{WHT}{obj}{RST}"

# -------------------------------------------------------------- #
