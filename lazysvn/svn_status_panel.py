
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable
from typing import Optional, Tuple
from lazysvn.protocols.status_panel import SvnStatusPanelProtocol, SvnStatusPanelImpl


class SvnStatusPanel(Widget):
    def __init__(self, border_title: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = border_title
        self._status_panel_impl: Optional[SvnStatusPanelProtocol] = None


    def compose(self) -> ComposeResult:
        yield DataTable(show_header=False, cursor_foreground_priority="renderable")


    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        self._status_panel_impl = SvnStatusPanelImpl(table)
        table.cursor_type = "row"


    def set_columns(self, columns) -> None:
        if not self._status_panel_impl:
            raise Exception("UnstagedPanel not mounted")
        self._status_panel_impl.set_columns(columns)


    def set_table_data(self, table_data, sort_col) -> None:
        if not self._status_panel_impl:
            raise Exception("UnstagedPanel not mounted")
        self._status_panel_impl.set_table_data(table_data, sort_col)


    def next_row(self) -> None:
        if not self._status_panel_impl:
            raise Exception("UnstagedPanel not mounted")
        self._status_panel_impl.next_row()


    def prev_row(self) -> None:
        if not self._status_panel_impl:
            raise Exception("UnstagedPanel not mounted")
        self._status_panel_impl.prev_row()


    @property
    def row(self) -> Tuple[str, ...]:
        if not self._status_panel_impl:
            raise Exception("UnstagedPanel not mounted")
        return self._status_panel_impl.row


    def is_focused(self) -> bool:
        if not self._status_panel_impl:
            raise Exception("UnstagedPanel not mounted")
        return self._status_panel_impl.is_focused()


    def give_focus(self) -> None:
        if not self._status_panel_impl:
            raise Exception("UnstagedPanel not mounted")
        self._status_panel_impl.give_focus()

