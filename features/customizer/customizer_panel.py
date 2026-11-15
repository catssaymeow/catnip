from textual import on
from textual.containers import Container
from textual.widgets import Label

from features.customizer.customizer_controller import CustomizerController
from ui.widgets.dropdown import Dropdown


class CustomizerPanel(Container):
    """A side panel for choosing the app theme, the editor theme, and the active file's language."""

    def __init__(self, app_themes: list, current_app_theme: str,
                 editor_themes: list, current_editor_theme: str,
                 languages: list, controller: CustomizerController):
        super().__init__(id="customizer")
        self.app_themes = app_themes
        self.current_app_theme = current_app_theme
        self.editor_themes = editor_themes
        self.current_editor_theme = current_editor_theme
        self.languages = languages
        self.controller = controller

        # remove duplicates from language options
        unique_languages = sorted(set(languages))
        self.languages = [(lang.capitalize(), lang) for lang in
                          unique_languages]

    def compose(self):
        """Create the customization panel layout."""

        yield Container(
            Label("App theme:"),
            Dropdown(options=self.app_themes, value=self.current_app_theme,
                     tooltip="Select a theme to apply to the app",
                     id="app-theme-picker", ),
            Label("Editor theme:"),
            Dropdown(options=self.editor_themes,
                     value=self.current_editor_theme,
                     tooltip="Select a theme to apply to the editor",
                     id="editor-theme-picker", ),
            Label("File language:"),
            Dropdown(options=self.languages,
                     prompt="Not set",
                     tooltip="Select a programming language for the active tab",
                     id="language-picker", ), )

    def show_language(self, language: str | None) -> None:
        """Show the active tab's language in the picker without re-applying it."""

        self.query_one("#language-picker", expect_type=Dropdown).value = language

    @on(Dropdown.Changed)
    def on_dropdown_changed(self, event: Dropdown.Changed) -> None:
        """Notify the controller when the selection changes."""

        self.controller.handle_select_change(select_id=event.dropdown.id,
                                             value=event.value, )
