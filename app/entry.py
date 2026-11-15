from functools import partial
from pathlib import Path
from typing import Iterable, Optional

from rich.text import Text
from textual import events, on, work
from textual.app import App, ComposeResult, SystemCommand
from textual.binding import Binding
from textual.color import Color
from textual.containers import Horizontal, Vertical
from textual.content import Content
from textual.screen import Screen
from textual.widgets import Button, Footer, TabbedContent, TabPane, Markdown, \
    ContentSwitcher, RichLog

from app.workflows.file_workflow import FileWorkflow
from config.app import AppConfig
from core.document.context import DocumentContext
from core.document.document import Document
from core.editor.controller import EditorController
from core.editor.editor import Editor
from core.editor.languages import supported_languages
from core.editor.preview import toggle_preview, is_markdown_editor
from core.explorer.dialogs import get_dialog_handler, DialogUnavailableError
from core.explorer.file_browser import FileBrowser, count_files
from core.tab.constants import WELCOME_TAB_ID
from core.tab.lifecycle import TabLifecycle
from core.theme import APP_THEMES, EDITOR_THEMES, CUSTOM_APP_THEMES, \
    resolve_editor_theme
from features.chat.chat_pane import ChatPane
from features.chat.ollama_client import OllamaClient
from features.customizer.customizer_controller import CustomizerController
from features.customizer.customizer_panel import CustomizerPanel
from features.executor import runner
from features.executor.runner import RunResult
from features.shortcuts.shortcuts_tab import ShortcutsTab
from ui.constants import DEFAULT_SIDE_PANEL_WIDTH_PERCENTAGE, RUNNER_PROMPT, \
    RUNNER_EMPTY, RUNNER_MIN_WIDTH, UNSAVED_MARK, WELCOME_MESSAGE
from ui.layout.layout_controller import LayoutController, SidePanelId
from ui.modals.choice_modal import delete_modal
from ui.modals.menu_modal import file_menu
from ui.sidebar.sidebar import SideBar
from ui.topbar.top_bar import TopBar
from utils.editor import register_custom_editor_theme, prepare_runnable_file, \
    NotRunnableError, RunTarget
from utils.keymap import format_shortcut
from utils.tabs import is_open

# shortcuts that live on a single widget, listed after the app bindings
CONTEXT_SHORTCUTS = [
    ("Open the highlighted file (file tree)", "enter"),
    ("Delete file or folder (file tree)", "delete,backspace"),
    ("Undo the last delete (file tree)", "ctrl+z"),
    ("Send a message (Cat Me)", "enter"),
    ("New line in a message (Cat Me)", "ctrl+j,shift+enter"), ]


