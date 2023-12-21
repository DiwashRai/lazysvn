
from enum import Enum
from svn_model import Changes
from status_view import StatusView
from typing import List, Tuple

class StatusPanel(Enum):
    UNSTAGED = 1
    STAGED = 2


class StatusPresenter:
    def __init__(self, status_view, svn_model):
        self._status_view: StatusView = status_view
        self._svn_model = svn_model
        self._selected_panel = StatusPanel.UNSTAGED


    def on_view_mount(self):
        self._status_view.set_unstaged_cols(("Status", "Path"))
        self._status_view.set_staged_cols(("Status", "Path"))
        self.update_selected_panel()
        self._svn_model.refresh()
        self.reset_view_data()


    def update_selected_panel(self):
        if self._selected_panel == StatusPanel.UNSTAGED:
            self._status_view.select_unstaged_panel()
        elif self._selected_panel == StatusPanel.STAGED:
            self._status_view.select_staged_panel()


    def reset_view_data(self):
        self._status_view.set_unstaged_panel_data(format_changes(self._svn_model.unstaged_changes))
        self._status_view.set_staged_panel_data(format_changes(self._svn_model.staged_changes))
        self.update_diff_out()


    def update_diff_out(self):
        row: Tuple[str, ...] = self.get_selected_row()
        if row[0] == "?" or row[1] == "":
            self._status_view.set_diff_text("")
            return
        filepath = row[1]
        self._status_view.set_diff_text(self._svn_model.diff_file(filepath))


    def on_key_j(self):
        if self._selected_panel == StatusPanel.UNSTAGED:
            self._status_view.next_unstaged()
        elif self._selected_panel == StatusPanel.STAGED:
            self._status_view.next_staged()
        self.update_diff_out()


    def on_key_k(self):
        if self._selected_panel == StatusPanel.UNSTAGED:
            self._status_view.prev_unstaged()
        elif self._selected_panel == StatusPanel.STAGED:
            self._status_view.prev_staged()
        self.update_diff_out()


    def on_key_h(self):
        self.toggle_selected_panel()
        self.update_selected_panel()
        self.update_diff_out()


    def on_key_l(self):
        self.toggle_selected_panel()
        self.update_selected_panel()
        self.update_diff_out()


    def on_key_space(self):
        if self._selected_panel == StatusPanel.UNSTAGED:
            row_data = self._status_view.get_unstaged_row()
            if (row_data is None):
                return
            status = row_data[0]
            filepath = row_data[1]
            if (status == "?"):
                self._svn_model.add_file(filepath)
            self._svn_model.stage_file(filepath)
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
        self.reset_view_data()


    def toggle_selected_panel(self):
        if self._selected_panel == StatusPanel.UNSTAGED:
            self._selected_panel = StatusPanel.STAGED
        elif self._selected_panel == StatusPanel.STAGED:
            self._selected_panel = StatusPanel.UNSTAGED


    def get_selected_row(self) -> Tuple[str, ...]:
        if self._selected_panel == StatusPanel.UNSTAGED:
             return self._status_view.get_unstaged_row()
        elif self._selected_panel == StatusPanel.STAGED:
             return self._status_view.get_staged_row()
        return ("", "")


def format_changes(changes: List[Changes]):
    # create list of tuples from changes
    list_of_tuples = []
    for change in changes:
        list_of_tuples.append((change._status, change._path))
    return list_of_tuples
