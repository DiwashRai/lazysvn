
import os
import argparse

from textual.app import App
from lazysvn.status_view import StatusView
from lazysvn.log_view import LogView
from lazysvn.svn_model import SvnModel


def parse_args():
    parser = argparse.ArgumentParser(
        description="A simple terminal client for Subversion"
    )

    parser.add_argument(
        "path",
        metavar="PATH",
        type=str,
        nargs="?",
        default=os.getcwd(),
        help="Path to local Subversion repository",
    )

    parser.add_argument(
        "-u",
        "--username",
        dest="username",
        default=None,
        type=str,
        help="Subversion username",
    )

    parser.add_argument(
        "-p",
        "--password",
        dest="password",
        default=None,
        type=str,
        help="Subversion password",
    )
    args = parser.parse_args()
    return args


class LazySvn(App):
    BINDINGS = [
        ("1", "switch_mode('status')", "Status"),
        ("2", "switch_mode('log')", "Log"),
        ("q", "quit", "Quit"),
    ]
    def __init__(self, svn_model: SvnModel):
        super().__init__()
        self._svn_model = svn_model
        self.add_mode("status", StatusView(svn_model))
        self.add_mode("log", LogView(svn_model))

    def on_mount(self) -> None:
        self.switch_mode("status")


def main():
    os.environ["TERM"] = "xterm-256color"
    os.environ["COLORTERM"] = "truecolor"
    args = parse_args()

    svn_model = SvnModel(
        local_path=args.path,
        username=args.username,
        password=args.password,
    )

    app = LazySvn(svn_model)
    app.run()


if __name__ == "__main__":
    main()

