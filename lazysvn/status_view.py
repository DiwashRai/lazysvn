
from textual import on
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, RichLog, DataTable
from textual.binding import Binding
from textual.containers import Grid
from lazysvn.svn_status_panel import SvnStatusPanel
from lazysvn.diff_panel import DiffPanel, DiffText
from lazysvn.commit_view import CommitView
from typing import Optional, Tuple
from rich.text import Text


class StatusView(Screen):
    BINDINGS = [
        ("c", "on_key_c", "commit"),
        ("▼/j,j", "on_key_down", "next entry"),
        ("▲/k,k", "on_key_up", "prev entry"),
        ("◄ ►/hl,h,left", "on_key_left", "switch panel"),
        Binding("l,right", "on_key_right", "switch panel", show=False),
        Binding("tab,shift+tab", "on_key_left", "", show=False),
        ("space", "key_space", "stage/unstage"),
        ("t", "on_key_t", "toggle unversioned"),
    ]

    DEFAULT_CSS = """
    StatusView {
        layout: grid;
        grid-size: 2 1;
        grid-columns: 3fr 5fr;
    }

    StatusView .changes-grid {
        layout: grid;
        grid-size: 1 2;
    }

    StatusView .output-grid {
        layout: grid;
        grid-size: 1 2;
        grid-rows: 85% 15%;
    }

    StatusView Widget{
        scrollbar-color: grey;
        scrollbar-color-hover: grey;
        scrollbar-background: #1f1d2e;
        scrollbar-corner-color: #1f1d2e;
        scrollbar-size: 1 1;
        background: #1f1d2e;
    }

    StatusView Footer > .footer--key {
        background: #383838;
    }

    StatusView DataTable {
        height: 100%;
    }

    .panel {
        border: solid grey;
    }

    .panel:focus-within {
        border: solid #8ec07c;
    }

    .panel:focus-within .datatable--cursor {
        border: solid #8ec07c;
        background: #403d52;
    }

    .panel .datatable--cursor {
        background: #1f1d2e;
    }

    .diff-panel {
        padding: 1 2;
    }

    .cmd-panel {
        border: solid grey;
        scrollbar-size: 0 1;
    }
    """

    def __init__(self, svn_model, *args, **kwargs):
        from lazysvn.status_presenter import StatusPresenter
        super().__init__(*args, **kwargs)
        self.title = "Status"
        self._svn_model = svn_model
        self._presenter = StatusPresenter(self, svn_model)

        # initalized later in on_mount
        self._unstaged_panel: Optional[SvnStatusPanel] = None
        self._staged_panel: Optional[SvnStatusPanel] = None
        self._diff_panel: Optional[DiffPanel] = None


    def compose(self) -> ComposeResult:
        with Grid(classes="changes-grid"):
            yield SvnStatusPanel(classes="panel", border_title="Unstaged", id="unstaged")
            yield SvnStatusPanel(classes="panel", border_title="Staged", id="staged")
        with Grid(classes="output-grid"):
            yield DiffPanel(classes="diff-panel")
            yield RichLog(classes="cmd-panel", wrap=True)
        yield Footer()


    def on_mount(self) -> None:
        self._unstaged_panel = self.query_one("#unstaged", SvnStatusPanel)
        self._staged_panel = self.query_one("#staged", SvnStatusPanel)
        self._diff_panel = self.query_one(DiffPanel)
        self._diff_panel.can_focus = False
        self._cmd_log = self.query_one(RichLog)
        self._cmd_log.border_title = "Command Log"
        self._cmd_log.can_focus = False
        self.app.install_screen(
                CommitView(self._svn_model, refresh_status_view=self.action_refresh),
                name="commit",
        )
        self._presenter.on_view_mount()


    ############################ Keybindings #############################


    def action_on_key_left(self):
        self._presenter.on_key_left()


    def action_on_key_down(self):
        self._presenter.on_key_down()


    def action_on_key_up(self):
        self._presenter.on_key_up()


    def action_on_key_right(self):
        self._presenter.on_key_right()


    def action_key_space(self):
        self._presenter.on_key_space()


    def action_on_key_c(self):
        self._presenter.on_key_c()


    def action_on_key_t(self):
        self._presenter.on_key_t()


    ############################ General ###############################


    def move_cursor_down(self):
        if not self._unstaged_panel or not self._staged_panel:
            return
        if self._unstaged_panel.is_focused():
            self._unstaged_panel.next_row()
        elif self._staged_panel.is_focused():
            self._staged_panel.next_row()


    def move_cursor_up(self):
        if not self._unstaged_panel or not self._staged_panel:
            return
        if self._unstaged_panel.is_focused():
            self._unstaged_panel.prev_row()
        elif self._staged_panel.is_focused():
            self._staged_panel.prev_row()


    def on_data_table_row_highlighted(self):
        self._presenter.on_row_highlighted()


    def action_refresh(self):
        self._presenter.refresh()


    ########################## unstaged panel ############################


    def select_unstaged_panel(self):
        if not self._unstaged_panel or not self._staged_panel:
            return
        self._unstaged_panel.give_focus()


    def set_unstaged_cols(self, columns):
        if not self._unstaged_panel:
            return
        self._unstaged_panel.set_columns(columns)


    def set_unstaged_panel_data(self, table_data, sort_col=None):
        if not self._unstaged_panel:
            return
        self._unstaged_panel.set_table_data(table_data, sort_col)


    def get_unstaged_row(self) -> Tuple[str, ...]:
        if not self._unstaged_panel:
            return ("", "")
        return self._unstaged_panel.row


    ########################### staged panel #############################


    def select_staged_panel(self):
        if not self._unstaged_panel or not self._staged_panel:
            return
        self._staged_panel.give_focus()


    def set_staged_cols(self, columns):
        if not self._staged_panel:
            return
        self._staged_panel.set_columns(columns)


    def set_staged_panel_data(self, table_data, sort_col=None):
        if not self._staged_panel:
            return
        self._staged_panel.set_table_data(table_data, sort_col)


    def get_staged_row(self) -> Tuple[str, ...]:
        if not self._staged_panel:
            return ("", "")
        return self._staged_panel.row


    ########################### diff panel ##############################


    def set_diff_text(self, text):
        if not self._diff_panel:
            return
        self.query_one(DiffText).output = text


    ########################## command panell ############################


    def append_command_log(self, commands: list[str]):
        if not self._cmd_log or len(commands) == 0:
            return
        text = Text()
        text.append("cmd: ", style="#f6c177")
        text.append(commands[0])
        for command in commands[1:]:
            text.append("\ncmd: ", style="#f6c177")
            text.append(command)
        self._cmd_log.write(text)


