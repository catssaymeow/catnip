from enum import Enum
from typing import TYPE_CHECKING

from ui.constants import WIDTH_SCALES, DEFAULT_SIDE_PANEL_WIDTH_PERCENTAGE
from ui.sidebar.sidebar import SideBar
from ui.topbar.top_bar import TopBar

if TYPE_CHECKING:
    from app.entry import CatnipApp


class SidePanelId(Enum):
    FILE_BROWSER = "file-browser"
    CUSTOMIZER = "customizer"
    RUNNER_OUTPUT = "runner-output"


class LayoutController:
    """Control layout changes for the side panel and top bar based on user actions."""

    def __init__(self, app: "CatnipApp"):
        self.app = app
        self.side_panel_width_percentage = DEFAULT_SIDE_PANEL_WIDTH_PERCENTAGE

    def show_side_panel(self, panel_id: SidePanelId,
                        min_width: float = 0) -> None:
        """
        Display the given side panel, keeping the width the user chose.
        A hidden panel opens at the default width.

        @Args:
            min_width: widen to at least this share of the screen (a WIDTH_SCALES step).
        """

        side_panel = self._get_side_panel()
        side_panel.current = panel_id.value
        if not side_panel.display:
            self.side_panel_width_percentage = DEFAULT_SIDE_PANEL_WIDTH_PERCENTAGE
        side_panel.display = True
        self.side_panel_width_percentage = max(self.side_panel_width_percentage,
                                               min_width)
        self._apply_layout()

    def adjust_side_panel(self, reduce: bool = True) -> None:
        """Increase or decrease the side panel width based on predefined scales."""

        index = WIDTH_SCALES.index(self.side_panel_width_percentage)
        next_index = index - 1 if reduce else index + 1

        if 0 <= next_index < len(WIDTH_SCALES):
            self.side_panel_width_percentage = WIDTH_SCALES[next_index]

        side_panel = self._get_side_panel()
        side_panel.display = self.side_panel_width_percentage != min(
            WIDTH_SCALES)

        self._apply_layout()

    def hide_top_bar(self) -> None:
        """Hide the top bar and expand the main screen area."""

        self.app.query_one(".top-bar").display = False
        self.app.query_one(".main-screen").add_class("expanded")

    def show_top_bar(self) -> None:
        """Show the top bar and restore the main screen layout."""

        self.app.query_one(".top-bar").display = True
        self.app.query_one(".main-screen").remove_class("expanded")

    def _apply_layout(self) -> None:
        """Apply the current side panel width to the layout."""

        side_panel = self._get_side_panel()
        tabbed_editor = self.app.query_one(".tabbed-editor")

        if not side_panel.display:
            # Keep the icon rail visible and let the editor fill only the
            # horizontal space that remains after it.
            tabbed_editor.styles.width = "1fr"
        else:
            # Relative widths keep the layout fluid when the terminal is resized.
            side_panel.styles.width = f"{self.side_panel_width_percentage:.0%}"
            tabbed_editor.styles.width = "1fr"

        self._keep_focus_visible(side_panel, tabbed_editor)
        self.refresh_rail()

    def _keep_focus_visible(self, side_panel, tabbed_editor) -> None:
        """Move the keyboard to whatever is still on screen when the panel fills or leaves it."""

        focused = self.app.focused
        if (side_panel.display
                and self.side_panel_width_percentage == max(WIDTH_SCALES)):
            # the editor has no room left
            if focused is None or side_panel not in focused.ancestors_with_self:
                self._focus_first(side_panel.visible_content)
        elif not side_panel.display and (
                focused is None or side_panel in focused.ancestors_with_self):
            self._focus_first(tabbed_editor.active_pane)

    @staticmethod
    def _focus_first(widget) -> None:
        if widget is None:
            return
        if widget.focusable:
            widget.focus()
            return
        target = next((child for child in widget.query("*")
                       if child.focusable), None)
        if target:
            target.focus()

    def refresh_rail(self) -> None:
        """Highlight the rail button for the visible side panel and the top bar button for the active tab."""

        side_panel = self._get_side_panel()
        panel_id = side_panel.current if side_panel.display else None
        self.app.query_one(SideBar).refresh_active(panel_id)
        self.app.query_one(TopBar).refresh_active(self.app.tabbed_editor.active)

    def _get_side_panel(self) -> SideBar:
        """Return the side panel widget instance."""

        return self.app.query_one("#side-panel")
