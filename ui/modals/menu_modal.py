from textual import events, on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.content import Content
from textual.geometry import Region
from textual.screen import ModalScreen
from textual.widgets import OptionList
from textual.widgets.option_list import Option

# the list's round border takes a row above and below the items
_BORDER_ROWS = 2


class MenuModal(ModalScreen[str | None]):
    """
    A dropdown of actions hanging under the button that opened it. Returns the
    id of the chosen action, or None when Escape or a click outside closes it.
    """

    BINDINGS = [Binding("escape", "close", "Close", show=False)]

    def __init__(self, anchor: Region, items: list[tuple[str, str, str]],
                 selected: str | None = None) -> None:
        """
        @Args:
            anchor: screen region of the button the menu hangs under.
            items: (action id, label, key) in display order; key may be "".
            selected: id of the current choice, ticked and highlighted on open.
        """

        super().__init__()
        self._anchor = anchor
        self._items = items
        self._selected = selected

    def compose(self) -> ComposeResult:
        # keys line up in a right-hand column, in the peach every key wears
        label_width = max(len(label) for _, label, _ in self._items)
        yield OptionList(*[Option(self._prompt(action, label, key, label_width),
                                  id=action)
                           for action, label, key in self._items],
                         classes="menu-list")

    def _prompt(self, action: str, label: str, key: str,
                label_width: int) -> Content:
        parts = []
        if self._selected is not None:
            parts.append(("✓ " if action == self._selected else "  ",
                          "$text-primary"))
        parts.append(label.ljust(label_width) if key else label)
        if key:
            parts.extend(["   ", (key, "$accent")])
        return Content.assemble(*parts)

    def on_mount(self) -> None:
        menu = self.query_one(OptionList)

        # hang below the button, or open upward when there's more room above
        wanted = len(self._items) + _BORDER_ROWS
        below = self.size.height - self._anchor.bottom
        above = self._anchor.y
        if wanted > below and above > below:
            height = min(wanted, above)
            menu.styles.offset = (self._anchor.x, self._anchor.y - height)
        else:
            height = min(wanted, below)
            menu.styles.offset = (self._anchor.x, self._anchor.bottom)
        menu.styles.max_height = height
        menu.styles.min_width = self._anchor.width

        if self._selected is not None:
            ids = [action for action, _, _ in self._items]
            if self._selected in ids:
                menu.highlighted = ids.index(self._selected)
        menu.focus()

    @on(OptionList.OptionSelected)
    def on_option_selected(self, event: OptionList.OptionSelected) -> None:
        event.stop()
        self.dismiss(event.option.id)

    def on_click(self, event: events.Click) -> None:
        # a click that lands outside the list closes the menu
        if event.widget is self:
            self.dismiss(None)

    def action_close(self) -> None:
        self.dismiss(None)


def file_menu(anchor: Region) -> MenuModal:
    """The top bar's File menu."""

    return MenuModal(anchor, [("open-folder", "Open Folder", "F3"),
                              ("open-file", "Open File", "Ctrl+O"),
                              ("new-file", "New File", "Ctrl+N")])
