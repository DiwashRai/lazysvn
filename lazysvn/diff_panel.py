
from textual.containers import VerticalScroll

class DiffPanel(VerticalScroll):
    def __init__(self, classes: str):
        super().__init__(classes=classes)
