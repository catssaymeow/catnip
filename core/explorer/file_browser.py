import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional, Union

from textual.binding import Binding
from textual.widgets import DirectoryTree, Tree

# noise every project folder has; hidden so the tree shows the work itself
HIDDEN_NAMES = {".git", ".DS_Store", "__pycache__"}

# deleted items wait here so a slip of the Backspace key can be undone
TRASH_DIR = Path.home() / ".catnip" / "trash"
TRASH_KEEP_SECONDS = 7 * 24 * 60 * 60
TRASH_STAMP = "%Y%m%d-%H%M%S"
TRASH_STAMP_EXAMPLE = "20260101-120000"

# counting stops here so a huge folder doesn't stall the delete prompt
COUNT_LIMIT = 10_000


class FileBrowser(DirectoryTree):
    """Directory tree widget for browsing, opening, and deleting files."""

    ICON_FILE = "◦ "
    ICON_NODE = "▸ "
    ICON_NODE_EXPANDED = "▾ "

    BINDINGS = [
        Binding("enter", "open_highlighted", "Open the highlighted file",
                show=False),
        # Mac keyboards send backspace from the key labeled "delete"
        Binding("delete,backspace", "app.delete_selected_file",
                "Delete file or folder", show=False),
        Binding("ctrl+z", "restore_deleted", "Undo the last delete",
                show=False), ]

    def __init__(self, path: Union[str, Path] = "./",
                 on_open_file=None) -> None:
        # resolve so the root shows the folder's name instead of "./"
        super().__init__(Path(path).resolve(), id="file-browser",
                         classes="file-browser")
        self.selected_path = None
        self.last_click_node = None
        self.last_click_time = None
        self.on_open_file = on_open_file
        # (original path, where it waits in the trash), newest last
        self._deleted: list[tuple[Path, Path]] = []
        self._empty_old_trash()

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if path.name not in HIDDEN_NAMES]

    def action_open_highlighted(self) -> None:
        """Open the highlighted file right away, or expand/collapse a folder."""

        node = self.cursor_node
        if node is None or node.data is None:
            return

        if self._safe_is_dir(node.data.path):
            self.action_select_cursor()
        elif self.on_open_file:
            self.on_open_file(Path(node.data.path))

    def on_directory_tree_file_selected(self,
                                        event: DirectoryTree.FileSelected) -> None:
        """Handle mouse selection and trigger open action on double-click."""

        event.stop()
        current_time = datetime.now().timestamp()
        # both clicks must land on the same file to count as a double-click
        if (self.last_click_node is event.node and self.last_click_time
                and (current_time - self.last_click_time) < 0.5):
            self.selected_path = Path(event.path)
            if self.on_open_file:
                self.on_open_file(self.selected_path)
        self.last_click_node = event.node
        self.last_click_time = current_time

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
        """Track the currently highlighted file or folder in the tree."""

        event.stop()
        self.selected_path = Path(event.node.data.path)

    def protected_reason(self, path: Path) -> Optional[str]:
        """Say why a path must never be deleted from the tree, or None if it may be."""

        path = path.resolve()
        if path == Path(self.path).resolve():
            return "it's the folder open in the tree"
        if path in (Path.cwd(), Path.home(), Path(path.anchor)):
            return "it's a folder your system relies on"
        if path in Path.cwd().parents or path in Path.home().parents:
            return "it holds folders your system relies on"
        return None

    def delete_path(self, path: Path) -> bool:
        """Move a file or folder the user has already confirmed into the trash. Returns True on success."""

        stamp = time.strftime(TRASH_STAMP)
        trashed = TRASH_DIR / f"{stamp}-{path.name}"
        copy = 1
        while trashed.exists():
            copy += 1
            trashed = TRASH_DIR / f"{stamp}-{copy}-{path.name}"
        try:
            TRASH_DIR.mkdir(parents=True, exist_ok=True)
            shutil.move(path, trashed)
        except OSError as error:
            self.notify(f"Couldn't delete {path.name}: {error.strerror}.",
                        severity="error")
            return False

        self._deleted.append((path, trashed))
        self.reload()
        return True

    def action_restore_deleted(self) -> None:
        """Put the most recently deleted item back where it was."""

        if not self._deleted:
            self.notify("Nothing to bring back.")
            return

        original, trashed = self._deleted[-1]
        if original.exists():
            self.notify(f"Can't bring back {original.name}: something "
                        "with that name is there now.", severity="warning")
            return

        try:
            original.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(trashed, original)
        except OSError as error:
            self.notify(f"Couldn't bring back {original.name}: "
                        f"{error.strerror}.", severity="error")
            return

        self._deleted.pop()
        self.reload()
        self.notify(f"Brought back {original.name}")

    @staticmethod
    def _empty_old_trash() -> None:
        """Remove trashed items older than a week, so the trash never grows forever."""

        if not TRASH_DIR.is_dir():
            return

        cutoff = time.time() - TRASH_KEEP_SECONDS
        for item in TRASH_DIR.iterdir():
            # the name starts with when it was deleted; a moved item keeps its old mtime
            try:
                deleted_at = time.mktime(
                    time.strptime(item.name[:len(TRASH_STAMP_EXAMPLE)],
                                  TRASH_STAMP))
            except ValueError:
                continue  # not something Catnip put here
            try:
                if deleted_at >= cutoff:
                    continue
                if item.is_dir() and not item.is_symlink():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            except OSError:
                pass  # try again next start


def count_files(folder: Path) -> Optional[int]:
    """Count the files inside a folder, or None when there are more than COUNT_LIMIT."""

    count = 0
    for _, _, files in folder.walk():
        count += len(files)
        if count > COUNT_LIMIT:
            return None
    return count
