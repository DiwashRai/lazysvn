
from textual.widgets import DataTable
from rich.text import Text
from typing import Protocol

class SvnLogPanelProtocol(Protocol):
    def set_columns(self, columns) -> None:
        ...

    def set_table_data(self, table_data, sort_col=None) -> None:
        ...

    def next_row(self) -> None:
        ...

    def prev_row(self) -> None:
        ...


class SvnLogPanelImpl(SvnLogPanelProtocol):
    def __init__(self, table: DataTable):
        self._table: DataTable = table


    def set_columns(self, columns) -> None:
        for col in columns:
            self._table.add_column(col, key=col)


    def set_table_data(self, table_data, sort_col=None) -> None:
        self._table.clear()
        self._table.add_rows(table_data)


    def next_row(self) -> None:
        self._table.action_cursor_down()


    def prev_row(self) -> None:
        self._table.action_cursor_up()


