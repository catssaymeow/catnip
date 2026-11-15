from dataclasses import dataclass

from textual import events
from textual.message import Message
from textual.widgets import Button

from ui.modals.menu_modal import MenuModal


class Dropdown(Button):
    """
    A pill showing the current choice; pressing it opens a MenuModal of the
    options beneath it, with the current one ticked. Posts Dropdown.Changed
    only when the user picks a different value.
    """

    @dataclass
    class Changed(Message):
        dropdown: "Dropdown"
        value: str

        @property
        def control(self) -> "Dropdown":
            return self.dropdown

    def __init__(self, options: list[tuple[str, str]], value: str | None = None,
                 prompt: str = "Choose", **kwargs) -> None:
        """
        @Args:
            options: (label, value) in display order.
            value: the current choice; None shows the prompt.
            prompt: label shown while nothing is chosen.
        """

        super().__init__(classes="option pill-neutral dropdown", **kwargs)
        self._options = options
        self._prompt = prompt
        self._value = value
        self._show_value()

    @property
    def value(self) -> str | None:
        return self._value

    @value.setter
    def value(self, value: str | None) -> None:
        """Show a choice without announcing it, e.g. to follow the active tab."""

        known = {option_value for _, option_value in self._options}
        self._value = value if value in known else None
        self._show_value()

    def _show_value(self) -> None:
        labels = {value: label for label, value in self._options}
        name = labels.get(self._value, self._prompt)

        # cut the name, never the arrow, when the pill is too narrow for both
        if self.size.width:
            room = (self.size.width - self.styles.gutter.width
                    - 2 * self.styles.line_pad - len(" ▾"))
            if len(name) > room:
                name = name[:max(room - 1, 0)].rstrip() + "…"
        self.label = f"{name} ▾"

    def on_resize(self, event: events.Resize) -> None:
        self._show_value()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        menu = MenuModal(self.region,
                         [(value, label, "") for label, value in self._options],
                         selected=self._value)
        self.app.push_screen(menu, self._pick)

    def _pick(self, value: str | None) -> None:
        if value is None or value == self._value:
            return
        self.value = value
        self.post_message(self.Changed(self, value))
