
from textual.widgets import DataTable
from rich.text import Text
from typing import Protocol, Tuple


class SvnStatusPanelProtocol(Protocol):
    def set_columns(self, columns) -> None:
        ...

    def set_table_data(self, table_data) -> None:
        ...

    def next_row(self) -> None:
        ...

    def prev_row(self) -> None:
        ...

    @property
    def row(self) -> Tuple[str, ...]:
        ...

    def is_focused(self) -> bool:
        ...

    def give_focus(self) -> None:
        ...


class SvnStatusPanelImpl(SvnStatusPanelProtocol):
    def __init__(self, table: DataTable):
        self._table: DataTable = table


    def set_columns(self, columns) -> None:
        self._table.add_columns(*columns)


    def set_table_data(self, table_data) -> None:
        prev_idx = self._table.cursor_row
        self._table.clear()
        for row in table_data:
            if row[0] == "M":
                styled_row = [
                    Text(str(cell), style="#f6c177") for cell in row
                ]
            elif row[0] == "A":
                styled_row = [
                    Text(str(cell), style="#8ec07c") for cell in row
                ]
            else:
                styled_row = [
                    Text(str(cell), style="#6e6a86") for cell in row
                ]
            self._table.add_row(*styled_row)
        self._table.move_cursor(row=prev_idx)


    def next_row(self) -> None:
        self._table.action_cursor_down()


    def prev_row(self) -> None:
        self._table.action_cursor_up()


    @property
    def row(self) -> Tuple[str, ...]:
        if self._table.row_count == 0:
            return ("", "")
        rich_row = self._table.get_row_at(self._table.cursor_row)
        return (rich_row[0].plain, rich_row[1].plain)


    def is_focused(self) -> bool:
        return self._table.has_focus


    def give_focus(self) -> None:
        self._table.focus()


    def move_cursor(self, row: int):
        self._table.move_cursor(row=row)

