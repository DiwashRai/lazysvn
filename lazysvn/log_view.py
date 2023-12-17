
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Placeholder


class LogView(Screen):
    def __init__(self, svn_model, *args, **kwargs):
        from log_presenter import LogPresenter
        super().__init__(*args, **kwargs)
        self._presenter = LogPresenter(self, svn_model)

    def compose(self) -> ComposeResult:
        yield Placeholder("Log Screen")
        yield Footer()


    def on_mount(self) -> None:
        print(self.app.screen_stack)
