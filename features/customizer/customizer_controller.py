from typing import TYPE_CHECKING

from textual.widgets import TabPane, DataTable

from config.app import AppConfig
from core.editor.editor import Editor
from core.editor.languages import supported_languages
from core.tab.constants import EXCEPTION_TAB_IDS
from core.theme import APP_THEMES, EDITOR_THEMES, resolve_editor_theme
from utils.editor import register_custom_editor_theme
from utils.keymap import create_mapping_table

if TYPE_CHECKING:
    from app.entry import CatnipApp


class CustomizerController:
    """Handle theme, language, and editor customization actions from the Customizer Panel."""

    def __init__(self, app: "CatnipApp"):
        self.app = app
        self.config = AppConfig.load()

    def handle_select_change(self, select_id: str, value: str) -> None:
        """Handle selection changes in the Customizer Panel."""

        if select_id == "app-theme-picker":
            if value in str(APP_THEMES):
                self.apply_app_theme(value)

        elif select_id == "editor-theme-picker":
            if value in str(EDITOR_THEMES):
                self.apply_editor_theme(value)

        elif select_id == "language-picker":
            if value in supported_languages():
                self.apply_language(value)

    def apply_app_theme(self, app_theme: str) -> None:
        """Apply and save the selected app-wide theme."""

        self.app.theme = app_theme
        self.config.app_theme = app_theme
        self.config.save()

        # an editor set to "match" follows the new app theme
        self._apply_to_editors(self.app.editor_theme)

        try:
            mappings_tab = self.app.tabbed_editor.get_pane("key-mappings")
            mappings_table = self.app.query_one("#key-mapping-table",
                                                expect_type=DataTable)
            mappings_table.clear()
            create_mapping_table(mappings_table, self.app.desc_key_pairs,
                                 self.app.key_color())
            mappings_tab.refresh()
        except Exception:
            pass

    def apply_editor_theme(self, theme: str) -> None:
        """Apply the selected theme to the code editor (syntax highlighting)."""

        self._apply_to_editors(theme)

        # save theme to project config and editor_theme attr
        self.app.editor_theme = theme
        self.config.editor_theme = theme
        self.config.save()

    def _apply_to_editors(self, theme: str) -> None:
        """Restyle every open editor with the given editor theme setting."""

        resolved = resolve_editor_theme(theme, self.app.theme,
                                        self.app.current_theme.dark)
        for tab in self.app.tabbed_editor.query(TabPane):
            for text_area in tab.query(Editor):
                register_custom_editor_theme(text_area)
                text_area.theme = resolved

    def apply_language(self, language: str) -> None:
        """Apply the selected language for syntax highlighting."""

        active_tab = self.app.tabbed_editor.active_pane
        if not active_tab or active_tab.id in EXCEPTION_TAB_IDS:
            return

        editors = active_tab.query(Editor)
        if not editors:
            return
        editors.first().language = Editor.normalize_language(language)

        # untitled documents take their file type (and runnability) from this
        document = self.app.documents.try_get(active_tab.id)
        if document:
            document.language = language
