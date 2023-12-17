
from enum import Enum
from status_view import StatusView

class StatusPanel(Enum):
    CHANGES = 1
    STAGED = 2


class StatusPresenter:
    def __init__(self, status_view):
        self._status_view: StatusView = status_view
        self._selected_panel = StatusPanel.CHANGES


    def on_view_mount(self):
        self._status_view.select_panel(self._selected_panel)


    def on_key_j(self):
        if self._selected_panel == StatusPanel.CHANGES:
            self._status_view.next_change()
        elif self._selected_panel == StatusPanel.STAGED:
            self._status_view.next_staged()


    def on_key_k(self):
        if self._selected_panel == StatusPanel.CHANGES:
            self._status_view.prev_change()
        elif self._selected_panel == StatusPanel.STAGED:
            self._status_view.prev_staged()


    def toggle_selected_panel(self):
        if self._selected_panel == StatusPanel.CHANGES:
            self._selected_panel = StatusPanel.STAGED
        elif self._selected_panel == StatusPanel.STAGED:
            self._selected_panel = StatusPanel.CHANGES


    def on_key_h(self):
        self.toggle_selected_panel()
        self._status_view.select_panel(self._selected_panel)


    def on_key_l(self):
        self.toggle_selected_panel()
        self._status_view.select_panel(self._selected_panel)
