# welcome message displayed in the starter screen
WELCOME_MESSAGE = """
### Purr purr, welcome to Catnip!
Pick a file from the tree on the left, or open a folder to settle into.

- **Enter** opens the highlighted file; **Ctrl+N** starts a new one.
- **Ctrl+S** saves, **Ctrl+W** closes the tab.
- **Ctrl+R** runs the file you're in: Python, JavaScript, TypeScript, or Java.
- **Ctrl+P** finds any command; **F1** lists every shortcut.
- **Ctrl+T** changes the look; **Ctrl+G** chats with the cat (needs Ollama).

### Syntax highlighting
> Python, JSON, Markdown, YAML, TOML, Rust, HTML, CSS, XML, SQL,
> JavaScript, TypeScript, Java, Bash, and Go.
"""

# prompt line shown in the runner output panel
RUNNER_PROMPT = "➜ (catnip):"

# shown in the runner output panel before anything has run
RUNNER_EMPTY = ("Nothing has run yet. Open a Python, JavaScript, TypeScript, "
                "or Java file and press Ctrl+R.")

# marks a tab whose document has unsaved changes
UNSAVED_MARK = " ●"

# width sizes for side panel and tabbed editor in percentages
WIDTH_SCALES = [0, 0.25, 0.5, 1]
DEFAULT_SIDE_PANEL_WIDTH_PERCENTAGE = WIDTH_SCALES[1]
# the runner opens at least this wide when a file runs, so output stays readable
RUNNER_MIN_WIDTH = WIDTH_SCALES[2]
