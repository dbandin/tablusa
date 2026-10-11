"""Command-line entry point for the Textual editor."""

import argparse
from pathlib import Path

from .tui.app import TabnoteApp


def main() -> None:
    parser = argparse.ArgumentParser(prog="tabnote")
    parser.add_argument("path", type=Path)
    parser.add_argument("--instrument", choices=("bass", "guitar"), default="bass")
    arguments = parser.parse_args()
    TabnoteApp(arguments.path, arguments.instrument).run()


if __name__ == "__main__":
    main()
