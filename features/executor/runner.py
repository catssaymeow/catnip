import os
import signal
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from utils.editor import RunnableLanguage, RunTarget

# scripts that need longer than this belong in a real terminal
RUN_TIMEOUT_SECONDS = 60

# the run in progress, so the app can stop it from the UI thread
_lock = threading.Lock()
_process: Optional[subprocess.Popen] = None
_stopped = False


@dataclass
class RunResult:
    """What a run printed and how it ended."""

    output: str
    exit_code: Optional[int]  # None when the run could not start or finish
    elapsed: float
    problem: Optional[str] = None  # user-facing reason when exit_code is None


class RunStopped(Exception):
    """Raised when the user stops a run; carries what it printed so far."""

    def __init__(self, output: str):
        super().__init__()
        self.output = output


def run_file(target: RunTarget) -> RunResult:
    """Run the target using the appropriate language runner based on its extension."""

    global _stopped
    _stopped = False

    file_path = target.file
    ext: RunnableLanguage = RunnableLanguage(file_path.suffix.lstrip("."))
    start = time.monotonic()

    try:
        output, exit_code = LANGUAGE_RUNNERS[ext](file_path, target.cwd)
        problem = None
    except FileNotFoundError as error:
        output, exit_code = "", None
        problem = f"{error.filename} isn't installed or isn't on your PATH."
    except subprocess.TimeoutExpired as error:
        output, exit_code = _text(error.output), None
        problem = (f"Stopped after {RUN_TIMEOUT_SECONDS}s. Run longer scripts "
                   "in a full terminal.")
    except RunStopped as stop:
        output, exit_code = stop.output, None
        problem = "Stopped."

    # name the file people know, not the temp copy that actually ran
    if str(file_path) != target.shown_as:
        output = output.replace(str(file_path), target.shown_as)

    return RunResult(output, exit_code, time.monotonic() - start, problem)


def stop_current_run() -> bool:
    """Stop the run in progress. Returns False when nothing was running."""

    global _stopped
    with _lock:
        if _process is None or _process.poll() is not None:
            return False
        _stopped = True
        _kill(_process)
        return True


def _kill(process: subprocess.Popen) -> None:
    """Kill the process and anything it started."""

    try:
        if os.name == "nt":
            process.kill()
        else:
            os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass  # it finished on its own


def _run(command: list[str], cwd: Path,
         env: Optional[dict[str, str]] = None) -> tuple[str, int]:
    """Run a command without a keyboard attached, so input() fails fast instead of hanging."""

    global _process
    with _lock:
        if _stopped:
            raise RunStopped("")
        _process = process = subprocess.Popen(
            command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            errors="replace", start_new_session=os.name != "nt")

    try:
        output, _ = process.communicate(timeout=RUN_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        _kill(process)
        output, _ = process.communicate()
        raise subprocess.TimeoutExpired(command, RUN_TIMEOUT_SECONDS,
                                        output=output)
    finally:
        with _lock:
            _process = None

    if _stopped:
        raise RunStopped(output)
    return output, process.returncode


def _text(output: Optional[bytes | str]) -> str:
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    return output or ""


def run_python(file_path: Path, cwd: Path) -> tuple[str, int]:
    # a temp copy lives elsewhere, so let it import the files beside the original
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        filter(None, [str(cwd), env.get("PYTHONPATH")]))
    return _run(["python3", str(file_path)], cwd, env)


def run_javascript(file_path: Path, cwd: Path) -> tuple[str, int]:
    return _run(["node", str(file_path)], cwd)


def run_typescript(file_path: Path, cwd: Path) -> tuple[str, int]:
    js_file = file_path.with_suffix(".js")

    try:
        output, exit_code = _run(["tsc", str(file_path)], cwd)
        if exit_code != 0:
            return output, exit_code

        return _run(["node", str(js_file)], cwd)

    finally:
        if js_file.exists():
            js_file.unlink()


def run_java(file_path: Path, cwd: Path) -> tuple[str, int]:
    # compile Java source
    output, exit_code = _run(["javac", str(file_path)], cwd)
    if exit_code != 0:
        return output, exit_code

    # detect generated .class files (javac may generate multiple)
    class_files = list(file_path.parent.glob("*.class"))
    if not class_files:
        return "Java compilation succeeded but no .class file was produced.", 1

    # the public class is named after the file; otherwise take the first one
    main_class = (file_path.stem
                  if file_path.with_suffix(".class") in class_files
                  else class_files[0].stem)

    try:
        return _run(["java", "-cp", str(file_path.parent), main_class], cwd)
    finally:
        # clean up all generated .class files
        for cf in class_files:
            if cf.exists():
                cf.unlink()


Runner = Callable[[Path, Path], tuple[str, int]]

LANGUAGE_RUNNERS: dict[RunnableLanguage, Runner] = {
    RunnableLanguage.PY: run_python,
    RunnableLanguage.JS: run_javascript,
    RunnableLanguage.TS: run_typescript,
    RunnableLanguage.JAVA: run_java,
}
