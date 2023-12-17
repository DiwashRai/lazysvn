
from enum import Enum
from svn_model import Changes
from status_view import StatusView
from typing import List

class StatusPanel(Enum):
    CHANGES = 1
    STAGED = 2


class StatusPresenter:
    def __init__(self, status_view, svn_model):
        self._status_view: StatusView = status_view
        self._selected_panel = StatusPanel.CHANGES
        self._svn_model = svn_model


    def on_view_mount(self):
        self._status_view.select_panel(self._selected_panel)
        self._svn_model.fetch_status()
        self._status_view.set_changes_cols(("Status", "Path"))
        self._status_view.set_staged_cols(("Status", "Path"))
        self.refresh_view()

    
    def refresh_view(self):
        self._status_view.set_changes_panel_data(format_changes(self._svn_model.unstaged_changes))
        self._status_view.set_staged_panel_data(format_changes(self._svn_model.staged_changes))


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


    def on_key_h(self):
        self.toggle_selected_panel()
        self._status_view.select_panel(self._selected_panel)


    def on_key_l(self):
        self.toggle_selected_panel()
        self._status_view.select_panel(self._selected_panel)


    def on_key_space(self):
        if self._selected_panel == StatusPanel.CHANGES:
            row_data = self._status_view.get_changes_row()
            if (row_data is None):
                return
            status = row_data[0]
            filepath = row_data[1]
            if (status == "?"):
                self._svn_model.add_file(filepath)
            self._svn_model.stage_file(filepath)
            self._svn_model.fetch_status()
            self.refresh_view()
        elif self._selected_panel == StatusPanel.STAGED:
            row_data = self._status_view.get_staged_row()
            if (row_data is None):
                return
            status = row_data[0]
            filepath = row_data[1]
            self._svn_model.unstage_file(filepath)
            if (status == "A"):
                self._svn_model.revert_file(filepath)
            self._svn_model.fetch_status()
            self.refresh_view()


    def toggle_selected_panel(self):
        if self._selected_panel == StatusPanel.CHANGES:
            self._selected_panel = StatusPanel.STAGED
        elif self._selected_panel == StatusPanel.STAGED:
            self._selected_panel = StatusPanel.CHANGES


def format_changes(changes: List[Changes]):
    # create list of tuples from changes
    list_of_tuples = []
    for change in changes:
        list_of_tuples.append((change._status, change._path))
    return list_of_tuples
