
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Placeholder
from changes_panel import ChangesPanel
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

    .panel {
        border: solid grey;
    }

    .selected-panel {
        border: solid green;
    }

    .diff-panel {
        row-span: 2;
        padding: 1 2;
    }

    .panel DataTable {
        height: 100%;
    }

    .panel .datatable--cursor {
        background: $surface;
    }

    .selected-panel .datatable--cursor {
        background: #505050;
    }
    """

    def __init__(self, svn_model, *args, **kwargs):
        from status_presenter import StatusPresenter
        super().__init__(*args, **kwargs)
        self.title = "Status"
        self._presenter = StatusPresenter(self, svn_model)

        # initalized later in on_mount
        self._changes_panel: Optional[ChangesPanel] = None
        self._staged_panel: Optional[StagedPanel] = None
        self._diff_panel: Optional[DiffPanel] = None


    def compose(self) -> ComposeResult:
        yield ChangesPanel(classes="panel")
        yield DiffPanel(classes="diff-panel")
        yield StagedPanel(classes="panel")
        yield Footer()


    def on_mount(self) -> None:
        self._changes_panel = self.query_one(ChangesPanel)
        self._staged_panel = self.query_one(StagedPanel)
        self._diff_panel = self.query_one(DiffPanel)
        self.app.install_screen(CommitView(), name="commit")
        self._presenter.on_view_mount()


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


    def next_change(self):
        if (self._changes_panel is None):
            return
        self._changes_panel.next_row()


    def prev_change(self):
        if (self._changes_panel is None):
            return
        self._changes_panel.prev_row()


    def next_staged(self):
        if (self._staged_panel is None):
            return
        self._staged_panel.next_row()


    def prev_staged(self):
        if (self._staged_panel is None):
            return
        self._staged_panel.prev_row()


    def select_changes_panel(self):
        if (self._changes_panel is None or self._staged_panel is None):
            return
        self._changes_panel.classes = "selected-panel"
        self._staged_panel.classes = "panel"


    def select_staged_panel(self):
        if (self._staged_panel is None or self._changes_panel is None):
            return
        self._staged_panel.classes = "selected-panel"
        self._changes_panel.classes = "panel"


    def select_panel(self, panel):
        from status_presenter import StatusPanel
        if panel == StatusPanel.CHANGES:
            self.select_changes_panel()
        elif panel == StatusPanel.STAGED:
            self.select_staged_panel()
        else:
            raise ValueError("Unknown panel")


    def set_changes_cols(self, columns):
        if (self._changes_panel is None):
            return
        self._changes_panel.set_columns(columns)


    def set_changes_panel_data(self, table_data):
        if (self._changes_panel is None):
            return
        self._changes_panel.set_table_data(table_data)


    def set_staged_cols(self, columns):
        if (self._staged_panel is None):
            return
        self._staged_panel.set_columns(columns)


    def set_staged_panel_data(self, table_data):
        if (self._staged_panel is None):
            return
        self._staged_panel.set_table_data(table_data)


    def get_changes_row(self):
        if (self._changes_panel is None):
            return
        return self._changes_panel.get_row()


    def get_staged_row(self):
        if (self._staged_panel is None):
            return
        return self._staged_panel.get_row()


    def set_diff_text(self, text):
        if (self._diff_panel is None):
            return
        self.query_one(DiffText).output = text

