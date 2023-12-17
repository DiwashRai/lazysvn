
import os
import argparse

from textual.app import App
from status_view import StatusView
from log_view import LogView


def parse_args():
    parser = argparse.ArgumentParser(
        description="A simple terminal client for Subversion"
    )

    parser.add_argument(
        "-u",
        "--username",
        dest="username",
        type=str,
        help="Subversion username",
    )
    args = parser.parse_args()
    return args


class LazySvn(App):
    BINDINGS = [
        ("1", "switch_mode('status')", "Status"),
        ("2", "switch_mode('log')", "Log"),
        ("q,escape", "quit", "Quit"),
    ]
    MODES = {
        "status": StatusView,
        "log": LogView,
    }

    def on_mount(self) -> None:
        self.switch_mode("status")


def main():
    os.environ["TERM"] = "xterm-256color"
    os.environ["COLORTERM"] = "truecolor"

    # args = parse_args()
    app = LazySvn()
    app.run()


if __name__ == "__main__":
    main()
