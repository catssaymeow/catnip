import os
from enum import Enum
from pathlib import Path
from typing import Iterable, Optional

from textual import events, on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.suggester import Suggester
from textual.widgets import Button, DirectoryTree, Input, Label

from core.explorer.file_browser import FileBrowser, HIDDEN_NAMES
from ui.modals.choice_modal import CANCEL, ChoiceModal


class PickMode(Enum):
    """What the picker asks for: (title, confirm label)."""

    FOLDER = ("Open folder", "Open")
    FILE = ("Open a file", "Open")
    SAVE = ("Save as", "Save")


HINTS = {
    PickMode.FOLDER: "Tab completes · ↓ browses · Enter opens the folder",
    PickMode.FILE: "Tab completes · ↓ browses · Enter opens the file",
    PickMode.SAVE: "Tab completes · ↓ picks a folder · Enter saves",
}


def display_path(path: Path) -> str:
    """Write a path the short way people type it: ~/notes instead of /Users/me/notes."""

    home = Path.home()
    if path == home:
        return "~"
    if path.is_relative_to(home):
        return f"~{os.sep}{path.relative_to(home)}"
    return str(path)


def resolve_typed(value: str) -> Path:
    return Path(value.strip()).expanduser().resolve()


class PathSuggester(Suggester):
    """Suggest the rest of the last path segment from what's on disk."""

    def __init__(self, folders_only: bool) -> None:
        super().__init__(use_cache=False, case_sensitive=True)
        self.folders_only = folders_only

    async def get_suggestion(self, value: str) -> Optional[str]:
        if not value or value.endswith(os.sep):
            return None

        typed = Path(value).expanduser()
        prefix = typed.name
        try:
            matches = sorted(
                entry for entry in typed.parent.iterdir()
                if entry.name.startswith(prefix)
                and (prefix.startswith(".") or not entry.name.startswith("."))
                and (entry.is_dir() or not self.folders_only))
        except OSError:
            return None
        if not matches:
            return None

        completion = os.path.commonprefix([entry.name for entry in matches])
        if len(matches) == 1 and matches[0].is_dir():
            completion += os.sep
        if completion == prefix:
            return None
        return value + completion[len(prefix):]


class PathInput(Input):
    """Path field where Tab accepts the suggested completion before moving focus."""

    BINDINGS = [Binding("down", "browse", "Browse the folders", show=False)]

    def action_browse(self) -> None:
        self.screen.query_one(PickerTree).focus()

    async def _on_key(self, event: events.Key) -> None:
        if (event.key == "tab" and self._suggestion
                and len(self._suggestion) > len(self.value)):
            event.stop()
            event.prevent_default()
            self.value = self._suggestion
            self.cursor_position = len(self.value)
            return
        await super()._on_key(event)


class PickerTree(DirectoryTree):
    """Browse beside the path field; Backspace climbs to the parent folder."""

    ICON_FILE = FileBrowser.ICON_FILE
    ICON_NODE = FileBrowser.ICON_NODE
    ICON_NODE_EXPANDED = FileBrowser.ICON_NODE_EXPANDED

    BINDINGS = [Binding("backspace", "go_up", "Parent folder", show=False)]

    def __init__(self, path: Path, folders_only: bool) -> None:
        super().__init__(path, classes="picker-tree")
        self.folders_only = folders_only

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if not path.name.startswith(".")
                and path.name not in HIDDEN_NAMES
                and (path.is_dir() or not self.folders_only)]

    def action_go_up(self) -> None:
        parent = Path(self.path).parent
        if parent != Path(self.path):
            self.screen.browse(parent)


