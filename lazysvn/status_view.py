
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer
from textual.binding import Binding
from svn_status_panel import SvnStatusPanel
from diff_panel import DiffPanel, DiffText
from commit_view import CommitView
from typing import Optional, Tuple


class StatusView(Screen):
    BINDINGS = [
        ("c", "on_key_c", "commit"),
        ("▼/j,j", "on_key_down", "next entry"),
        ("▲/k,k", "on_key_up", "prev entry"),
        ("◄ ►/hl,h,left", "on_key_left", "switch panel"),
        Binding("l,right", "on_key_right", "switch panel", show=False),
        Binding("tab,shift+tab", "on_key_left", "", show=False),
        ("space", "key_space", "stage/unstage"),
    ]

    DEFAULT_CSS = """
    StatusView {
        layout: grid;
        grid-size: 2;
    }

    StatusView Widget{
        scrollbar-color: grey;
        scrollbar-color-hover: grey;
        scrollbar-size: 1 1;
    }

    StatusView Footer {
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
        background: #1f1d2e;
    }

    .panel.selected {
        border: solid #8ec07c;
    }

    .panel .datatable--cursor {
        background: #1f1d2e;
    }

    .panel.selected .datatable--cursor {
        background: #403d52;
    }

    .diff-panel {
        row-span: 2;
        padding: 1 2;
        background: #1f1d2e;
    }
    """

    def __init__(self, svn_model, *args, **kwargs):
        from status_presenter import StatusPresenter
        super().__init__(*args, **kwargs)
        self.title = "Status"
        self._svn_model = svn_model
        self._presenter = StatusPresenter(self, svn_model)

        # initalized later in on_mount
        self._unstaged_panel: Optional[SvnStatusPanel] = None
        self._staged_panel: Optional[SvnStatusPanel] = None
        self._diff_panel: Optional[DiffPanel] = None


    def compose(self) -> ComposeResult:
        yield SvnStatusPanel(classes="panel", border_title="Unstaged", id="unstaged")
        yield DiffPanel(classes="diff-panel")
        yield SvnStatusPanel(classes="panel", border_title="Staged", id="staged")
        yield Footer()


    def on_mount(self) -> None:
        self._unstaged_panel = self.query_one("#unstaged", SvnStatusPanel)
        self._staged_panel = self.query_one("#staged", SvnStatusPanel)
        self._diff_panel = self.query_one(DiffPanel)
        self._diff_panel.can_focus = False
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


    def set_diff_text(self, text):
        if not self._diff_panel:
            return
        self.query_one(DiffText).output = text


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
        self._unstaged_panel.add_class("selected")
        self._unstaged_panel.give_focus()
        self._staged_panel.remove_class("selected")


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
        self._staged_panel.add_class("selected")
        self._staged_panel.give_focus()
        self._unstaged_panel.remove_class("selected")


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

