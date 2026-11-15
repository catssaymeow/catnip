from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button

from core.tab.constants import CAT_ME_TAB_ID

# top bar button id -> id of the editor tab it opens
TAB_BUTTONS = {"cat-me": CAT_ME_TAB_ID}


class TopBar(Container):
    """
    The top bar: the File menu on the left, the cat me tab on the right.
    """

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        """Create the top bar layout."""
        # each pill wears its own pastel; the tab opener sits at the far end
        yield Horizontal(
            Horizontal(Button("File ▾", id="file-menu",
                              classes="option pill-primary",
                              tooltip="Open a folder or file, or start a new one"),
                       classes="top-bar-group"),
            Horizontal(Button("ᓚᘏᗢ Cat Me", id="cat-me",
                              classes="option pill-bloom",
                              tooltip="Chat with the cat (Ctrl+G)"),
                       classes="top-bar-group top-bar-end"),
            classes="top-bar", )

    def refresh_active(self, tab_id: str | None) -> None:
        """Mark the buttons whose tab is currently showing."""

        for button_id, button_tab_id in TAB_BUTTONS.items():
            self.query_one(f"#{button_id}", Button).set_class(
                button_tab_id == tab_id, "-current")
