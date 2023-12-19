
from textual.app import ComposeResult
from textual.widgets import DataTable
from textual.widget import Widget

class UnstagedPanel(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = "Unstaged"


    def compose(self) -> ComposeResult:
        yield DataTable(show_header=False, classes = "unstaged_table")

    def on_mount(self) -> None:
        self._table = self.query_one(DataTable)
        self._table.cursor_type = "row"


    def set_columns(self, columns):
        self._table.add_columns(*columns)


    def set_table_data(self, table_data):
        self._table.clear()
        self._table.add_rows(table_data)


    def next_row(self):
        self._table.action_cursor_down()


    def prev_row(self):
        self._table.action_cursor_up()


    @property
    def row_idx(self):
        return self._table.cursor_row


    def get_row(self):
        if self._table.row_count == 0:
            return None
        return self._table.get_row_at(self._table.cursor_row)


    def move_cursor(self, row: int):
        self._table.move_cursor(row=row)

