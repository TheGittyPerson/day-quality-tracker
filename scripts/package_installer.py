"""Install project dependencies from ``requirements.txt``."""

from pathlib import Path
import subprocess
import sys


def install_dependencies(
    requirements_file: str | Path = "requirements.txt",
) -> None:
    """Install dependencies listed in the given requirements file."""
    requirements_path = Path(requirements_file)

    if not requirements_path.is_file():
        raise FileNotFoundError(
            f"Requirements file not found: '{requirements_path}'."
        )

    print("\nInstalling third-party dependencies...\n")

    try:
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-r",
                str(requirements_path),
            ]
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "Failed to install dependencies from requirements.txt."
        ) from exc

    print("\nSuccessfully installed dependencies.")
    print("Resuming program...")
    print("\n==============================\n")


if __name__ == "__main__":
    install_dependencies()
