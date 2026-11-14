# Product

<!-- impeccable:product-schema 1 -->

## Platform

terminal

(Catnip is a terminal TUI built with Textual. It is none of the schema's web/ios/android values; renders are terminal cells styled with TCSS, verified by running the app headlessly and screenshotting at representative terminal sizes.)

## Users

- Primary: the author (catssaymeow), a self-learning software developer, using Catnip as a daily driver for browsing and editing files in the terminal. The project doubles as their learning journey, so features may evolve or exist as experiments.
- Secondary (confirmed): other terminal-dwelling developers who clone and install it. Design must hold up for strangers' folders, files, and habits, not just the author's.

## Product Purpose

A terminal-based file browser and editor: browse a directory tree, open files in tabbed editors with syntax highlighting, run scripts, chat with a local AI, and restyle the app live. Success is the author (and other devs) genuinely reaching for it for quick terminal work, while the codebase keeps teaching its maker.

## Positioning

A cozy personality editor: a terminal editor with a warm, playful cat identity. The feel is the differentiator — neighboring TUI editors are faster or more featureful, but none are this one's kind of cozy.

## Operating Context

- Runs inside the user's terminal emulator at arbitrary sizes; layout must stay fluid across resizes (fixed as of 2026-11-14).
- Installed by cloning the repo and running `install.sh`, which links a `catnip` command; moving the folder breaks the link (`./install.sh --relink` repairs it).
- Dependencies are managed with uv (`pyproject.toml` + `uv.lock`); Python ≥3.12; Textual 7.x, Rich, Pygments, psutil.
- AI chat ("Cat Me" tab) starts a local `ollama serve` and streams from `qwen3:8b`; Ollama must be installed on the machine. The app can shut the server down on quit.
- Script running executes the active document from a temp file under `~/.catnip/tmp` and prints to a runner panel.
- App config persists at `~/.config/catnip/config.json` (themes, LLM-on-start).

## Capabilities and Constraints

- Shell: top bar (Open Folder / Open Files / New File), emoji icon rail (file browser, customizer, runner, shortcuts, AI chat), collapsible side panel at 0/25/50/100% widths, tabbed editor, footer with key hints.
- Tabbed editor with syntax highlighting for: Python, JSON, Markdown, YAML, TOML, Rust, HTML, CSS, XML, SQL, JavaScript, TypeScript, Java, Bash, Go.
- File explorer with double-click open and delete-with-confirmation; native OS dialogs for open/save.
- Theme customizer with live switching: Textual built-in themes plus the custom "catnip" theme (app + editor variants).
- AI direction (confirmed): local Ollama only. The `together` dependency in pyproject.toml is vestigial, imported nowhere, and can be removed; no hosted/remote model option is planned.
- Keyboard-first: every panel and action has a Ctrl binding; the shortcuts tab is generated from the binding list, so binding descriptions are user-facing copy.

## Brand Commitments

- The cat identity is the product's voice and is binding: the name Catnip, "purr purr" welcome copy, the "Cat Me" chat tab, cat/emoji iconography on the rail, and the cat-themed README. Playful, warm, never corporate.
- The custom "catnip" theme (pastel green primary `#a6e3a1`, rose error `#f38ba8`, deep soft dark `#1e1e2e` family) is the house palette for both app and editor.
- Emoji as icons is the established TUI-native icon language here; do not replace it with drawn icon sets.

## Evidence on Hand

- A real screenshot of the app is embedded in README.md (hosted on GitHub).
- No testimonials, user counts, benchmarks, or press exist; future surfaces must not fabricate any.

## Product Principles

1. Cozy over clinical: warmth and personality are product requirements, expressed through precise details, not noise.
2. The terminal is the home field: respect its conventions (keyboard-first, fluid resize, theme-token colors), never fight them.
3. Hold up for strangers: features must work on any folder, any terminal size, any machine — not just the author's setup.
4. Local and self-contained: AI stays local (Ollama); the app owns what it starts and cleans up after itself.
5. A learning project that ships: experiments are welcome, but what lands in the default path must be finished and honest about its state.
