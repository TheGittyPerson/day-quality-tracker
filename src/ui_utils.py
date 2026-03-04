import textwrap
from time import sleep
from typing import TYPE_CHECKING

from src.styletext import StyleText as Txt

if TYPE_CHECKING:
    from src.styletext import StyleText


def confirm(message: str, confirm_char: str = 'y',
            err_msg: str = "Only enter 'y' or 'n'.") -> bool:
    """Prompt the user for confirmation and validate input.
    
    Keep looping until user enters 'y' or 'n'.
    Return whether user input (lowercased) is equal to `confirm_char`.
    """
    while True:
        inp = input(f"\n{message} [y/n]: ").strip().lower()
        if inp not in ['y', 'n']:
            err(err_msg)
            continue
        break
    return inp == confirm_char.lower()


def cont_on_enter(msg: str = "[Press ENTER ↩ to return to main menu]") -> None:
    """Pause the program until the user presses Enter."""
    input(f"\n{msg}")


def err(message: str, *desc: str, pause: bool = True) -> None:
    """Print formatted error message."""
    print(
        Txt("\n❌ Error: ").bold().red()
        + message
    )
    for d in desc:
        print(d)
    if pause:
        sleep(1)
        

def invalid_choice(opts: int,
                   letters_given: bool = True,
                   start: int = 1) -> None:
    err(
        f"Only enter a number {start}~{opts}"
        f"{" or the given letters" if letters_given else ""}."
    )


def log_saved(text: str = "Log saved!") -> None:
    """Print formatted message to inform user that log was saved."""
    print("\n✅ " + Txt(text).bold().green())
    sleep(1)


def menu(*options: str | StyleText,
         title: str | StyleText | None = "Choose what to do: ") -> int:
    """Display menu options with title prompt. Return number of options."""
    if title is not None:
        print(Txt(f"\n{title}").bold())
    for i, o in enumerate(options, 1):
        print(Txt(f"{i})").bold(), o.removeprefix(f'{i}) '))
    return len(options)


def print_wrapped(text: str, maxcol: int):
    """Print line-wrapped text with a maximum of `maxcol` chars per line."""
    leading_newlines = len(text) - len(text.lstrip('\n'))
    stripped = text.lstrip('\n')

    wrapped = textwrap.fill(stripped, maxcol)
    print("\n" * leading_newlines + wrapped)
    