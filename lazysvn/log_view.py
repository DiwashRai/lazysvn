
from typing import Optional
from textual.app import ComposeResult
from textual.widget import Widget
from textual.screen import Screen
from textual.containers import Center, Grid, Horizontal, VerticalScroll
from textual.widgets import DataTable, Footer, Label, LoadingIndicator, Static
from rich.text import Text
from rich.console import RenderableType
from lazysvn.svn_log_panel import SvnLogPanel


class LogView(Screen):
    BINDINGS = [
        ("▼/j,j", "on_key_down", "next entry"),
        ("▲/k,k", "on_key_up", "prev entry"),
    ]

    DEFAULT_CSS = """
    LogView {
        layout: grid;
        grid-size: 2 1;
        grid-columns: 5fr 3fr;
    }

    LogView Widget{
        scrollbar-color: grey;
        scrollbar-color-hover: grey;
        scrollbar-background: #1f1d2e;
        scrollbar-corner-color: #1f1d2e;
        scrollbar-size: 1 1;
        background: #1f1d2e;
    }

    LogView .loading {
        align: center middle;
        height: 95%;
        layer: loading;
        margin: 2;
    }

    .loading.-hidden {
        display: none;
    }

    LogView Horizontal {
        width: auto;
        height: auto;
        border: solid grey;
    }

    LogView LoadingIndicator {
        width: 12;
        height: 1;
        background: #1f1d2e;
        color: grey;
    }

    LogView LoadingIndicator.-hidden {
        display: none;
    }

    LogView Footer > .footer--key {
        background: #383838;
    }

    InfoPanel {
        border: solid grey;
        padding: 1 1;
    }

    LogView VerticalScroll {
        border: solid grey;
        padding: 0 1;
    }

    SvnLogPanel, ChangelistPanel {
        border: solid grey;
    }

    SvnLogPanel DataTable {
        height: 100%;
        scrollbar-size: 0 1;
    }

    SvnLogPanel .datatable--cursor {
        background: #403d52;
    }
    """

    def __init__(self, svn_model, *args, **kwargs):
        from lazysvn.log_presenter import LogPresenter
        super().__init__(*args, **kwargs)
        self.title = "Log"
        self._svn_model = svn_model
        self._presenter = LogPresenter(self, svn_model)

    def compose(self) -> ComposeResult:
        # Main layer
        yield SvnLogPanel(border_title="Log")
        with Grid():
            yield InfoPanel()
            yield VerticalScroll(
                    Static(classes="msg-text"),
                    classes="msg-panel"
            )
            yield ChangelistPanel()
        # Loading layer
        with Center(classes="loading -hidden"):
            with Horizontal():
                yield Label(" Loading...")
                yield LoadingIndicator()
        yield Footer()

    def on_mount(self) -> None:
        self._log_panel = self.query_one(SvnLogPanel)
        self._info_panel = self.query_one(InfoPanel)
        msg_panel = self.query_one(".msg-panel", VerticalScroll)
        msg_panel.border_title = "Message"
        self._msg_text = self.query_one(".msg-text", Static)

        self._loading_indicator = self.query_one(".loading", Center)

        self._presenter.on_view_mount()


    ############################ Keybindings #############################


    def action_on_key_down(self):
        self._presenter.on_key_down()


    def action_on_key_up(self):
        self._presenter.on_key_up()


    ############################ Logs Panel ##############################


    def set_log_panel_cols(self, cols):
        self._log_panel.set_columns(cols)


    def set_log_panel_data(self, data, sort_col):
        self._log_panel.set_table_data(data, sort_col)


    def move_cursor_down(self):
        self._log_panel.next_row()


    def move_cursor_up(self):
        self._log_panel.prev_row()


    def set_log_loading(self, loading: bool):
        if not self._loading_indicator:
            return
        if loading:
            self._loading_indicator.add_class("-hidden")
        else:
            self._loading_indicator.remove_class("-hidden")


    ############################ Info Panel ##############################


    def set_info_text(self, author: str, date: str, message: str):
        self._info_panel.set_info_text(author, date, message)


    ############################ Msg Panel ###############################


    def set_msg_text(self, text: str):
        if not self._msg_text:
            return
        self._msg_text.update(text)


    ######################## Changelist Panel ############################




    ######################### Custom Widgets #############################


class InfoPanel(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = "Info"
        self._author = ""
        self._date = ""
        self._revision = ""

    def render(self) -> RenderableType:
        text = Text()
        text.append(f"Author: {self._author}\n", style="bold")
        text.append(f"Date: {self._date}\n", style="bold")
        text.append(f"Revision: {self._revision}\n", style="bold")
        return text

    def set_info_text(self, author: str, date: str, revision: str):
        self._author = author
        self._date = date
        self._revision = revision


class ChangelistPanel(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = "Changelist"
        self._table: Optional[DataTable] = None


    def compose(self) -> ComposeResult:
        yield DataTable(show_header=False, cursor_foreground_priority="renderable")


    def on_mount(self) -> None:
        self._table = self.query_one(DataTable)
        self._table.add_column("File")


    def set_table_data(self, table_data) -> None:
        if not self._table:
            raise Exception("ChangelistPanel not mounted")
        self._table.clear()
        self._table.add_row(*table_data)


    def next_row(self) -> None:
        if not self._table:
            return
        self._table.action_cursor_down()


    def prev_row(self) -> None:
        if not self._table:
            return
        self._table.action_cursor_up()


    @property
    def row(self) -> str:
        if not self._table or self._table.row_count == 0:
            return ""
        rich_row = self._table.get_row_at(self._table.cursor_row)
        return rich_row[0].plain

