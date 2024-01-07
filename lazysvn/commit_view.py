
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Horizontal
from textual.widgets import Footer, Label, TextArea, LoadingIndicator
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
        layers: committing;
    }

    CommitView Widget{
        scrollbar-color: grey;
        scrollbar-color-hover: grey;
        scrollbar-size: 0 1;
        background: #1f1d2e;
    }

    CommitView TextArea {
        width: 85;
        height: 10;
        padding: 0 1;
        border: solid grey;
        opacity: 1 !important;
    }

    CommitView Footer {
        background: #1f1d2e;
    }

    CommitView Footer > .footer--key {
        background: #383838;
    }

    CommitView .committing-indicator {
        width: auto;
        height: auto;
        border: solid grey;
        layer: committing;
    }

    CommitView .committing-indicator.-hidden {
        display: none;
    }

    CommitView LoadingIndicator {
        width: 12;
        height: 1;
        background: #1f1d2e;
        color: grey;
    }
    """

    def __init__(self, svn_model, refresh_status_view, *args, **kwargs):
        from lazysvn.commit_presenter import CommitPresenter
        super().__init__(*args, **kwargs)
        self.title = "Commit"
        self._presenter = CommitPresenter(self, svn_model, refresh_status_view)
        self._text_area: Optional[TextArea] = None
        self._loading_indicator: Optional[Horizontal] = None


    def compose(self) -> ComposeResult:
        yield TextArea()
        with Horizontal(classes="committing-indicator -hidden"):
            yield Label(" Committing...")
            yield LoadingIndicator()
        yield Footer()


    def on_mount(self) -> None:
        self._text_area = self.query_one(TextArea)
        self._committing_indicator = self.query_one(".committing-indicator", Horizontal)
        self._text_area.register_theme(default_theme)
        self._text_area.theme = "default_theme"
        self._text_area.show_line_numbers = False
        self._text_area.border_title = "Commit Message"


    def action_pop_screen(self):
        self.app.pop_screen()


    def action_on_submit(self):
        if not self._text_area:
            return
        self._presenter.on_commit_action()


    @property
    def commit_message(self) -> str:
        if not self._text_area:
            return ""
        return self._text_area.text


    def clear_commit_message(self):
        if not self._text_area:
            return
        self._text_area.text = ""


    def disable_ui(self):
        if not self._committing_indicator or not self._text_area:
            return
        self._committing_indicator.remove_class("-hidden")
        self._text_area.disabled = True


    def enable_ui(self):
        if not self._committing_indicator or not self._text_area:
            return
        self._committing_indicator.add_class("-hidden")
        self._text_area.disabled = False


    def focus_commit_text_input(self):
        if not self._text_area:
            return
        self._text_area.focus()


    def on_key(self, key: Key) -> None:
        if key.key == "escape":
            self.action_pop_screen()

