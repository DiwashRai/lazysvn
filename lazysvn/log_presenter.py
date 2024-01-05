
from lazysvn.log_view import LogView


class LogPresenter:
    def __init__(self, log_view, svn_model):
        self._log_view: LogView = log_view
        self._svn_model = svn_model


    def on_view_mount(self):
        self._log_view.set_log_panel_cols(("Revision", "Author", "Date", "Message"))
        self.refresh()
        self._svn_model.fetch_log()
        self._log_view.set_log_panel_data(self._svn_model._log_entries, "Revision")


    def refresh(self):
        pass


    def on_key_down(self):
        self._log_view.move_cursor_down()


    def on_key_up(self):
        self._log_view.move_cursor_up()
