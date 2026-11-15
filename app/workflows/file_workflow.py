from pathlib import Path
from typing import Awaitable, Callable, Optional

from textual.screen import ModalScreen
from textual.widgets import TabbedContent, TabPane

from core.document.context import DocumentContext
from core.document.document import Document
from core.editor.languages import LANGUAGE_EXTENSION_MAP
from core.explorer.dialogs import BaseDialogHandler, DialogUnavailableError
from core.tab.lifecycle import TabLifecycle
from ui.modals.choice_modal import CANCEL, unsaved_changes_modal


class FileWorkflow:
    """
    Coordinate file-related user workflows such as saving and closing documents.

    This class encapsulates high-level file operations that involve user
    interaction (dialogs and notifications) and document state management.
    It handles scenarios like prompting to save unsaved changes, saving to
    an existing path or a new path, and closing one or all tabs safely.

    FileWorkflow does not perform low-level file I/O itself; instead, it
    delegates persistence to DocumentContext and user interaction to the
    dialog handler and in-app modals, keeping responsibilities clearly separated.
    """

    def __init__(self, documents: DocumentContext, dialogs: BaseDialogHandler,
                 notify: Callable[..., None],
                 ask: Callable[[ModalScreen[str]], Awaitable[str]],
                 start_folder: Callable[[], Path]):
        """
        @Args:
            start_folder: where a save dialog opens for an untitled document.
        """

        self.documents = documents
        self.dialogs = dialogs
        self.notify = notify
        self.ask = ask
        self.start_folder = start_folder

    async def close_active_tab(self, editor: TabbedContent,
                               tab_lifecycle: TabLifecycle) -> None:
        """Close the currently active tab, asking first if it has unsaved changes."""

        active_tab = editor.active_pane
        if not active_tab:
            return

        if not await self.resolve_unsaved(active_tab.id, tab_lifecycle,
                                          closing="closing"):
            return

        tab_lifecycle.on_tab_closed(active_tab.id)

        await editor.remove_pane(active_tab.id)

    async def resolve_all_before_exit(self, editor: TabbedContent,
                                      tab_lifecycle: TabLifecycle) -> bool:
        """
        Ask about every document with unsaved changes before the application exits.

        Tabs are processed in reverse order so the most recently opened tabs are
        handled first, and each one is shown while its question is asked.

        Returns:
            True if it is safe to quit; False if the user cancelled.
        """
        for tab in reversed(list(editor.query(TabPane))):
            if not tab_lifecycle.needs_save_prompt(tab.id):
                continue
            editor.active = tab.id  # show the tab being asked about
            if not await self.resolve_unsaved(tab.id, tab_lifecycle,
                                              closing="quitting"):
                return False
        return True

    async def resolve_unsaved(self, tab_id: str, tab_lifecycle: TabLifecycle,
                              closing: str) -> bool:
        """
        Ask what to do with unsaved changes in the given tab.

        Returns:
            True if the tab may close (it was clean, saved, or the user chose
            not to save); False if the user cancelled or the save did not happen.
        """
        if not tab_lifecycle.needs_save_prompt(tab_id):
            return True

        name = tab_lifecycle.get_display_name(tab_id)
        choice = await self.ask(unsaved_changes_modal(name, closing))

        if choice == CANCEL:
            return False
        if choice == "discard":
            return True

        document = self.documents.get(tab_id)

        if document.path is None:
            file_path = await self._pick_save_path(document)
            if not file_path:
                return False

            self.documents.save_to(document.id, file_path)
            self.documents.close(document.id)
            self.notify(f"Saved {file_path.name} to {file_path.parent}")
            return True

        self.documents.save(document.id)
        self.notify(f"Saved {document.title}")
        return True

    def save_on_dirty(self, document: Document) -> None:
        """
        Save the given document if it has unsaved changes.

        This method unconditionally writes the document to its current path
        when it is dirty, and does nothing if the document is already clean.
        """

        if not self.documents.has_unsaved_changes(document.id):
            self.notify(f"No changes to save in {document.title}")
            return

        self.documents.save(document.id)
        self.notify(f"Saved {document.title}")

    async def save_as(self, document: Document) -> Optional[Path]:
        """
        Save the given document to a new user-selected location.

        The user is prompted to choose a destination path. If the user cancels
        the dialog, no save is performed and None is returned.

        Returns:
            The new file path if the save succeeds; otherwise, None.
        """
        file_path = await self._pick_save_path(document)
        if not file_path:
            return None

        self.documents.save_to(document.id, file_path)
        self.notify(f"Saved {file_path.name} to {file_path.parent}")

        return file_path

    async def _pick_save_path(self, document: Document) -> Optional[Path]:
        """Ask where to save the document, reporting it when the file picker can't open."""

        if document.path:
            start, file_name = document.path.parent, document.path.name
        else:
            extension = LANGUAGE_EXTENSION_MAP.get(document.language, "md")
            start, file_name = self.start_folder(), f"untitled.{extension}"

        try:
            return await self.dialogs.select_save_path(start, file_name)
        except DialogUnavailableError as error:
            self.notify(str(error), severity="error", timeout=8)
            return None
