import asyncio
import shutil
import socket
import subprocess

import psutil

# used when it has been pulled; otherwise any chat model the user has is fine
PREFERRED_MODEL = "qwen3:8b"
OLLAMA_PORT = 11434


class OllamaError(Exception):
    """Raised when Ollama runs but does not produce an answer."""


class OllamaClient:
    _started_pid = None

    @staticmethod
    def is_installed() -> bool:
        """Return True if the ollama command is on PATH."""

        return shutil.which("ollama") is not None

    @staticmethod
    def is_running() -> bool:
        """Return True if an Ollama server is listening on its local port."""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", OLLAMA_PORT)) == 0

    @classmethod
    def serve(cls) -> bool:
        """
        Start Ollama serve in the background if it is installed and not already running.
        This returns immediately; await wait_until_ready() before talking to the model.

        @Returns:
            False if Ollama is not installed, True otherwise.
        """
        if not cls.is_installed():
            return False
        if cls._started_pid is not None or cls.is_running():
            return True

        proc = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)

        cls._started_pid = proc.pid
        return True

    @classmethod
    async def wait_until_ready(cls, timeout: float = 10.0) -> bool:
        """Wait without blocking the UI until the server accepts connections."""

        for _ in range(int(timeout / 0.25)):
            if cls.is_running():
                return True
            await asyncio.sleep(0.25)
        return False

    @staticmethod
    async def installed_models() -> list[str]:
        """Return the chat models pulled on this machine, most recently changed first."""

        proc = await asyncio.create_subprocess_exec(
            "ollama", "list",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL)
        output, _ = await proc.communicate()
        rows = output.decode("utf-8", errors="replace").splitlines()[1:]
        names = [row.split()[0] for row in rows if row.strip()]
        # embedding models (nomic-embed-text, mxbai-embed-large…) can't chat
        return [name for name in names if "embed" not in name.lower()]

    @classmethod
    async def detect_model(cls, preferred: str = PREFERRED_MODEL) -> str | None:
        """
        Pick the model to chat with: the preferred one when it's pulled,
        otherwise the most recently changed chat model.

        @Returns:
            None if no chat model has been pulled.
        """

        models = await cls.installed_models()
        if preferred in models:
            return preferred
        return models[0] if models else None

    @staticmethod
    async def load_model(model: str) -> bool:
        """
        Load the model into memory without asking it anything, so the first
        answer starts sooner. Ollama keeps it loaded for a few minutes.
        """

        # with no prompt and stdin closed, ollama run loads the model and exits
        proc = await asyncio.create_subprocess_exec(
            "ollama", "run", model,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL)
        return await proc.wait() == 0

    @classmethod
    def shutdown(cls):
        """Stop Ollama serve started by this app."""

        if cls._started_pid is None:
            return
        try:
            proc = psutil.Process(cls._started_pid)
            proc.terminate()
        except psutil.NoSuchProcess:
            pass
        finally:
            cls._started_pid = None

    @staticmethod
    async def stream_response(model: str, prompt: str):
        """Run the Ollama CLI with the given model and prompt and yield streamed response lines."""

        # thinking models (qwen3, deepseek-r1…) would print their reasoning,
        # and the CLI's own word wrap writes cursor codes; the chat wraps itself.
        # stdin is closed: when it isn't a terminal, ollama reads it as more
        # prompt and waits for an end that never comes
        proc = await asyncio.create_subprocess_exec("ollama", "run", model,
                                                    prompt, "--hidethinking",
                                                    "--nowordwrap",
                                                    stdin=asyncio.subprocess.DEVNULL,
                                                    stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.DEVNULL, )
        async for line in proc.stdout:
            yield line.decode("utf-8", errors="replace")

        if await proc.wait() != 0:
            raise OllamaError(f"ollama run exited with code {proc.returncode}")
