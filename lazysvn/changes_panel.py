
from textual.app import ComposeResult
from textual.widgets import DataTable
from textual.widget import Widget

class ChangesPanel(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = "Changes"


    def compose(self) -> ComposeResult:
        yield DataTable()

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


    def get_row(self):
        return self._table.get_row_at(self._table.cursor_row)

