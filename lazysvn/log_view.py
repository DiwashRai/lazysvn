
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Grid
from textual.widgets import Footer, Placeholder
from lazysvn.svn_log_panel import SvnLogPanel


class LogView(Screen):
    BINDINGS = [
        ("▼/j,j", "on_key_down", "next entry"),
        ("▲/k,k", "on_key_up", "prev entry"),
    ]

    DEFAULT_CSS = """
    LogView {
        layout: grid;
        grid-size: 2 1;
    }

    LogView Widget{
        scrollbar-color: grey;
        scrollbar-color-hover: grey;
        scrollbar-background: #1f1d2e;
        scrollbar-corner-color: #1f1d2e;
        scrollbar-size: 1 1;
        background: #1f1d2e;
    }

    LogView Footer > .footer--key {
        background: #383838;
    }

    SvnLogPanel {
        border: solid grey;
    }
    """

    def __init__(self, svn_model, *args, **kwargs):
        from lazysvn.log_presenter import LogPresenter
        super().__init__(*args, **kwargs)
        self.title = "Log"
        self._svn_model = svn_model
        self._presenter = LogPresenter(self, svn_model)

    def compose(self) -> ComposeResult:
        yield SvnLogPanel(border_title="Log")
        with Grid():
            yield Placeholder()
            yield Placeholder()
            yield Placeholder()
        yield Footer()


    def on_mount(self) -> None:
        self._log_panel = self.query_one(SvnLogPanel)


    ############################ Keybindings #############################


    def action_on_key_down(self):
        self._presenter.on_key_down()


    def action_on_key_up(self):
        self._presenter.on_key_up()


    ############################ Logs Panel ##############################


    def set_log_panel_cols(self, cols):
        self._log_panel.set_cols(cols)


    def move_cursor_down(self):
        self._log_panel.next_row()


    def move_cursor_up(self):
        self._log_panel.prev_row()