class CatnipApp(App):
    """
    Main application entry point responsible for UI orchestration.
    Document state and file lifecycle are delegated to DocumentContext.
    """

    TITLE = "Catnip"
    CSS_PATH = "../styles/entry.tcss"
    # the screen gets -wide from 120 columns, so roomy terminals get roomier chrome
    HORIZONTAL_BREAKPOINTS = [(0, "-compact"), (120, "-wide")]
    # Bindings are grouped by task; this order is also the Shortcuts tab order.
    # Every action leads with a key any terminal can send (Ctrl+letter or an
    # F-key); Ctrl+digit and Ctrl+Shift+letter aliases only reach the app in
    # terminals with the kitty keyboard protocol, so they never come first.
    BINDINGS = [
        Binding("ctrl+o", "open_file", "Open a file", show=False),
        Binding("f3,ctrl+shift+o", "open_folder", "Open folder", show=False),
        Binding("ctrl+n", "new_file", "New file", show=False),
        Binding("ctrl+s", "save_file", "Save", priority=True),
        Binding("f2,ctrl+shift+s", "save_file_as", "Save as", show=False,
                priority=True),
        Binding("ctrl+w", "close_tab", "Close tab", show=False, priority=True),
        Binding("ctrl+r,ctrl+shift+r", "run_script", "Run file"),
        Binding("f6", "stop_run", "Stop the run", show=False, priority=True),
        Binding("f4,ctrl+shift+p", "toggle_markdown_preview",
                "Toggle Markdown preview", show=False),
        Binding("ctrl+b,ctrl+1", "show_file_browser", "Files panel",
                show=False),
        Binding("ctrl+t,ctrl+2", "show_customizer_panel", "Customize panel",
                show=False),
        Binding("ctrl+l,ctrl+3", "show_runner_panel", "Runner panel",
                show=False),
        Binding("f1,ctrl+4", "show_shortcuts", "Shortcuts"),
        Binding("ctrl+g,ctrl+shift+c", "open_ai_chat", "Chat with the cat",
                show=False, priority=True),
        # not priority, so inside the editor Ctrl+Shift+arrows keep selecting
        # by word; F7/F8 reach the app from anywhere
        Binding("f8,ctrl+shift+right", "extend_side_panel", "Widen panel",
                show=False),
        Binding("f7,ctrl+shift+left", "reduce_side_panel", "Narrow panel",
                show=False),
        Binding("ctrl+shift+up", "hide_top_bar", "Hide top bar", show=False,
                priority=True),
        Binding("ctrl+shift+down", "unhide_top_bar", "Show top bar",
                show=False, priority=True),
        Binding("ctrl+q", "quit", "Quit", priority=True), ]

    def __init__(self) -> None:
        super().__init__()

        self.tabbed_editor = None

        self._init_config()
        self._init_core_state()
        self._init_dialogs()
        self._init_themes()
        self._init_features()
        self._init_layout()

    def _init_core_state(self) -> None:
        self.documents = DocumentContext()
        self.tab_lifecycle = TabLifecycle(self.documents)
        self.side_panel_width_percentage = DEFAULT_SIDE_PANEL_WIDTH_PERCENTAGE
        self.languages = supported_languages()
        self.desc_key_pairs = ([("Find a command", self.COMMAND_PALETTE_BINDING)]
                               + [(b.description, b.key) for b in self.BINDINGS]
                               + CONTEXT_SHORTCUTS)

    def _init_config(self) -> None:
        self.config = AppConfig.load()
        self.app_theme = self.config.app_theme
        self.editor_theme = self.config.editor_theme

    def _init_dialogs(self) -> None:
        self.dialog_handler = get_dialog_handler(
            self.push_screen_wait, self.config.system_file_picker)

    def _init_themes(self) -> None:
        for theme in CUSTOM_APP_THEMES:
            self.register_theme(theme)
        self.theme = self.app_theme

    def _init_features(self) -> None:
        self.editor_controller = EditorController(self.documents)
        self.customizer_controller = CustomizerController(self.app)

        self.file_browser = FileBrowser(on_open_file=self.open_file_in_tab)

        self.customizer_panel = CustomizerPanel(APP_THEMES, self.app_theme,
                                                EDITOR_THEMES,
                                                self.editor_theme,
                                                self.languages,
                                                self.customizer_controller)

        # min_width=1 so output wraps to whatever width the panel has
        self.runner = RichLog(highlight=True, markup=False, wrap=True, min_width=1,
                              id="runner-output", auto_scroll=True, )
        self.runner.border_title = "Runner"
        self._runner_shows_hint = False

        self.file_workflow = FileWorkflow(documents=self.documents,
                                          dialogs=self.dialog_handler,
                                          notify=self.notify,
                                          ask=self.push_screen_wait,
                                          start_folder=lambda: Path(
                                              self.file_browser.path))

    def _init_layout(self):
        self.layout_controller = LayoutController(self.app)

    def compose(self) -> ComposeResult:
        """Create the screen layout."""

        self.tabbed_editor = TabbedContent(classes="tabbed-editor",
                                           id="tabbed-editor")

        yield Vertical(TopBar(), Horizontal(SideBar(),
                                            ContentSwitcher(self.file_browser,
                                                            self.customizer_panel,
                                                            self.runner,
                                                            id="side-panel",
                                                            initial="file-browser", ),
                                            self.tabbed_editor,
                                            classes="main-screen", ),
                       Footer(), )

    def on_mount(self) -> None:
        """Mount Welcome tab and start LLM, if applicable."""

        welcome_tab = TabPane(title="Welcome", id=WELCOME_TAB_ID)
        self.tabbed_editor.add_pane(welcome_tab)
        welcome_tab.mount(Markdown(WELCOME_MESSAGE))

        self.layout_controller.refresh_rail()

        # start in the tree, so the first keypress browses files
        self.file_browser.focus()

        if self.config.llm_on_start:
            OllamaClient.serve()

    def get_key_display(self, binding: Binding) -> str:
        """Write keys the same way everywhere: footer, Shortcuts tab, tooltips, and welcome text."""

        if binding.key_display:
            return binding.key_display
        return format_shortcut(binding.key)

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        """Offer every bound action in the command palette, with its shortcut as help."""

        for binding in self.BINDINGS:
            yield SystemCommand(binding.description,
                                format_shortcut(binding.key),
                                partial(self.run_action, binding.action))

    def key_color(self) -> str:
        """The theme color used for keys in the footer, reused by the Shortcuts tab."""

        variables = self.get_css_variables()
        return variables.get("footer-key-foreground", variables["primary"])

    def muted_color(self) -> str:
        """Muted text as a solid color (60% foreground on the background), for Rich text."""

        variables = self.get_css_variables()
        return (Color.parse(variables["background"])
                .blend(Color.parse(variables["foreground"]), 0.6).hex)

    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
        self._mark_editing_area()

    def on_descendant_blur(self, event: events.DescendantBlur) -> None:
        self.call_after_refresh(self._mark_editing_area)

    def _mark_editing_area(self) -> None:
        """Light the tab underline while the editor area holds the keyboard."""

        if self.tabbed_editor is None:
            return
        focused = self.focused
        self.tabbed_editor.set_class(
            focused is not None
            and self.tabbed_editor in focused.ancestors_with_self, "-editing")

    def on_tabbed_content_tab_activated(self, event) -> None:
        self.layout_controller.refresh_rail()

        document = self._get_active_document()
        self.customizer_panel.show_language(document.language
                                            if document else None)

    @on(Editor.Changed)
    def on_editor_changed(self, event: Editor.Changed) -> None:
        """Keep the unsaved-changes mark on the tab in step with the document."""

        if isinstance(event.text_area, Editor):
            self._refresh_tab_title(event.text_area.document_id)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks for the File menu or switching panels."""

        match event.button.id:
            case "file-menu":
                self.push_screen(file_menu(event.button.region),
                                 self._run_file_action)

            case "file-browser":
                self.layout_controller.show_side_panel(SidePanelId.FILE_BROWSER)

            case "customizer":
                self.layout_controller.show_side_panel(SidePanelId.CUSTOMIZER)

            case "runner":
                self.action_show_runner_panel()

            case "cat-me":
                self.action_open_ai_chat()

            case _:
                return

    def _run_file_action(self, action: str | None) -> None:
        """Run the action picked from the File menu; None means it was closed."""

        match action:
            case "open-file":
                self.open_file_dialog()

            case "open-folder":
                self.open_folder_dialog()

            case "new-file":
                self.create_a_file()

    def action_open_file(self) -> None:
        self.open_file_dialog()

    def action_open_folder(self) -> None:
        self.open_folder_dialog()

    def action_new_file(self) -> None:
        self.create_a_file()

    def action_show_file_browser(self) -> None:
        self.layout_controller.show_side_panel(SidePanelId.FILE_BROWSER)
        self.file_browser.focus()

    def action_show_customizer_panel(self) -> None:
        self.layout_controller.show_side_panel(SidePanelId.CUSTOMIZER)

    def action_show_runner_panel(self, min_width: float = 0) -> None:
        self.layout_controller.show_side_panel(SidePanelId.RUNNER_OUTPUT,
                                               min_width)
        if not self.runner.lines:
            self.runner.write(Text(RUNNER_EMPTY,
                                   style=f"italic {self.muted_color()}"))
            self._runner_shows_hint = True

    def action_show_shortcuts(self) -> None:
        """Open the key mappings inside a new tab in the tabbed editor."""

        tab = ShortcutsTab(self.desc_key_pairs, self.key_color(),
                           self.muted_color())
        self._open_or_focus_tab(tab)

    def action_toggle_markdown_preview(self) -> None:
        """Toggle the active markdown tab between the editor and its rendered preview."""

        tab = self.tabbed_editor.active_pane
        editors = tab.query(Editor) if tab else None
        if not editors or not is_markdown_editor(editors.first()):
            self.notify("Preview works on Markdown files. This tab isn't one.")
            return

        toggle_preview(tab)

    def action_open_ai_chat(self) -> None:
        """Start the LLM in the background, then create/switch to the Cat Me tab."""

        # the chat pane explains what's missing if Ollama isn't installed
        OllamaClient.serve()

        tab = ChatPane()
        self._open_or_focus_tab(tab)

    def action_extend_side_panel(self) -> None:
        self.layout_controller.adjust_side_panel(reduce=False)

    def action_reduce_side_panel(self) -> None:
        self.layout_controller.adjust_side_panel()

    def action_hide_top_bar(self) -> None:
        self.layout_controller.hide_top_bar()
        self.notify("Top bar hidden. Ctrl+Shift+↓ brings it back, or find "
                    "\"Show top bar\" with Ctrl+P.")

    def action_unhide_top_bar(self) -> None:
        self.layout_controller.show_top_bar()

    def action_delete_selected_file(self) -> None:
        self._delete_selected_item()

    @work(exclusive=True, group="prompts")
    async def _delete_selected_item(self) -> None:
        """Delete the selected file or folder after asking, and close any open document for it."""

        path = self.file_browser.selected_path
        if not path:
            return

        reason = self.file_browser.protected_reason(path)
        if reason:
            self.notify(f"Catnip won't delete {path.name or path}: {reason}.",
                        severity="warning")
            return

        file_count = count_files(path) if path.is_dir() else 0
        if await self.push_screen_wait(
                delete_modal(path, file_count)) != "delete":
            return

        if not self.file_browser.delete_path(path):
            return

        # close tabs for the file, or for anything inside the folder
        for doc_id in self.documents.close_under(path):
            self.tabbed_editor.remove_pane(doc_id)

        self.notify(f"Deleted {path.name}. Ctrl+Z in the file tree "
                    "brings it back.")

    @work(exclusive=True, group="prompts")
    async def action_save_file(self) -> None:
        """
        Save the currently active document.

        If the active tab represents a document managed by DocumentContext,
        the document is saved to disk. If the document has not been saved
        before, the user is prompted to choose a save location.

        Non-document tabs (e.g. welcome screen, shortcuts, AI chat) are ignored.
        """

        document = self._get_active_document()
        if document is None:
            return

        if document.path is None:
            # finalize untitled document
            file_path = await self.file_workflow.save_as(document)
            if not file_path:
                return

            # replace tab for unsaved document and reload file browser
            self.tab_lifecycle.on_tab_closed(document.id)
            self.tabbed_editor.remove_pane(document.id)

            self.open_file_in_tab(file_path)

            self._show_file_browser_at(file_path.parent)
        else:
            self.file_workflow.save_on_dirty(document)
            self._refresh_tab_title(document.id)

    def _get_active_document(self) -> Optional[Document]:
        """Return the Document associated with the currently active tab, if any."""

        tab = self.tabbed_editor.active_pane
        if not tab:
            return None

        return self.documents.try_get(tab.id)

    def _refresh_tab_title(self, doc_id: str) -> None:
        """Show the document's title on its tab, marked when it has unsaved changes."""

        document = self.documents.try_get(doc_id)
        if not document or not is_open(doc_id, self.tabbed_editor):
            return

        mark = UNSAVED_MARK if document.dirty else ""
        self.tabbed_editor.get_tab(doc_id).label = Content(
            f"{document.title}{mark}")

    def _show_file_browser_at(self, path: Path) -> None:
        """Navigate the file browser to the given path and make it visible."""

        browser = self.file_browser
        browser.path = Path(path).resolve()
        browser.reload()
        self.layout_controller.show_side_panel(SidePanelId.FILE_BROWSER)

    @work(exclusive=True, group="prompts")
    async def action_save_file_as(self) -> None:
        """
        Save the currently active document under a new file path.

        If the active tab represents a document managed by DocumentContext,
        the user is prompted to choose a new save location. The document is
        then persisted to disk and its identity (path, title, dirty state)
        is updated accordingly.

        Non-document tabs are ignored.
        """

        document = self._get_active_document()
        if document is None:
            return

        file_path = await self.file_workflow.save_as(document)
        if not file_path:
            return

        folder_path = file_path.parent
        self._show_file_browser_at(folder_path)

    def action_close_tab(self) -> None:
        self._close_active_tab()

    @work(exclusive=True, group="prompts")
    async def _close_active_tab(self) -> None:
        """
        Close the currently active tab.

        If the active tab corresponds to a document managed by DocumentContext and
        the document has unsaved changes, the user is asked to save, not save, or
        cancel; cancelling keeps the tab open.

        Tabs that do not represent documents (e.g. welcome screen, key mappings,
        AI chat) are closed immediately without any save prompt.
        """

        await self.file_workflow.close_active_tab(self.tabbed_editor,
                                                  self.tab_lifecycle)
        # saving an untitled tab on close may have created a file
        self.file_browser.reload()

    def action_quit(self) -> None:
        self._quit_after_saving()

    @work(exclusive=True, group="prompts")
    async def _quit_after_saving(self) -> None:
        """
        Quit the application, asking about each document with unsaved changes first.

        Cancelling any of those questions keeps the app open. Non-document tabs
        (e.g. welcome screen, key mappings, AI chat) are ignored.
        """

        if not await self.file_workflow.resolve_all_before_exit(
                self.tabbed_editor, self.tab_lifecycle):
            return

        OllamaClient.shutdown()
        self.exit()

    def action_run_script(self) -> None:
        """
        Run the currently active document using a temp file.

        The document is NOT auto-saved. Unsaved changes are written to a
        temporary file under ~/.catnip/tmp and executed from there, in the
        background so the app stays responsive while the script runs.
        """

        if self.runner.border_subtitle:
            self.notify("Something is already running. F6 stops it.",
                        severity="warning")
            return

        try:
            target = prepare_runnable_file(self.tabbed_editor, self.documents)
        except NotRunnableError as error:
            self.notify(str(error), severity="warning")
            return

        # output needs room to read: open the runner at half the screen or more
        self.action_show_runner_panel(min_width=RUNNER_MIN_WIDTH)
        if self._runner_shows_hint:
            self.runner.clear()
            self._runner_shows_hint = False

        # each run opens with a heading, so separate runs read as blocks
        title = self._get_active_document().title
        heading = self.get_css_variables()["markdown-h1-color"]
        self.runner.write(Text.assemble((RUNNER_PROMPT, f"bold {heading}"),
                                        (f" {title}", "bold")))
        self.runner.border_subtitle = f"running {title} · F6 stops"
        self._run_in_background(target)

    def action_stop_run(self) -> None:
        if not runner.stop_current_run():
            self.notify("Nothing is running.")

    @work(thread=True, exclusive=True, group="runner")
    def _run_in_background(self, target: RunTarget) -> None:
        result = runner.run_file(target)
        self.call_from_thread(self._show_run_result, result)

    def _show_run_result(self, result: RunResult) -> None:
        """Print a finished run's output followed by how it ended."""

        variables = self.get_css_variables()
        if result.output.strip():
            self.runner.write(Text(result.output.rstrip()))

        elapsed = f"{result.elapsed:.1f}s"
        if result.exit_code == 0:
            status = Text(f"✓ finished in {elapsed}",
                          style=variables["text-success"])
        elif result.exit_code is not None:
            status = Text(f"✗ exited with code {result.exit_code} after {elapsed}",
                          style=variables["text-error"])
        else:
            status = Text(f"✗ {result.problem}", style=variables["text-error"])
        self.runner.write(status)
        self.runner.write("")
        self.runner.border_subtitle = ""

    @work(exclusive=True, group="prompts")
    async def open_file_dialog(self) -> None:
        """Ask for files and open them in editor tabs."""

        try:
            file_paths = await self.dialog_handler.select_file(
                Path(self.file_browser.path))
        except DialogUnavailableError as error:
            self.notify(str(error), severity="error", timeout=8)
            return
        if not file_paths:
            return

        for file in file_paths:
            self.open_file_in_tab(file)

        folder_path = file_paths[0].parent
        self._show_file_browser_at(folder_path)

    @work(exclusive=True, group="prompts")
    async def open_folder_dialog(self) -> None:
        """Ask for a folder and load it into the file browser."""

        try:
            folder_path = await self.dialog_handler.select_folder(
                Path(self.file_browser.path))
        except DialogUnavailableError as error:
            self.notify(str(error), severity="error", timeout=8)
            return
        if not folder_path:
            return

        self._show_file_browser_at(folder_path)

    def open_file_in_tab(self, file_path: Path) -> None:
        """
        Open a file in the editor as a tab.

        This method delegates document loading and lifecycle management to
        DocumentContext. If the file is already open, the existing tab is
        activated. Otherwise, a new editor tab is created and populated
        with the file content. Files that aren't readable text are reported
        instead of opened.
        """

        try:
            document = self.documents.open(file_path.resolve())
        except UnicodeDecodeError:
            self.notify(f"Can't open {file_path.name}: it isn't a UTF-8 text file.",
                        severity="error")
            return
        except OSError as error:
            self.notify(f"Can't open {file_path.name}: {error.strerror}.",
                        severity="error")
            return

        tab = TabPane(id=document.id, title=Content(document.title))
        self._open_or_focus_tab(tab, document)

    def create_a_file(self) -> None:
        """
        Create a new untitled document and open it in the editor.

        This method delegates untitled document creation to DocumentContext,
        then creates a corresponding editor tab and mounts a text editor
        initialized with the document's default state.
        """

        document = self.documents.create_untitled()

        tab = TabPane(id=document.id, title=document.title)
        self._open_or_focus_tab(tab, document)

    def _mount_editor_for_document(self, tab: TabPane, document) -> None:
        """Create and mount an Editor widget for the given document inside the provided tab, then focus it."""

        text_area = Editor.for_document(document_id=document.id,
                                        controller=self.editor_controller,
                                        language=document.language or "markdown",
                                        soft_wrap=True, )
        register_custom_editor_theme(text_area)
        text_area.theme = resolve_editor_theme(self.editor_theme, self.theme,
                                               self.current_theme.dark)
        text_area.load_text(document.content or "")

        tab.mount(text_area)
        text_area.focus()

    def _open_or_focus_tab(self,
                           tab: TabPane,
                           document: Optional[Document] = None) -> None:
        """Open a new tab or focus an existing one, mounting and focusing an editor if a document is provided."""

        if not is_open(tab.id, self.tabbed_editor):
            self.tabbed_editor.add_pane(tab)
            if document is not None:
                self.call_after_refresh(
                    lambda: self._mount_editor_for_document(tab, document))
        else:
            editors = self.tabbed_editor.get_pane(tab.id).query(Editor)
            if editors:
                self.call_after_refresh(editors.first().focus)

        self.tabbed_editor.active = tab.id


if __name__ == "__main__":
    app = CatnipApp()
    app.run()
