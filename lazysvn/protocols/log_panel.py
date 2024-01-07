
from textual.widgets import DataTable
from rich.text import Text
from typing import List, Protocol
from enum import Enum

class SvnLogPanelProtocol(Protocol):
    def set_columns(self, columns) -> None:
        ...

    def set_table_data(self, table_data, sort_col=None) -> None:
        ...

    def next_row(self) -> None:
        ...

    def prev_row(self) -> None:
        ...

    @property
    def rich_row(self) -> List[Text]:
        ...

    def is_focused(self) -> bool:
        ...

    def give_focus(self) -> None:
        ...


class Column(Enum):
    REVISION = 0
    AUTHOR = 1
    DATE = 2
    MESSAGE = 3


class SvnLogPanelImpl(SvnLogPanelProtocol):
    def __init__(self, table: DataTable):
        self._table: DataTable = table


    def set_columns(self, columns) -> None:
        for col in columns:
            self._table.add_column(col, key=col)


    def set_table_data(self, table_data, sort_col=None) -> None:
        prev_idx = self._table.cursor_row
        self._table.clear()
        for row in table_data:
            styled_row: List[Text] = [
                Text(str(row[Column.REVISION.value]), style="#eb6f92"),
                Text(str(row[Column.AUTHOR.value]), style="#9ccfd8"),
                Text(str(row[Column.DATE.value][:10]), style="#8ec07c"),
                Text(str(row[Column.MESSAGE.value]))
            ]

            self._table.add_row(*styled_row)
        self._table.move_cursor(row=prev_idx)


    def next_row(self) -> None:
        self._table.action_cursor_down()


    def prev_row(self) -> None:
        self._table.action_cursor_up()


    @property
    def rich_row(self) -> List[Text]:
        return self._table.get_row_at(self._table.cursor_row)


    def is_focused(self) -> bool:
        return self._table.has_focus


    def give_focus(self) -> None:
        self._table.focus()

