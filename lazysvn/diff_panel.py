
from textual.containers import VerticalScroll

class DiffPanel(VerticalScroll):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