class PathModal(ModalScreen[Optional[Path]]):
    """
    An in-terminal picker for opening a folder or file, or choosing where to
    save. Type a path with Tab completion, or browse with the tree below it.
    Escape always cancels, like every Catnip dialog.
    """

    BINDINGS = [Binding("escape", "cancel", "Cancel", show=False)]

    def __init__(self, mode: PickMode, start: Path,
                 file_name: str = "") -> None:
        """
        @Args:
            start: folder the picker opens in.
            file_name: name filled in after the folder, for saving.
        """

        super().__init__()
        self.mode = mode
        self.start = start.resolve()
        self.file_name = file_name

    def compose(self) -> ComposeResult:
        title, confirm = self.mode.value
        folders_only = self.mode in (PickMode.FOLDER, PickMode.SAVE)
        value = display_path(self.start)
        value = value if value.endswith(os.sep) else value + os.sep

        with Vertical(classes="modal-box picker-box"):
            yield Label(title, classes="modal-title")
            yield PathInput(value + self.file_name, classes="picker-input",
                            suggester=PathSuggester(
                                self.mode is PickMode.FOLDER))
            yield Label(HINTS[self.mode], classes="picker-hint")
            yield PickerTree(self.start, folders_only)
            with Horizontal(classes="modal-actions"):
                yield Button(confirm, id="confirm",
                             classes="option pill-primary")
                yield Button("Cancel", id=CANCEL,
                             classes="option pill-neutral")

    def on_mount(self) -> None:
        field = self.query_one(PathInput)
        field.focus()
        if self.file_name:
            # select the name without its extension, so typing renames the
            # file and both the folder and the file type stay
            stem = Path(self.file_name).stem or self.file_name
            start = len(field.value) - len(self.file_name)
            field.selection = (start, start + len(stem))

    def browse(self, folder: Path) -> None:
        """Show the given folder in the tree and the path field."""

        tree = self.query_one(PickerTree)
        tree.path = folder
        name = self.file_name if self.mode is PickMode.SAVE else ""
        field = self.query_one(PathInput)
        shown = display_path(folder)
        field.value = (shown if shown.endswith(os.sep) else shown + os.sep) + name
        field.cursor_position = len(field.value)

    def _set_hint(self, message: Optional[str] = None) -> None:
        hint = self.query_one(".picker-hint", Label)
        hint.update(message or HINTS[self.mode])
        hint.set_class(bool(message), "-error")

    @on(Input.Changed, ".picker-input")
    def on_path_changed(self, event: Input.Changed) -> None:
        """Clear a stale problem and follow the typed folder in the tree."""

        self._set_hint()
        typed = Path(event.value.strip()).expanduser()
        folder = typed if event.value.endswith(os.sep) else typed.parent
        tree = self.query_one(PickerTree)
        if folder.is_dir() and folder.resolve() != Path(tree.path).resolve():
            tree.path = folder.resolve()

    @on(DirectoryTree.DirectorySelected)
    def on_folder_picked(self, event: DirectoryTree.DirectorySelected) -> None:
        event.stop()
        if self.mode is PickMode.FILE:
            return  # the tree opens the folder; a file is still to come
        name = self.file_name if self.mode is PickMode.SAVE else ""
        field = self.query_one(PathInput)
        field.value = display_path(event.path) + os.sep + name
        field.cursor_position = len(field.value)

    @on(DirectoryTree.FileSelected)
    def on_file_picked(self, event: DirectoryTree.FileSelected) -> None:
        event.stop()
        self.query_one(PathInput).value = display_path(event.path)
        self._confirm()

    @on(Input.Submitted, ".picker-input")
    def on_path_submitted(self) -> None:
        self._confirm()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        if event.button.id == "confirm":
            self._confirm()
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _confirm(self) -> None:
        """Check the typed path for this mode, then return it or say what's wrong."""

        value = self.query_one(PathInput).value.strip()
        if not value:
            self._set_hint("Type a path first.")
            return

        path = resolve_typed(value)
        shown = display_path(path)

        if self.mode is PickMode.FOLDER:
            if not path.is_dir():
                self._set_hint(f"There's no folder at {shown}.")
                return
            self.dismiss(path)

        elif self.mode is PickMode.FILE:
            if path.is_dir():
                self.browse(path)
                return
            if not path.is_file():
                self._set_hint(f"There's no file at {shown}.")
                return
            self.dismiss(path)

        else:
            if value.endswith(os.sep) or path.is_dir():
                self._set_hint("Add a file name after the folder.")
                return
            if not path.parent.is_dir():
                self._set_hint(
                    f"There's no folder at {display_path(path.parent)}.")
                return
            if path.exists():
                self.app.push_screen(replace_modal(path),
                                     lambda choice: choice == "replace"
                                     and self.dismiss(path))
                return
            self.dismiss(path)


def replace_modal(path: Path) -> ChoiceModal:
    """Ask before saving over a file that already exists."""

    return ChoiceModal(title="Replace file",
                       message=f"'{path.name}' already exists in "
                               f"{display_path(path.parent)}. Replace it?",
                       options=[("replace", "Replace", "pill-error"),
                                (CANCEL, "Cancel", "pill-neutral")],
                       focus=CANCEL, destructive=True)
