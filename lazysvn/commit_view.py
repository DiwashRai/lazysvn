
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, TextArea
from textual.widgets.text_area import TextAreaTheme
from textual.events import Key
from rich.style import Style
from typing import Optional


default_theme = TextAreaTheme(
    name="default_theme",
    base_style=Style(bgcolor="#1f1d2e"),
    cursor_style=Style(color="white", bgcolor="#505050"),
    cursor_line_style=Style(bgcolor="#1f1d2e"),
)


class CommitView(Screen):
    BINDINGS = [
        ("escape", "pop_screen", "cancel"),
        ("ctrl+s", "on_submit", "Submit svn commit"),
    ]
    DEFAULT_CSS = """
    CommitView {
        align: center middle;
        background: #1f1d2e 0%;
    }

    CommitView Label {
        background: #1f1d2e;
    }

    CommitView TextArea {
        width: 120;
        height: 10;
        padding: 0 1;
        border: round grey;
    }

    CommitView Footer {
        background: #1f1d2e;
    }

    CommitView Footer > .footer--key {
        background: #383838;
    }

    """

    def __init__(self, svn_model, *args, **kwargs):
        from commit_presenter import CommitPresenter
        super().__init__(*args, **kwargs)
        self.title = "Commit"
        self._presenter = CommitPresenter(self, svn_model)
        self._text_area: Optional[TextArea] = None


    def compose(self) -> ComposeResult:
        yield TextArea()
        yield Footer()


    def on_mount(self) -> None:
        self._text_area = self.query_one(TextArea)
        self._text_area.register_theme(default_theme)
        self._text_area.theme = "default_theme"
        self._text_area.show_line_numbers = False
        self._text_area.border_title = "Commit Message"


    def action_pop_screen(self):
        self.app.pop_screen()


    def action_on_submit(self):
        if not self._text_area:
            return
        self._presenter.submit_commit(self._text_area.text)


    def on_key(self, key: Key) -> None:
        if key.key == "escape":
            self.action_pop_screen()

