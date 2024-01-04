
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable
from typing import Optional
from lazysvn.protocols.log_panel import SvnLogPanelProtocol, SvnLogPanelImpl

class SvnLogPanel(Widget):
    def __init__(self, border_title: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = border_title
        self._log_panel_impl: Optional[SvnLogPanelProtocol] = None


    def compose(self) -> ComposeResult:
        yield DataTable(show_header=False, cursor_foreground_priority="renderable")


    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        self._log_panel_impl = SvnLogPanelImpl(table)
        table.cursor_type = "row"


    def set_columns(self, columns) -> None:
        if not self._log_panel_impl:
            raise Exception("LogPanel not mounted")
        self._log_panel_impl.set_columns(columns)


    def set_table_data(self, table_data, sort_col) -> None:
        if not self._log_panel_impl:
            raise Exception("UnstagedPanel not mounted")
        self._log_panel_impl.set_table_data(table_data, sort_col)


    def next_row(self) -> None:
        if not self._log_panel_impl:
            raise Exception("UnstagedPanel not mounted")
        self._log_panel_impl.next_row()


    def prev_row(self) -> None:
        if not self._log_panel_impl:
            raise Exception("UnstagedPanel not mounted")
        self._log_panel_impl.prev_row()
