
from typing import Optional
from textual.app import ComposeResult
from textual.widget import Widget
from textual.screen import Screen
from textual.containers import Grid, Horizontal, VerticalScroll
from textual.widgets import DataTable, Footer, Label, LoadingIndicator, Static
from textual.binding import Binding
from rich.text import Text
from rich.console import RenderableType
from lazysvn.svn_log_panel import SvnLogPanel


class LogView(Screen):
    BINDINGS = [
        ("▼/j,j", "on_key_down", "next entry"),
        ("▲/k,k", "on_key_up", "prev entry"),
        ("◄ ►/hl,h,left", "on_key_left", "switch panel"),
        Binding("l,right", "on_key_right", "switch panel", show=False),
        Binding("tab", "on_key_right", "", show=False),
        Binding("shift+tab", "on_key_left", "", show=False),
    ]

    DEFAULT_CSS = """
    LogView {
        align: center middle;
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
        width: auto;
        height: auto;
        border: solid grey;
        layer: loading;
        offset-x: -20vw;
    }

    LogView .loading.-hidden {
        display: none;
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

    SvnLogPanel {
        border: solid grey;
    }

    InfoPanel {
        border: solid grey;
        padding: 1 1;
    }

    .msg-panel {
        border: solid grey;
        padding: 0 1;
    }

    ChangelistPanel {
        border: solid grey;
    }

    ChangelistPanel .datatable--cursor {
        background: #1f1d2e;
    }

    ChangelistPanel .datatable--cursor {
        background: #403d52;
    }

    SvnLogPanel:focus-within,
    ChangelistPanel:focus-within,
    VerticalScroll:focus-within {
        border: solid #8ec07c;
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
        yield SvnLogPanel(border_title="Log")
        with Grid():
            yield InfoPanel()
            yield VerticalScroll(
                    Static(classes="msg-text"),
                    classes="msg-panel"
            )
            yield ChangelistPanel()
        with Horizontal(classes="loading -hidden"):
            yield Label(" Loading...")
            yield LoadingIndicator()
        yield Footer()


    def on_mount(self) -> None:
        self._log_panel = self.query_one(SvnLogPanel)
        self._info_panel = self.query_one(InfoPanel)

        self._msg_panel = self.query_one(".msg-panel", VerticalScroll)
        self._msg_panel.border_title = "Message"
        self._msg_text = self.query_one(".msg-text", Static)

        self._changelist_panel = self.query_one(ChangelistPanel)
        self._loading_indicator = self.query_one(".loading", Horizontal)
        self._presenter.on_view_mount()


    ############################ General ###############################


    def move_cursor_down(self):
        if self._log_panel.is_focused():
            self._log_panel.next_row()
            log_row = self._log_panel.rich_row
            self._info_panel.set_info_text(log_row[1].plain, log_row[2].plain, log_row[0].plain)
            self._msg_text.update(log_row[3].plain)
        if self._changelist_panel.is_focused():
            self._changelist_panel.next_row()


    def move_cursor_up(self):
        if self._log_panel.is_focused():
            self._log_panel.prev_row()
            log_row = self._log_panel.rich_row
            self._info_panel.set_info_text(log_row[1].plain, log_row[2].plain, log_row[0].plain)
            self._msg_text.update(log_row[3].plain)
        if self._changelist_panel.is_focused():
            self._changelist_panel.prev_row()


    ############################ Keybindings #############################


    def action_on_key_down(self):
        self._presenter.on_key_down()


    def action_on_key_up(self):
        self._presenter.on_key_up()


    def action_on_key_left(self):
        self._presenter.on_key_left()


    def action_on_key_right(self):
        self._presenter.on_key_right()


    ############################ Logs Panel ##############################


    def set_log_panel_cols(self, cols):
        self._log_panel.set_columns(cols)


    def set_log_panel_data(self, data, sort_col):
        self._log_panel.set_table_data(data, sort_col)


    def give_log_panel_focus(self):
        self._log_panel.give_focus()


    def set_log_loading(self, loading: bool):
        if not self._loading_indicator:
            return
        if loading:
            self._loading_indicator.remove_class("-hidden")
        else:
            self._loading_indicator.add_class("-hidden")


    @property
    def selected_revision(self) -> int:
        return int(self._log_panel.rich_row[0].plain)


    ############################ Info Panel ##############################


    def set_info_text(self, author: str, date: str, revision: str):
        self._info_panel.set_info_text(author, date, revision)


    ############################ Msg Panel ###############################


    def set_msg_text(self, text: str):
        if not self._msg_text:
            return
        self._msg_text.update(text)


    def give_msg_panel_focus(self):
        if not self._msg_panel:
            return
        self._msg_panel.focus()


    ######################## Changelist Panel ############################


    def set_changelist_panel_data(self, table_data):
        self._changelist_panel.set_table_data(table_data)


    def give_changelist_panel_focus(self):
        self._changelist_panel.give_focus()


    ######################### Custom Widgets #############################


class InfoPanel(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = "Info"
        self._author = ""
        self._date = ""
        self._revision = ""

    def render(self) -> RenderableType:
        grey = "#908caa"
        text = Text()
        text.append(f"Author: ", style=grey)
        text.append(f"{self._author}\n")
        text.append(f"Date: ", style=grey)
        text.append(f"{self._date}\n")
        text.append(f"Revision: ", style=grey)
        text.append(f"{self._revision}\n")
        return text

    def set_info_text(self, author: str, date: str, revision: str):
        self._author = author
        self._date = date
        self._revision = revision
        self.refresh()


class ChangelistPanel(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border_title = "Changelist"
        self._table: Optional[DataTable] = None


    def compose(self) -> ComposeResult:
        yield DataTable(show_header=False, cursor_foreground_priority="renderable")


    def on_mount(self) -> None:
        self._table = self.query_one(DataTable)
        self._table.cursor_type = "row"
        self._table.add_column("Status")
        self._table.add_column("File")


    def set_table_data(self, table_data) -> None:
        if not self._table:
            raise Exception("ChangelistPanel not mounted")
        self._table.clear()
        for entry in table_data:
            row = [entry[0], entry[1]]
            self._table.add_row(*row)


    def next_row(self) -> None:
        if not self._table:
            return
        print("changelist next row")
        self._table.action_cursor_down()


    def prev_row(self) -> None:
        if not self._table:
            return
        print("changelist prev row")
        self._table.action_cursor_up()


    @property
    def row(self) -> str:
        if not self._table or self._table.row_count == 0:
            return ""
        rich_row = self._table.get_row_at(self._table.cursor_row)
        return rich_row[0].plain


    def is_focused(self) -> bool:
        if not self._table:
            return False
        return self._table.has_focus


    def give_focus(self) -> None:
        if not self._table:
            return
        self._table.focus()

