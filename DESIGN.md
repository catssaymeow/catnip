---
name: Catnip
description: A cozy, cat-themed terminal file browser and editor with a pastel garden palette on deep velvet dark.
colors:
  catnip-green: "#a6e3a1"
  seafoam-teal: "#94e2d5"
  peach-fuzz: "#fab387"
  butter-cream: "#f9e2af"
  rose-bud: "#f38ba8"
  nepeta-bloom: "#c9b0f7"
  moonlight-fur: "#e2e6de"
  whisker-sage: "#a7b0a5"
  plum-nap: "#423f56"
  twilight-panel: "#313244"
  dusk-surface: "#252532"
  midnight-velvet: "#1e1e2e"
spacing:
  cell: "1 cell"
  gap: "2 cells"
components:
  button-pill-rest:
    backgroundColor: "#a6e3a126"
    textColor: "{colors.catnip-green}"
    padding: "0 2"
    height: "1"
  button-pill-hover:
    backgroundColor: "{colors.catnip-green}"
    textColor: "{colors.midnight-velvet}"
    padding: "0 2"
    height: "1"
  button-pill-neutral-rest:
    backgroundColor: "#e2e6de14"
    textColor: "{colors.moonlight-fur}"
    padding: "0 2"
    height: "1"
  rail-button-rest:
    backgroundColor: "transparent"
    width: "3"
    height: "1"
  rail-button-focus:
    backgroundColor: "#a6e3a14d"
    width: "3"
    height: "1"
  runner-frame:
    borderColor: "#e2e6de26"
    textColor: "{colors.moonlight-fur}"
  rail-button-current:
    backgroundColor: "{colors.catnip-green}"
    textColor: "{colors.midnight-velvet}"
    width: "3"
    height: "1"
  side-panel:
    backgroundColor: "#31324466"
    padding: "0 1"
    width: "25%"
  chat-bubble-user:
    textColor: "{colors.catnip-green}"
    padding: "0 1"
    width: "max 70%"
---

# Design System: Catnip

## Overview

**Creative North Star: "The Sunny Windowsill"**

Catnip's interface is the spot a cat actually chooses: a warm, soft-lit place inside a disciplined structure. The structure is the terminal grid — deep velvet dark, exact cell alignment, keyboard-first economy. The warmth is pastel light falling onto it: catnip green, seafoam, peach, and butter tints that appear as washes and accents, never as floods. The result is cozy but never messy; every playful touch ("purr purr" copy, the sitting cat `ᓚᘏᗢ` on the Cat Me pill, Captain Chonky Orange in the Cat Me tab) sits on top of a quiet, flat, precise frame.

This is a terminal application (Textual/TCSS). Every styled value is theme-driven: TCSS references semantic variables (`$primary`, `$warning`, `$error`, `$panel`, `$surface`, `$boost`), and the custom **catnip** theme defines the house palette those variables resolve to. Users can live-switch to any Textual theme from the customizer, so the layout and tint logic must read correctly under any palette — the catnip theme is the authoritative expression, not the only one.

**Key Characteristics:**
- Deep soft dark ground with pastel garden accents, each hue carrying one meaning.
- Tonal depth only: translucent washes (15/25/40/70%) and `$boost`, never shadows.
- Soft-spoken controls that commit fully on interaction (tinted at rest, solid on hover/focus).
- Single-cell Unicode glyphs as the rail's icon language (the cat itself, `ᓚᘏᗢ`, sits on the Cat Me pill); box-drawing `round` borders as the shape language.
- The cat lives in voice, palette, and moments (greeting, empty states, setup help), not in decoration.
- Everything flows with the terminal: fractional/percent widths, fluid at any size.

## Colors

A pastel garden at dusk: six soft hues glowing on three layered darks, with warm off-white text.

