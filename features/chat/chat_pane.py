import asyncio
from typing import Optional

from textual import events, on
from textual.containers import Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import (TabPane, TextArea, Markdown, LoadingIndicator,
                             Static)

from .domain.chat_session import ChatSession
from .ollama_client import PREFERRED_MODEL, OllamaClient

WAKING = ("Zzz… the cat is waking up from a nap. One big stretch and I'm "
          "all yours.")
GREETING = ("*stretches across your keyboard* Mrrrow, I'm awake! Captain "
            "Chonky Orange here, purring through `{model}`. Ask me about your "
            "code or anything you're writing.")
NO_OLLAMA = ("Ollama isn't installed, so I can't wake up. Install it from "
             "ollama.com, then send your message again.")
NO_SERVER = ("Ollama didn't start in time. Check that `ollama serve` runs in "
             "a terminal, then send your message again.")
NO_MODEL = ("I need a chat model first. Run `ollama pull "
            f"{PREFERRED_MODEL}` (or any model you like) in a terminal, then "
            "send your message again.")
NO_LOAD = ("I couldn't load {model}. Run `ollama run {model}` in a terminal "
           "to see what's wrong, then send your message again.")
NO_ANSWER = ("Ollama stopped before answering. Run `ollama run {model}` in a "
             "terminal to see what's wrong, then try again.")


class ChatInput(TextArea):
    """Message box for the chat: Enter sends, Ctrl+J or Shift+Enter adds a new line."""

    class Submitted(Message):
        """Posted when the user presses Enter to send the message."""

    async def _on_key(self, event: events.Key) -> None:
        if event.key in ("enter", "ctrl+enter"):
            event.stop()
            event.prevent_default()
            self.post_message(self.Submitted())
        elif event.key in ("ctrl+j", "shift+enter"):
            event.stop()
            event.prevent_default()
            self.insert("\n")


class ChatPane(TabPane):
    """A chat-box for interacting with AI via Ollama."""

    def __init__(self, title: str = "Cat Me", tab_id: str = "cat-me"):
        super().__init__(title=title, id=tab_id)
        self.text_area: Optional[TextArea] = None
        self.message = None
        self.chat_session = ChatSession()
        # detected before each message, so a model pulled mid-chat is picked up
        self.model: Optional[str] = None

    def compose(self):
        """Create the chat UI layout."""

        yield Vertical(
            VerticalScroll(Static(WAKING, classes="ai-message chat-waking"),
                           LoadingIndicator(classes="chat-waking"),
                           classes="chat-log"),
            ChatInput(classes="chat-input",
                      placeholder="Ask the cat…  Enter sends, Ctrl+J adds a new line"),
            classes="chat-pane")

    def on_mount(self):
        """Focus the text area and wake the cat while the user starts typing."""

        self.text_area = self.query_one(".chat-input")
        self.text_area.focus()

        # its own group, so sending a message early doesn't cancel the wake-up
        self.run_worker(self._wake_up(), group="wake")

    async def _wake_up(self) -> None:
        """Start Ollama and load the model, then trade the nap note for a hello."""

        text_log = self.query_one(".chat-log")
        problem = await self._check_ollama()
        if problem is None and not await OllamaClient.load_model(self.model):
            problem = NO_LOAD.format(model=self.model)

        if problem:
            hello = Static(problem, classes="ai-message chat-status")
        else:
            hello = Markdown(GREETING.format(model=self.model),
                             classes="ai-message")
        # at the top, so it stays above anything sent while the cat was waking
        await text_log.mount(hello, before=0)
        await text_log.query(".chat-waking").remove()

    @on(ChatInput.Submitted)
    def on_chat_input_submitted(self) -> None:
        """Send the typed message."""

        self._send_current_message(self.query_one(".chat-log"))

    async def _send_message(self, text_log: VerticalScroll):
        """Handle sending user input to LLM and displaying the response."""

        loading = LoadingIndicator()
        await text_log.mount(loading)
        text_log.scroll_end(animate=False)

        problem = await self._check_ollama()
        if problem:
            await loading.remove()
            await self._show_status(text_log, problem)
            return

        try:
            buffer = ""
            response_widget = Markdown("", classes="ai-message")
            await text_log.mount(response_widget)

            first_chunk = True
            prompt = self.chat_session.build_prompt()
            async for chunk in OllamaClient.stream_response(self.model,
                                                            prompt):
                if first_chunk:
                    await loading.remove()
                    first_chunk = False

                buffer += chunk
                await response_widget.update(buffer)
                text_log.scroll_end(animate=False)
                await asyncio.sleep(0)

            if not buffer.strip():
                raise RuntimeError("empty response")
            self.chat_session.add_assistant_message(buffer)

        except Exception:
            if loading.is_mounted:
                await loading.remove()
            await self._show_status(text_log,
                                    NO_ANSWER.format(model=self.model))

    async def _check_ollama(self) -> Optional[str]:
        """
        Start Ollama if needed and pick the model to talk through; return a
        message describing what's missing, if anything.
        """

        if not OllamaClient.serve():
            return NO_OLLAMA
        if not await OllamaClient.wait_until_ready():
            return NO_SERVER
        self.model = await OllamaClient.detect_model()
        if self.model is None:
            return NO_MODEL
        return None

    @staticmethod
    async def _show_status(text_log: VerticalScroll, message: str) -> None:
        await text_log.mount(Static(message, classes="ai-message chat-status"))
        text_log.scroll_end(animate=False)

    def _send_current_message(self, text_log: VerticalScroll):
        user_message = self.text_area.text.strip()
        if not user_message:
            return

        self.chat_session.add_user_message(user_message)

        text_log.mount(Static(user_message, classes="user-message"))

        self.text_area.clear()
        self.run_worker(self._send_message(text_log), exclusive=True)
