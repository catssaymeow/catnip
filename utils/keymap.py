from rich.text import Text
from textual.widgets import DataTable

# how each key name is written to people: Ctrl+Shift+O, F1, Ctrl+Shift+→
_KEY_NAMES = {"ctrl": "Ctrl", "shift": "Shift", "alt": "Alt", "super": "Cmd",
              "left": "←", "right": "→", "up": "↑", "down": "↓",
              "enter": "Enter", "escape": "Esc", "delete": "Delete",
              "backspace": "Backspace"}


def _format_key(key: str) -> str:
    return "+".join(_KEY_NAMES.get(part, part.upper()) for part in key.split("+"))


def format_shortcut(keys: str) -> str:
    """Format a binding key string such as "ctrl+b,ctrl+1" as "Ctrl+B / Ctrl+1"."""

    return " / ".join(_format_key(key) for key in keys.split(","))


def needs_kitty_protocol(key: str) -> bool:
    """
    True for keys that only reach the app in terminals with the kitty keyboard
    protocol: Ctrl+digit, Ctrl+Shift+letter, and Shift+Enter.
    """

    parts = key.split("+")
    name = parts[-1]
    if "shift" in parts and name == "enter":
        return True
    if "ctrl" not in parts:
        return False
    return name.isdigit() or ("shift" in parts and len(name) == 1)


def create_mapping_table(table: DataTable, bindings: list,
                         key_color: str, muted_color: str) -> DataTable:
    """
    Fill the table with (keys, action) rows, keeping the task order they are
    given in. Keys come first so narrow terminals clip the description, not
    the key. Keys that need the kitty keyboard protocol are muted.
    """

    for action, shortcut in bindings:
        keys = Text(justify="left")
        for index, key in enumerate(str(shortcut).split(",")):
            if index:
                keys.append(" / ", style=muted_color)
            keys.append(_format_key(key), style=muted_color
                        if needs_kitty_protocol(key) else key_color)
        table.add_row(keys, Text(str(action), justify="left"))
    return table