### Primary
- **Catnip Green** (#a6e3a1): the life color, spent only on what is *current* or *primary*: the one primary action per group (Open Folder, Open/Save in pickers), the current rail icon, the tree cursor, the focused tab block, the active-tab underline while the editor holds the keyboard, user chat bubbles, the cursor. Never on chrome at rest (scrollbars, guides, frames, headings, key hints).

### Secondary
- **Seafoam Teal** (#94e2d5): supporting accent; operators, functions, and links in the editor. Used sparingly in chrome.
- **Nepeta Bloom** (#c9b0f7): the catnip flower. Keywords (including conditionals, loops, and exceptions) in syntax highlighting, and every Markdown heading in app content (Welcome, Cat Me) via the theme's `markdown-h*-color` variables. The runner's `➜ (catnip):` prompt borrows the same heading color, since each run is a section of the log.

### Tertiary
- **Peach Fuzz** (#fab387): the designated "accent" slot and the color of *keys*: footer key hints and the Shortcuts table's sendable keys (`footer-key-foreground`); numbers, list markers, and HTML tags in the editor.
- **Butter Cream** (#f9e2af): warning hue; setup problems the cat reports in Cat Me, types in syntax.
- **Rose Bud** (#f38ba8): error/destructive hue; Delete, Replace, and Don't save in dialogs, destructive dialog titles, failed runs, picker problems, errors. In the editor only for `html.end_tag_error`; never for ordinary syntax.

### Neutral
- **Moonlight Fur** (#e2e6de): warm off-white foreground; all body text.
- **Whisker Sage** (#a7b0a5): muted text — editor gutter and comments. A catnip-leaf gray-green rather than a borrowed blue-gray; clears 4.5:1 on every catnip surface and on Plum Nap selection.
- **Plum Nap** (#423f56): selection backgrounds (editor and inputs) and bracket matching. Every syntax hue except rose clears 4.5:1 on it.
- **Twilight Panel** (#313244): panel layer; side panel wash at 40% opacity.
- **Dusk Surface** (#252532): raised surface; the Screen background, cursor line, gutter.
- **Midnight Velvet** (#1e1e2e): deepest ground; editor background and text-on-accent color.

The pinned three (Catnip Green, Rose Bud, Midnight Velvet) come from the Catppuccin Mocha family; the rest of the palette is Catnip's own: neutrals and the flower/leaf hues are drawn from the catnip plant (Nepeta's lilac bloom, its downy sage leaves) so the palette tells the brand's story instead of reading as a stock theme.

### Named Rules
**The Theme Variable Rule.** TCSS never hardcodes a hex value. All color flows through semantic theme variables (`$primary`, `$warning`, `$error`, `$panel`, `$surface`, `$boost`, `$background`) so the customizer's live theme switching restyles every screen. The catnip theme is where hex lives.

**The One Meaning Rule.** Each pastel keeps one job: green = current/primary, peach = keys, butter = caution, rose = destructive/error, bloom = headings and keywords, teal = the editor's functions and operators. The one exception is the top bar's Cat Me pill, which wears the bloom: the flower is the cat's own color. Chrome at rest (scrollbars, tree guides, frames, modal borders, input frames, blockquote bars) is a neutral `$foreground` wash. Don't borrow a hue for a different meaning because it looks nice.

## Typography

**Display/Body/Mono Font:** the user's terminal monospace font. The app does not choose a family — it inherits whatever the terminal provides.

**Character:** one mono voice at one size; hierarchy is built entirely from weight, color, and space, never from font size.

### Hierarchy
- **Headings** (bold + Nepeta Bloom): section headers in Markdown content; pill labels, key hints, and the active tab are bold.
- **Body** (regular, Moonlight Fur): everything else. Reading content (the Welcome tab) is capped at a 90-cell measure.
- **Muted** (`$text-muted` / Whisker Sage, italic where supported): dotfiles, gutter numbers, comments, picker hints, keys a terminal may not send, de-emphasized metadata.

### Named Rules
**The One Size Rule.** The terminal has one glyph size. Emphasis comes from bold, color, and surrounding space. Never fake "large text" with figlet banners or doubled rows in app chrome.

## Layout

The shell is a fixed frame around a fluid center: a one-row top bar of pill buttons (padding `1 2 0 1`, so the File pill's left edge lines up with the rail; the File menu on the left, the Cat Me tab opener pushed to the right; Shortcuts lives on F1 in the footer), a 3-cell glyph icon rail, a collapsible side panel, and a tabbed editor that takes the remaining width (`1fr`). The side panel steps through 0 / 25% / 50% / 100% widths (F7 / F8) and keeps the width the user chose when switching panels; a hidden panel reopens at 25%, and running a file opens the runner at 50% or wider. When the panel fills the screen or disappears, the keyboard moves to whatever is still visible. All widths are relative so the layout reflows live with the terminal. Main content carries `1 1 0 1` padding (`0 1` when the top bar is hidden). Spacing rhythm is the cell: 1 cell of padding inside things, 2 cells where groups separate. The footer is Textual's key-hint bar, limited to Save, Run file, Shortcuts, Quit, and the command palette so it fits at 80 columns; keys are written the same way everywhere (`Ctrl+Shift+O`, `F1`). Every action's first key is one any terminal sends (Ctrl+letter or an F-key); kitty-only aliases come second and are dimmed in the Shortcuts table. Everything must remain usable at 80×24.

## Elevation & Depth

No shadows — a terminal has none. Depth is purely tonal: layers step from Midnight Velvet (deepest, editor) through Dusk Surface (screen) to Twilight Panel (raised), and translucent washes signal interactivity — 15% hue tint for a resting pill, 25% for focus, 40% for the side panel's wash (70% while it holds the keyboard), `$boost` for hover on transparent controls. Scrollbars are slim (1 cell) and neutral: a `$foreground` 35% thumb on a 5% track, primary only while dragged.

**The Wash Rule.** Depth and state are expressed as translucent color washes over the dark ground, never as borders-everywhere or bright fills at rest.

## Shapes

The form language is the terminal cell. Buttons are borderless one-row pills whose shape is pure background color. Containers that need an outline use box-drawing borders: `round` (rounded corners) for conversational/soft elements like chat bubbles, `panel` for utility panes like the runner output. No other border styles; no heavy double-line frames.

## Components

Component philosophy: **soft-spoken, then certain** — controls rest as quiet tints and commit to a full solid fill the moment you engage them.

### Buttons (top-bar pills)
- **Shape:** borderless one-liner, `height: 1`, 2 cells either side of the label (`padding: 0 1` plus Button's `line-pad: 1` in the top bar), bold label.
- **Rest:** 15% tint of the button's hue as background, `$text-<hue>` as text (contrast-safe in every theme). Neutral pills rest on an 8% foreground wash.
- **Hover / Focus:** flips solid — full hue background, `auto` text. No intermediate state. Neutral pills flip to primary.
- **Hue assignment:** in dialogs, one primary (green) action per group; the rest are neutral. Rose (`pill-error`) only for actions that destroy or discard work. In the top bar, `File ▾` is the primary pill and Cat Me is `pill-bloom` (from `$markdown-h1-color`), solid (`-current`) while its tab is showing.

### Dropdown menu (File, Customizer)
- **Style:** a `MenuModal` hanging directly under its button: an `OptionList` on `$panel` in a `round` border at `$foreground` 30%, the screen behind left undimmed. Labels on the left, keys in a right-hand peach column.
- **Highlight:** a 30% primary wash with bold foreground text, not a solid fill, so the peach keys stay readable.
- **Behavior:** ↑/↓ and Enter pick an action; Escape or a click outside closes it. Items: Open Folder (F3), Open File (Ctrl+O), New File (Ctrl+N).
- **Pickers:** the Customizer's App theme, Editor theme, and File language are `Dropdown` pills (`pill-neutral`, labelled `<current choice> ▾`, or the prompt while nothing is chosen) that open the same menu with the current choice ticked `✓` in `$text-primary` and highlighted. Long lists scroll; a menu opens upward when there's more room above its button, and is never narrower than it.

### Icon rail buttons
- **Style:** a single one-cell glyph on transparent, `width: 3` (one cell either side of the glyph), growing to a 5×3 block from 120 columns (`HORIZONTAL_BREAKPOINTS` puts `-wide` on the screen; `-compact` below), one row, 2-cell bottom margin, `$text-muted` at rest.
- **Hover:** `$boost` wash. **Focus:** 30% primary tint. **Current** (its panel is showing): solid primary with background-colored glyph.
- **Icons:** `▤` files · `◐` customize · `▷` runner. The rail only opens side panels; buttons that open tabs live in the top bar. Each must measure 1 cell (`rich.cells.cell_len`); no full-color emoji (they break cell width and the flat look), no drawn/SVG sets. Tooltips name the panel and its key.

### Tabs
- **Style:** Textual's TabbedContent under the active theme. Inactive labels at 70% foreground; the active label full foreground and bold; when the tab bar itself has focus, the active tab is a solid `$block-cursor` block. Tabs are titled in plain words ("Welcome", "Cat Me", file names); a document with unsaved changes gets a trailing ` ●`.
- **Focus cue:** the active-tab underline is primary at 35% at rest and full primary while the editor area holds the keyboard (`.tabbed-editor.-editing`, set from focus events because `:focus-within` doesn't restyle nested component classes). The side panel shows the same thing with its deeper wash. One cue per region; no focus frames around the editor.

### Side panel
- **Style:** 40% Twilight Panel wash over the surface, `padding: 0 1`, 25% width at rest, stepping 0/25/50/100%.
- **Scrollbars:** 1 cell, both axes, on any scrolling surface it hosts.

### Chat bubbles (Cat Me)
- **User:** catnip-green text in a `round` box-drawing border (primary-darken-2), `max-width: 70%`, left-aligned.
- **AI:** borderless, full-measure, 1 cell of top padding — the cat speaks plainly; the user's words get the bubble. An empty chat opens with a muted italic nap note ("Zzz… the cat is waking up from a nap…") over a 3-row loading indicator while Ollama starts and the detected model loads; once it's ready, the note is replaced in place by Captain Chonky Orange's greeting naming the model (or by the setup problem, if any); the input placeholder carries the send keys.
- **Setup problems** (no Ollama, no model, server not ready): borderless, `$text-warning`, naming the problem and the one command that fixes it.
- **Input:** framed like the path picker's field: `round` at `$foreground` 25%, `round $primary` while it has the keyboard.

### Dialogs
- **Style:** in-terminal `ModalScreen` (never a GUI dialog for a decision), `round` border at `$foreground` 30% on `$panel`, bold foreground title (`$text-error` for destructive dialogs), plain message, right-aligned pills. Escape always cancels. Destructive confirmations focus Cancel first.
- **Delete:** moves to Catnip's trash (`~/.catnip/trash`, emptied after 7 days), says how many files a folder holds, and Ctrl+Z in the file tree brings the last delete back. The open folder, the working directory, home, and their ancestors are refused with a warning toast instead of a dialog.

### Path picker
- **Style:** the dialog box at 80% × 80% (max 90 × 26): title, a path field in a `round` border (`$foreground` 25%, primary on focus), a muted one-line hint that turns `$text-error` to name a problem, a folder tree with the same `◦ ▸ ▾` glyphs as the file tree, then Open/Save (primary) and Cancel.
- **Behavior:** opens in the tree's folder (or the document's); paths display with `~`; Tab completes the last segment, ↓ moves into the tree, Backspace in the tree climbs a folder, Enter confirms. Save as pre-selects the file name's stem so typing renames and the extension stays; saving over a file asks first (Replace / Cancel). The OS dialog (zenity/Tk) is opt-in via `system_file_picker` in the config and falls back to the in-terminal picker when it isn't installed.

### Runner output
- **Style:** RichLog in a `panel` border at `$foreground` 15% titled "Runner" (a quiet wash, not a solid green bar), `padding: 0 1`, wrapping to the panel's width, prompt line `➜ (catnip): <file>` (prompt in the heading color, file name bold foreground), output, then one status line: `✓ finished in 0.4s` (`$text-success`) or `✗ exited with code 2 after 0.4s` / `✗ <reason>` / `✗ Stopped.` (`$text-error`). Before anything runs, a muted italic hint says how to start. Runs in a worker with a 60s limit; the border subtitle says what is running and that F6 stops it.
- **Where it runs:** a saved Python or JavaScript file with no unsaved changes runs in place; anything else runs from a copy under `~/.catnip/tmp/<doc>/<real file name>`, with the document's own folder as the working directory (and on `PYTHONPATH`), and the copy's path is replaced with the real one in the output.

## Do's and Don'ts

### Do:
- **Do** route every color through a theme variable and verify new chrome under at least one non-catnip theme (the customizer makes this a one-keystroke check).
- **Do** keep controls soft-spoken, then certain: tint at rest (15%), solid on hover/focus, nothing in between.
- **Do** use relative widths (`%`, `1fr`, `auto`) so every screen reflows with the terminal; verify at 80×24 and a wide size.
- **Do** keep the cat voice in copy and the cat on the Cat Me pill — warmth lives in words, palette, and a few moments, not extra decoration.
- **Do** lead every binding with a plain Ctrl+letter or F-key; Ctrl+digit, Ctrl+Shift+letter, and Shift+Enter never reach apps in terminals without the kitty keyboard protocol, so they are only ever second aliases.
- **Do** cap prose content at a ~90-cell measure.

### Don't:
- **Don't** hardcode hex values in TCSS; hex belongs only in the theme definitions (core/theme.py).
- **Don't** add shadows, gradients, or figlet-style large type — depth is tonal, type is one size.
- **Don't** mix icon languages: no emoji, nerd-font glyphs, or `[X]` letter codes beside the one-cell glyph set.
- **Don't** reassign hue meanings (rose stays destructive; green stays current/primary; peach stays keys).
- **Don't** spend green on chrome at rest: scrollbars, tree guides, frames, and headings are neutral or bloom.
- **Don't** let any surface depend on a fixed terminal size or absolute column widths.
