
from lazysvn.commit_view import CommitView
from lazysvn.svn_model import SvnModel, SVNCommandError


class CommitPresenter:
    def __init__(self, commit_view, svn_model, refresh_status_view):
        self._commit_view: CommitView = commit_view
        self._svn_model: SvnModel = svn_model
        self._refresh_status_view = refresh_status_view


    def on_commit_action(self) -> None:
        self._commit_view.run_worker(self.submit_commit, thread=True)


    def submit_commit(self):
        self._commit_view.disable_ui()
        message = self._commit_view.commit_message
        try:
            self._svn_model.commit_staged(message)
            self._commit_view.clear_commit_message()
            self._commit_view.action_pop_screen()
            self._refresh_status_view()
        except SVNCommandError as e:
            self._commit_view.app.notify(
                    str(e),
                    title="Commit failed",
                    severity="error",
                    timeout=10)
        self._commit_view.enable_ui()
