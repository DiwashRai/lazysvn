
from enum import Enum
from lazysvn.log_view import LogView


class LogPanel(Enum):
    LOGS = 1
    MESSAGE = 2
    CHANGELIST = 3


class LogPresenter:
    def __init__(self, log_view, svn_model):
        self._log_view: LogView = log_view
        self._svn_model = svn_model
        self._selected_panel = LogPanel.LOGS


    def on_view_mount(self):
        self._log_view.set_log_panel_cols(("Revision", "Author", "Date", "Message"))
        self.refresh()
        self._log_view.run_worker(self.fetch_log_entries, thread=True)


    def refresh(self):
        pass


    def on_key_down(self):
        self._log_view.move_cursor_down()
        if self._selected_panel == LogPanel.LOGS:
            log_cache_entry = self._svn_model.get_log_cache_entry(self._log_view.selected_revision)
            self._log_view.set_changelist_panel_data(log_cache_entry[1])


    def on_key_up(self):
        self._log_view.move_cursor_up()


    def on_key_left(self):
        self.select_prev_panel()


    def on_key_right(self):
        self.select_next_panel()


    def select_prev_panel(self):
        if self._selected_panel == LogPanel.LOGS:
            self.focus_changelist_panel()
        elif self._selected_panel == LogPanel.MESSAGE:
            self.focus_log_panel()
        elif self._selected_panel == LogPanel.CHANGELIST:
            self.focus_msg_panel()


    def select_next_panel(self):
        if self._selected_panel == LogPanel.LOGS:
            self.focus_msg_panel()
        elif self._selected_panel == LogPanel.MESSAGE:
            self.focus_changelist_panel()
        elif self._selected_panel == LogPanel.CHANGELIST:
            self.focus_log_panel()


    def focus_log_panel(self):
        self._selected_panel = LogPanel.LOGS
        self._log_view.give_log_panel_focus()


    def focus_msg_panel(self):
        self._selected_panel = LogPanel.MESSAGE
        self._log_view.give_msg_panel_focus()


    def focus_changelist_panel(self):
        self._selected_panel = LogPanel.CHANGELIST
        self._log_view.give_changelist_panel_focus()


    def fetch_log_entries(self):
        self._log_view.set_log_loading(True)
        self._svn_model.fetch_log()
        self._log_view.app.call_from_thread(
                self._log_view.set_log_panel_data,
                self._svn_model._log_entries,
                "Revision")
        self._log_view.set_log_loading(False)


