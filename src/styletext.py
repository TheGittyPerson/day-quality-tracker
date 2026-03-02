import os
import sys


def _detect_ansi_support() -> bool:
    """Determine if ANSI escape codes in stdout are supported."""
    # 1) Explicit override
    if 'DQT_COLOR' in os.environ:
        return os.environ['DQT_COLOR'] == '1'
    
    # 2) PyCharm console
    if os.environ.get('PYCHARM_HOSTED') == '1':
        return True
    
    # 3) IDLE console
    if 'idlelib.run' in sys.modules:
        return False
    
    # 4) Real terminal
    if sys.stdout.isatty():
        return True
    
    # 5) Dumb terminals explicitly disable ANSI
    if os.environ.get('TERM') in (None, 'dumb'):
        return False
    
    # 6) Modern Windows terminals usually support ANSI
    if os.name == 'nt':
        return True
    
    return False


class StyleText:
    """A class to create basic styled text with ANSI escape codes."""
    
    ansi_enabled: bool | None = _detect_ansi_support()
    
    RESET: str = '\033[0m' if ansi_enabled else ''
    
    @classmethod
    def set_ansi(cls, enabled: bool | None) -> None:
        """Enable or disable ANSI escape codes usage for text styling.

        If set to None, usage will be automatically set based on whether
        stdout supports ANSI escape codes.
        """
        if enabled is None:
            cls.ansi_enabled = _detect_ansi_support()
        else:
            cls.ansi_enabled = enabled
            cls.RESET = '\033[0m' if enabled else ''
    
    def __init__(self, text: object, prefix: str = '', reset: bool = True):
        self.text: str = str(text)
        self.prefix: str = prefix
        self.reset: bool = reset
    
    def _code(self, ansi: str) -> str:
        """Return ANSI code or empty string depending on terminal support."""
        return ansi if self.ansi_enabled else ''
    
    def _add(self, code: str, reset: bool) -> "StyleText":
        return StyleText(
            self.text,
            self.prefix + self._code(code),
            reset=reset
        )
    
    # --- styles ---
    def bold(self, reset: bool = True) -> "StyleText":
        return self._add('\033[1m', reset)
    
    def dim(self, reset: bool = True) -> "StyleText":
        return self._add('\033[2m', reset)
    
    def italic(self, reset: bool = True) -> "StyleText":
        return self._add('\033[3m', reset)
    
    def underline(self, reset: bool = True) -> "StyleText":
        return self._add('\033[4m', reset)
    
    # --- colors ---
    def red(self, reset: bool = True) -> "StyleText":
        return self._add('\033[31m', reset)
    
    def green(self, reset: bool = True) -> "StyleText":
        return self._add('\033[32m', reset)
    
    def yellow(self, reset: bool = True) -> "StyleText":
        return self._add('\033[33m', reset)
    
    def blue(self, reset: bool = True) -> "StyleText":
        return self._add('\033[34m', reset)
    
    def magenta(self, reset: bool = True) -> "StyleText":
        return self._add('\033[35m', reset)
    
    def cyan(self, reset: bool = True) -> "StyleText":
        return self._add('\033[36m', reset)
    
    def white(self, reset: bool = True) -> "StyleText":
        return self._add('\033[37m', reset)
    
    def __str__(self) -> str:
        if self.reset:
            return f"{self.prefix}{self.text}{self.RESET}"
        return f"{self.prefix}{self.text}"
    
    def __add__(self, other: str) -> "StyleText":
        if not isinstance(other, str):
            return NotImplemented
        
        if self.reset:
            combined = f"{self.prefix}{self.text}{self.RESET}{other}"
            return StyleText(combined, '', reset=False)
        
        return StyleText(
            self.text + other,
            self.prefix,
            reset=False
        )
    
    def __radd__(self, other: str) -> "StyleText":
        if not isinstance(other, str):
            return NotImplemented
        return StyleText(
            self.text,
            other + self.prefix,
            reset=self.reset
        )
