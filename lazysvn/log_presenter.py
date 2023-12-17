
from log_view import LogView


class LogPresenter:
    def __init__(self, log_view, svn_model):
        self._log_view: LogView = log_view
        self._svn_model = svn_model
