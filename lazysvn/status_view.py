
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer
from svn_status_panel import SvnStatusPanel
from diff_panel import DiffPanel, DiffText
from commit_view import CommitView
from typing import Optional, Tuple


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

    StatusView Widget{
        scrollbar-color: grey;
        scrollbar-color-hover: grey;
        scrollbar-size-vertical: 1;
    }

    StatusView DataTable {
        height: 100%;
    }

    .panel {
        border: solid grey;
    }

    .panel.selected {
        border: solid #8ec07c;
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


    def toggle_panel(self):
        print("next panel")
        if not self._unstaged_panel or not self._staged_panel:
            return
        if self._unstaged_panel.is_focused():
            self._staged_panel.give_focus()
        elif self._staged_panel.is_focused():
            self._unstaged_panel.give_focus()


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


    def get_unstaged_row(self) -> Tuple[str, ...]:
        if not self._unstaged_panel:
            return ("", "")
        return self._unstaged_panel.row


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


    def get_staged_row(self) -> Tuple[str, ...]:
        if not self._staged_panel:
            return ("", "")
        return self._staged_panel.row

