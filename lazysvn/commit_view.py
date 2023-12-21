
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, TextArea
from textual.events import Key
from typing import Optional


class CommitView(Screen):
    BINDINGS = [
        ("escape", "pop_screen", "cancel"),
    ]
    DEFAULT_CSS = """
    CommitView {
        align: center middle;
        background: black 25%;
    }

    CommitView TextArea {
        width: 120;
        height: 10;
        padding: 0 1;
        border: round grey;
        background: $surface;
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = "Commit"
        self._text_area: Optional[TextArea] = None

    def compose(self) -> ComposeResult:
        yield TextArea(theme="dracula")
        yield Footer()


    def on_mount(self) -> None:
        self._text_area = self.query_one(TextArea)
        self._text_area.show_line_numbers = False


    def action_pop_screen(self):
        self.app.pop_screen()


    def on_key(self, key: Key) -> None:
        if key.key == "escape":
            self.action_pop_screen()

