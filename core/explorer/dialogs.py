import asyncio
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Awaitable, Callable, Optional

from textual.screen import ModalScreen

from ui.modals.path_modal import PathModal, PickMode

if sys.platform.startswith("win"):
    from tkinter import Tk, filedialog

ZENITY_MISSING = ("Can't open the system file picker because zenity isn't "
                  "installed. Install it with `brew install zenity` or your "
                  "package manager, then try again.")

# shows a modal screen and waits for what it returns
Ask = Callable[[ModalScreen], Awaitable[Optional[Path]]]


class DialogUnavailableError(Exception):
    """Raised when the system file dialog can't be shown."""


class BaseDialogHandler(ABC):
    """Abstract base class for handling file and folder selection dialogs."""

    @abstractmethod
    async def select_file(self, start: Path) -> Optional[list[Path]]:
        """Select one or more files and return their paths, or None if cancelled."""

    @abstractmethod
    async def select_folder(self, start: Path) -> Optional[Path]:
        """Select a folder and return its path, or None if cancelled."""

    @abstractmethod
    async def select_save_path(self, start: Path,
                               file_name: str) -> Optional[Path]:
        """Choose where to save a file and return its path, or None if cancelled."""


class TerminalDialogHandler(BaseDialogHandler):
    """In-terminal pickers: work everywhere, including over SSH."""

    def __init__(self, ask: Ask):
        self.ask = ask

    async def select_file(self, start: Path) -> Optional[list[Path]]:
        path = await self.ask(PathModal(PickMode.FILE, start))
        return [path] if path else None

    async def select_folder(self, start: Path) -> Optional[Path]:
        return await self.ask(PathModal(PickMode.FOLDER, start))

    async def select_save_path(self, start: Path,
                               file_name: str) -> Optional[Path]:
        return await self.ask(PathModal(PickMode.SAVE, start, file_name))


class TkinterDialogHandler(BaseDialogHandler):
    """System file dialogs using Tkinter on Windows."""

    async def select_file(self, start: Path) -> Optional[list[Path]]:
        root = Tk()
        root.withdraw()
        file_paths = filedialog.askopenfilenames(initialdir=start)
        root.destroy()
        return [Path(file) for file in file_paths] if file_paths else None

    async def select_folder(self, start: Path) -> Optional[Path]:
        root = Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory(initialdir=start)
        root.destroy()
        return Path(folder_path) if folder_path else None

    async def select_save_path(self, start: Path,
                               file_name: str) -> Optional[Path]:
        root = Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(initialdir=start,
                                                 initialfile=file_name)
        root.destroy()
        return Path(file_path) if file_path else None


class ZenityDialogHandler(BaseDialogHandler):
    """System file dialogs using Zenity on Linux/macOS."""

    async def select_file(self, start: Path) -> Optional[list[Path]]:
        output = await self._zenity("--file-selection", "--multiple",
                                    "--separator=\n", f"--filename={start}/")
        return [Path(line) for line in output.splitlines()] if output else None

    async def select_folder(self, start: Path) -> Optional[Path]:
        output = await self._zenity("--file-selection", "--directory",
                                    f"--filename={start}/")
        return Path(output) if output else None

    async def select_save_path(self, start: Path,
                               file_name: str) -> Optional[Path]:
        output = await self._zenity("--file-selection", "--save",
                                    "--confirm-overwrite",
                                    f"--filename={start / file_name}")
        return Path(output) if output else None

    @staticmethod
    async def _zenity(*args: str) -> Optional[str]:
        """Run zenity off the event loop and return what it printed, or None if cancelled."""

        try:
            result = await asyncio.to_thread(
                subprocess.run, ["zenity", *args], capture_output=True,
                text=True)
        except FileNotFoundError:
            raise DialogUnavailableError(ZENITY_MISSING)
        output = result.stdout.strip()
        return output if result.returncode == 0 and output else None


def get_dialog_handler(ask: Ask, use_system_picker: bool) -> BaseDialogHandler:
    """
    Return the in-terminal picker, or the OS file dialog when the config asks
    for it and one is available on this machine.
    """

    if use_system_picker:
        if sys.platform.startswith("win"):
            return TkinterDialogHandler()
        if shutil.which("zenity"):
            return ZenityDialogHandler()
    return TerminalDialogHandler(ask)
