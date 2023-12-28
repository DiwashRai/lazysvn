
from textual.containers import VerticalScroll
from textual.app import ComposeResult
from textual.widget import Widget
from textual.reactive import reactive
from rich.text import Text
from rich.console import RenderableType


class DiffText(Widget):
    output = reactive("")

    def render(self) -> RenderableType:
        text = Text()
        for line in self.output.splitlines():
            if line.startswith("+"):
                text.append(line + "\n", style="#8ec07c")
            elif line.startswith("-"):
                text.append(line + "\n", style="#eb6f92")
            elif line.startswith("@"):
                text.append(line + "\n", style="#56949f")
            else:
                text.append(line + "\n")
        return text


class DiffPanel(VerticalScroll):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def compose(self) -> ComposeResult:
        yield DiffText()

