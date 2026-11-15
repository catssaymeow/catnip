from __future__ import annotations

from textual import events, on
from textual.widgets import TextArea

from .controller import EditorController


class Editor(TextArea):
    """
    Text editor widget bound to a document and coordinated by an EditorController.

    This class extends TextArea with editor-specific behaviors such as paired
    character insertion, selection handling, and change notifications that
    propagate updates to the document model.
    """

    def __init__(self, document_id: str, controller: EditorController, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.document_id = document_id
        self.controller = controller

    def on_key(self, event: events.Key) -> None:
        """Handles special character insertions."""

        if event.character in [")", "}", "]", "'", '"'] and self._next_character() == event.character:
            # step over the closing character that auto-pairing already inserted
            self.move_cursor_relative(columns=1)
            event.prevent_default()
            return

        if event.character in ["'", '"'] and self._follows_word_character():
            # an apostrophe in "don't" or a closing quote: insert it as typed
            return

        if event.character in ["(", "{", "[", "'", '"']:
            pairs = {"(": "()", "{": "{}", "[": "[]", "'": "''", '"': '""'}
            self.insert(pairs[event.character])
            self.move_cursor_relative(columns=-1)
            event.prevent_default()

    def _follows_word_character(self) -> bool:
        """Return True if the character before the cursor is a letter or digit."""

        row, column = self.cursor_location
        line = self.document.get_line(row)
        return column > 0 and line[column - 1].isalnum()

    def _next_character(self) -> str:
        """Return the character right after the cursor, or an empty string at line end."""

        row, column = self.cursor_location
        line = self.document.get_line(row)
        return line[column] if column < len(line) else ""

    @on(TextArea.Changed)
    def on_changed(self, event: TextArea.Changed) -> None:
        """Notify the controller when the editor content changes."""

        self.controller.on_editor_text_changed(self.document_id,
                                               event.control.text, )

    @on(TextArea.SelectionChanged)
    def handle_selection_change(self, event: TextArea.SelectionChanged):
        """Copy selected text to clipboard when a selection is made."""

        if not event.selection.is_empty:
            self.action_copy()

    @classmethod
    def for_document(cls, *, document_id: str, controller: EditorController,
                     language: str = "markdown", **kwargs, ) -> Editor:
        """Create an Editor instance configured for a specific document."""

        return cls(document_id=document_id, controller=controller,
                   language=language, show_line_numbers=True, **kwargs)

    @staticmethod
    def normalize_language(language: str) -> str:
        """Normalize language names to match supported editor syntax."""

        return "javascript" if language == "typescript" else language
