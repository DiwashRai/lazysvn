
from commit_view import CommitView
from svn_model import SvnModel


class CommitPresenter:
    def __init__(self, commit_view, svn_model):
        self._commit_view: CommitView = commit_view
        self._svn_model: SvnModel = svn_model


    def on_view_mount(self) -> None:
        print("commit presenter on view mount")


    def submit_commit(self, commit_message: str):
        try:
            self._commit_view.app.notify(commit_message, title="Committing...")
            self._svn_model.commit_staged(commit_message)
        except Exception as e:
            self._commit_view.app.notify(str(e), title="Error", severity="error")


