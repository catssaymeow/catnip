# 🍀 Catnip
## A terminal-based, Textual-powered file browser and more.
<img width="1082" height="799" alt="catnip-theme" src="https://github.com/user-attachments/assets/cf51caa6-9942-41a2-ba46-20c5ef089071" />

## 🌱 About this project
Catnip is **not just an app** — it is my personal journey of becoming a self‑learning software developer.
Some features may evolve quickly, change direction, or exist mainly as learning experiments.  
If you’re also learning, curious, or enjoy thoughtful software design, you’re very welcome here.


##  🧶 Features
- Tabbed Editor with syntax highlighting for multiple languages
- File Explorer with double-click to open, and deletes you can undo (Ctrl+Z)
- Run Python, JavaScript, TypeScript, and Java files from the editor (Ctrl+R, F6 stops)
- AI Chat tab (Ollama) for instant help
- Custom Themes with live switching


## 🎏 Getting Started
### 1️⃣ Prerequisites
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (installs Python 3.12+ for you if it's missing)
- Optional: zenity on macOS and Linux, only if you'd rather open and save with your system's file dialog. Catnip's own in-terminal picker works everywhere, including over SSH; set `"system_file_picker": true` in `~/.config/catnip/config.json` to switch.
- [Ollama](https://ollama.com) and any chat model, only for the Cat Me chat. Catnip uses `qwen3:8b` when it's pulled, otherwise the chat model you used most recently (`install.sh` offers to set up Ollama and `qwen3:8b`)

### 2️⃣ Installation
1. Clone the repository:
`git clone git@github.com:catssaymeow/catnip.git`
2. Move the folder to your home directory or another permanent location of your choice.  
⚠️ Do this before running the installer — if you move the folder later, the `catnip` command will break. To fix it, rerun the installer with `./install.sh --relink`.
3. Navigate into the catnip directory and run the installation script:
```bash
cd catnip
./install.sh
```

### Development
Dependencies are declared in `pyproject.toml` and pinned in `uv.lock`.
```bash
uv sync              # install everything, including dev tools (black)
uv add <package>     # add a dependency and update uv.lock
uv lock --upgrade    # move dependencies to the newest versions allowed by pyproject.toml
```

### 3️⃣ Running Catnip
```
catnip
```
