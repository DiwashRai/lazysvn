
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Placeholder


class LogView(Screen):
    def compose(self) -> ComposeResult:
        yield Placeholder("Log Screen")
        yield Footer()


    def on_mount(self) -> None:
        print(self.app.screen_stack)
