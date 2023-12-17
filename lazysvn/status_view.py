
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer
from changes_panel import ChangesPanel
from staged_panel import StagedPanel
from diff_panel import DiffPanel
from typing import Optional


class StatusView(Screen):
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

    .diff {
        row-span: 2;
    }
    """
    def __init__(self, *args, **kwargs):
        from status_presenter import StatusPresenter
        super().__init__(*args, **kwargs)
        self.title = "Status"
        self._presenter = StatusPresenter(self)

        # initalized later in on_mount
        self._changes_panel: Optional[ChangesPanel] = None
        self._staged_panel: Optional[StagedPanel] = None
        self._diff_panel: Optional[DiffPanel] = None


    def compose(self) -> ComposeResult:
        yield ChangesPanel(classes="panel")
        yield DiffPanel(classes="diff")
        yield StagedPanel(classes="panel")
        yield Footer()


    def on_mount(self) -> None:
        self._changes_panel = self.query_one(ChangesPanel)
        self._staged_panel = self.query_one(StagedPanel)
        self._diff_panel = self.query_one(DiffPanel)
        self._presenter.on_view_mount()


    def key_h(self):
        self._presenter.on_key_h()


    def key_j(self):
        self._presenter.on_key_j()


    def key_k(self):
        self._presenter.on_key_k()


    def key_l(self):
        self._presenter.on_key_l()


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
