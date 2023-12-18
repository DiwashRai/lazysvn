
from textual.containers import VerticalScroll
from textual.app import ComposeResult
from textual.widget import Widget
from textual.reactive import reactive


class DiffText(Widget):
    output = reactive("")

    def render(self) -> str:
        return self.output


class DiffPanel(VerticalScroll):
    DEFAULT_CSS = """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def compose(self) -> ComposeResult:
        yield DiffText()

