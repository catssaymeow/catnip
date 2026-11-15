from textual.app import ComposeResult
from textual.containers import Container
from textual.content import Content
from textual.widgets import Button

# rail button id -> id of the side panel it opens
PANEL_BUTTONS = {"file-browser": "file-browser", "customizer": "customizer",
                 "runner": "runner-output"}


class SideBar(Container):
    """
    The sidebar containing the buttons that open side panels: file browser,
    customizer, and runner.
    """

    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        """Create the sidebar layout."""

        # one-cell glyphs, colored by the theme
        yield Container(Button(Content("▤"), id="file-browser",
                               tooltip="Files (Ctrl+B)"),
                        Button(Content("◐"), id="customizer",
                               tooltip="Customize (Ctrl+T)"),
                        Button(Content("▷"), id="runner",
                               tooltip="Runner (Ctrl+L)"),
                        classes="side-button")

    def refresh_active(self, panel_id: str | None) -> None:
        """Mark the button whose panel is currently showing."""

        for button in self.query(Button):
            button.set_class(PANEL_BUTTONS.get(button.id) == panel_id,
                             "-current")
