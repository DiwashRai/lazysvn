
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Placeholder
from unstaged_panel import UnstagedPanel
from staged_panel import StagedPanel
from diff_panel import DiffPanel, DiffText
from typing import Optional


class CommitView(Screen):
    BINDINGS = [
        ("escape", "pop_screen", "cancel"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = "Commit"

    def compose(self) -> ComposeResult:
        yield Placeholder("Commit Screen")
        yield Footer()


    def action_pop_screen(self):
        self.app.pop_screen()


class StatusView(Screen):
    BINDINGS = [
        ("c", "push_screen('commit')", "commit"),
        ("▲▼/jk", "", "navigate entries"), # hack to populate footer
        ("◄ ►/hl", "_", "navigate panels"),
        ("space", "key_space", "stage/unstage"),
    ]

    DEFAULT_CSS = """
    StatusView {
        layout: grid;
        grid-size: 2;
    }

    StatusView DataTable {
        height: 100%;
    }

    .panel {
        border: solid grey;
    }

    .panel.selected {
        border: solid green;
    }

    .panel .datatable--cursor {
        background: $surface;
    }

    .panel.selected .datatable--cursor {
        background: #505050;
    }

    .diff-panel {
        row-span: 2;
        padding: 1 2;
    }

    """

    def __init__(self, svn_model, *args, **kwargs):
        from status_presenter import StatusPresenter
        super().__init__(*args, **kwargs)
        self.title = "Status"
        self._presenter = StatusPresenter(self, svn_model)

        # initalized later in on_mount
        self._unstaged_panel: Optional[UnstagedPanel] = None
        self._staged_panel: Optional[StagedPanel] = None
        self._diff_panel: Optional[DiffPanel] = None


    def compose(self) -> ComposeResult:
        yield UnstagedPanel(classes="panel")
        yield DiffPanel(classes="diff-panel")
        yield StagedPanel(classes="panel")
        yield Footer()


    def on_mount(self) -> None:
        self._unstaged_panel = self.query_one(UnstagedPanel)
        self._staged_panel = self.query_one(StagedPanel)
        self._diff_panel = self.query_one(DiffPanel)
        self.app.install_screen(CommitView(), name="commit")
        self._presenter.on_view_mount()

    ############################ Keybindings #############################

    def key_h(self):
        self._presenter.on_key_h()


    def key_j(self):
        self._presenter.on_key_j()


    def key_k(self):
        self._presenter.on_key_k()


    def key_l(self):
        self._presenter.on_key_l()


    def action_key_space(self):
        self._presenter.on_key_space()


    def set_diff_text(self, text):
        if not self._diff_panel:
            return
        self.query_one(DiffText).output = text



    ########################## unstaged panel ############################


    def next_unstaged(self):
        if (self._unstaged_panel is None):
            return
        self._unstaged_panel.next_row()


    def prev_unstaged(self):
        if not self._unstaged_panel:
            return
        self._unstaged_panel.prev_row()


    def select_unstaged_panel(self):
        if not self._unstaged_panel or not self._staged_panel:
            return
        self._unstaged_panel.add_class("selected")
        self._staged_panel.remove_class("selected")


    def set_unstaged_cols(self, columns):
        if not self._unstaged_panel:
            return
        self._unstaged_panel.set_columns(columns)


    def set_unstaged_panel_data(self, table_data):
        if not self._unstaged_panel:
            return
        self._unstaged_panel.set_table_data(table_data)


    @property
    def unstaged_row_idx(self) -> int:
        if not self._unstaged_panel:
            return 0
        return self._unstaged_panel.row_idx


    def get_unstaged_row(self):
        if not self._unstaged_panel:
            return
        return self._unstaged_panel.get_row()


    def move_unstaged_cursor(self, row: int):
        if not self._unstaged_panel:
            return
        self._unstaged_panel.move_cursor(row)


    ########################### staged panel #############################


    def next_staged(self):
        if not self._staged_panel:
            return
        self._staged_panel.next_row()


    def prev_staged(self):
        if not self._staged_panel:
            return
        self._staged_panel.prev_row()


    def select_staged_panel(self):
        if not self._unstaged_panel or not self._staged_panel:
            return
        self._staged_panel.add_class("selected")
        self._unstaged_panel.remove_class("selected")


    def set_staged_cols(self, columns):
        if not self._staged_panel:
            return
        self._staged_panel.set_columns(columns)


    def set_staged_panel_data(self, table_data):
        if not self._staged_panel:
            return
        self._staged_panel.set_table_data(table_data)


    @property
    def staged_row_idx(self) -> int:
        if not self._staged_panel:
            return 0
        return self._staged_panel.row_idx


    def get_staged_row(self):
        if not self._staged_panel:
            return
        return self._staged_panel.get_row()


    def move_staged_cursor(self, row: int):
        if not self._staged_panel:
            return
        self._staged_panel.move_cursor(row)

