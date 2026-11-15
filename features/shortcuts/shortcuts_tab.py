from textual.containers import VerticalScroll
from textual.widgets import DataTable, Static, TabPane

from utils.keymap import create_mapping_table

KITTY_NOTE = ("Dimmed keys only reach Catnip in terminals that support the "
              "kitty keyboard protocol. The first key on each row works "
              "everywhere.")


class ShortcutsTab(TabPane):
    """Tab pane displaying available keyboard shortcuts in a table."""

    def __init__(self, desc_key_pairs, key_color: str, muted_color: str):
        super().__init__(title="Shortcuts", id="key-mappings")
        self._desc_key_pairs = desc_key_pairs
        self._key_color = key_color
        self._muted_color = muted_color

    def on_mount(self) -> None:
        """Build and mount the shortcuts table when the tab is displayed."""

        table = DataTable(id="key-mapping-table")
        table.add_columns("Shortcut", "Action")
        create_mapping_table(table, self._desc_key_pairs, self._key_color,
                             self._muted_color)
        self.mount(VerticalScroll(table,
                                  Static(KITTY_NOTE, classes="shortcuts-note")))
