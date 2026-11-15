from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from textual.widgets import TabbedContent
from textual.widgets import TextArea

from core.document.context import DocumentContext
from core.editor.languages import LANGUAGE_EXTENSION_MAP
from core.tab.constants import EXCEPTION_TAB_IDS
from core.theme import CUSTOM_EDITOR_THEMES


class RunnableLanguage(Enum):
    """
    Languages supported for execution by Catnip.

    This enum defines the set of file extensions that can be run.
    For each language added here, a corresponding runner
    implementation must exist in @features/executor/runner.

    This keeps the list of runnable languages explicit and centralized.
    """
    PY = "py"
    JS = "js"
    TS = "ts"
    JAVA = "java"


RUNNABLE_NAMES = "Python, JavaScript, TypeScript, and Java"

# languages whose runners leave nothing behind, so a saved file can run where it is;
# TypeScript and Java write build output next to the file, so they run from a copy
RUN_IN_PLACE = {RunnableLanguage.PY, RunnableLanguage.JS}


@dataclass
class RunTarget:
    """What to run, from which folder, and the name to show for it in output."""

    file: Path
    cwd: Path
    shown_as: str  # the file people know; replaces any temp path in the output


class NotRunnableError(Exception):
    """Raised with a user-facing reason when the active tab can't be run."""


def register_custom_editor_theme(text_area: TextArea) -> None:
    for theme in CUSTOM_EDITOR_THEMES:
        text_area.register_theme(theme)


def prepare_runnable_file(tabbed_editor: TabbedContent,
                          documents: DocumentContext) -> RunTarget:
    """
    Determine whether the currently active tab can be executed and, if so,
    say what to run.

    This function encapsulates the editor-side rules for running a file
    (which tab is eligible, whether it maps to a document, and whether its
    language is supported) and hides these details from the runner.

    A saved Python or JavaScript file with no unsaved changes runs where it
    is. Anything else runs from a temp copy, still from the document's own
    folder, so imports of neighbouring files and relative paths keep working.

    @Returns:
        The file to execute, the folder to run it from, and the name to show for it.

    @Raises:
        NotRunnableError: with the reason, when the active tab can't be run.
    """

    active_tab = tabbed_editor.active_pane

    if (not active_tab or active_tab.id in EXCEPTION_TAB_IDS
            or not documents.is_document(active_tab.id)):
        raise NotRunnableError(
            f"Open a {RUNNABLE_NAMES} file to run it.")

    document = documents.get(active_tab.id)

    if not document.content.strip():
        raise NotRunnableError(
            f"{document.title} is empty, so there's nothing to run yet.")

    suffix = (
        document.path.suffix.lstrip(".")
        if document.path
        else LANGUAGE_EXTENSION_MAP.get(document.language, "")
    )
    try:
        language = RunnableLanguage(suffix)
    except ValueError:
        raise NotRunnableError(f"Catnip can run {RUNNABLE_NAMES} files. "
                               f"{document.title} isn't one of those.")

    if document.path and not document.dirty and language in RUN_IN_PLACE:
        return RunTarget(document.path, document.path.parent,
                         str(document.path))

    # write and run a temp copy instead of forcing a save
    temp_path = documents.write_temp(document.id)
    folder = document.path.parent if document.path else temp_path.parent
    return RunTarget(temp_path, folder,
                     str(document.path) if document.path else document.title)
