
from commit_view import CommitView
from svn_model import SvnModel


class CommitPresenter:
    def __init__(self, commit_view, svn_model):
        self._commit_view: CommitView = commit_view
        self._svn_model: SvnModel = svn_model


    def submit_commit(self, commit_message: str) -> None:
        self._commit_view.app.notify("lorem ipsum", title="Comitting...")
        self._commit_view.run_worker(self.sleep_then_notify(commit_message), thread=True)


    async def sleep_then_notify(self, message: str) -> None:
        import time
        time.sleep(2)
        self._commit_view.app.notify(message, title="Success")


