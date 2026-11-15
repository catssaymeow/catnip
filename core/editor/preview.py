from __future__ import annotations

from textual.containers import VerticalScroll
from textual.widgets import Markdown, TabPane

from .editor import Editor

MARKDOWN_LANGUAGE = "markdown"


class MarkdownPreview(VerticalScroll):
    """Scrollable rendered view of a markdown document, shown in place of its editor."""

    def __init__(self, text: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self._markdown = Markdown(text)

    def compose(self):
        yield self._markdown

    def render_text(self, text: str) -> None:
        """Replace the rendered content with the given markdown source."""

        self._markdown.update(text)


def is_markdown_editor(editor: Editor) -> bool:
    return editor.language == MARKDOWN_LANGUAGE


def toggle_preview(tab: TabPane) -> bool:
    """
    Swap a markdown editor tab between editing and rendered preview.

    The preview is created on first use and always re-rendered from the
    editor's current text, so unsaved edits are reflected.

    @Returns:
        True if the preview is now showing, False if the editor is.
        Tabs without a markdown editor are left untouched and return False.
    """

    editors = tab.query(Editor)
    if not editors or not is_markdown_editor(editors.first()):
        return False

    editor = editors.first()
    previews = tab.query(MarkdownPreview)

    if previews and previews.first().display:
        previews.first().display = False
        editor.display = True
        editor.focus()
        return False

    if previews:
        preview = previews.first()
        preview.render_text(editor.text)
    else:
        preview = MarkdownPreview(editor.text)
        tab.mount(preview)

    preview.display = True
    editor.display = False
    preview.focus()
    return True
