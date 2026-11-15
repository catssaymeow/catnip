from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label

CANCEL = "cancel"


class ChoiceModal(ModalScreen[str]):
    """
    A small in-terminal dialog that asks one question and returns the id of the
    chosen option. Escape always dismisses with CANCEL, so the safe exit is one
    key away and never depends on a mouse or a GUI dialog.
    """

    BINDINGS = [Binding("escape", "cancel", "Cancel", show=False),
                Binding("left", "app.focus_previous", show=False),
                Binding("right", "app.focus_next", show=False)]

    def __init__(self, title: str, message: str,
                 options: list[tuple[str, str, str]],
                 focus: str | None = None, destructive: bool = False) -> None:
        """
        @Args:
            options: (choice id, button label, pill class) in display order.
            focus: id of the option focused on open; defaults to the first.
            destructive: title the dialog in the error hue, for removing work.
        """

        super().__init__()
        self._title = title
        self._message = message
        self._options = options
        self._focus = focus or options[0][0]
        self._destructive = destructive

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-box"):
            yield Label(self._title, classes="modal-title"
                        + (" -destructive" if self._destructive else ""))
            yield Label(self._message, classes="modal-message")
            with Horizontal(classes="modal-actions"):
                for choice, label, pill in self._options:
                    yield Button(label, id=choice, classes=f"option {pill}")

    def on_mount(self) -> None:
        self.query_one(f"#{self._focus}", expect_type=Button).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        self.dismiss(event.button.id)

    def action_cancel(self) -> None:
        self.dismiss(CANCEL)


def unsaved_changes_modal(name: str, closing: str) -> ChoiceModal:
    """Ask whether to save a document before closing it or quitting."""

    return ChoiceModal(title="Unsaved changes",
                       message=f"Save changes to {name} before {closing}?",
                       options=[("save", "Save", "pill-primary"),
                                ("discard", "Don't save", "pill-error"),
                                (CANCEL, "Cancel", "pill-neutral")])


def delete_modal(path: Path, file_count: int | None = 0) -> ChoiceModal:
    """
    Ask before moving a file, or a folder and its contents, to Catnip's trash.

    @Args:
        file_count: files inside a folder; None when there are too many to count.
    """

    undo = "Ctrl+Z in the file tree brings it back."
    if path.is_dir():
        title = "Delete folder"
        if file_count is None:
            contents = "and the thousands of files in it"
        elif file_count == 0:
            contents = "(it's empty)"
        else:
            contents = (f"and the {file_count:,} "
                        f"file{'' if file_count == 1 else 's'} in it")
        message = f"Delete the folder '{path.name}' {contents}? {undo}"
    else:
        title = "Delete file"
        message = f"Delete '{path.name}'? {undo}"

    return ChoiceModal(title=title, message=message,
                       options=[("delete", "Delete", "pill-error"),
                                (CANCEL, "Cancel", "pill-neutral")],
                       focus=CANCEL, destructive=True)
