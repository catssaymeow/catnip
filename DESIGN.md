---
name: Catnip
description: A cozy, cat-themed terminal file browser and editor with a pastel garden palette on deep velvet dark.
colors:
  catnip-green: "#a6e3a1"
  seafoam-teal: "#94e2d5"
  peach-fuzz: "#fab387"
  butter-cream: "#f9e2af"
  rose-bud: "#f38ba8"
  lavender-sprig: "#cba6f7"
  moonlight-fur: "#e2e6de"
  whisker-gray: "#6c7086"
  shadow-nap: "#45475a"
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
  rail-button-rest:
    backgroundColor: "transparent"
    width: "4"
    height: "1"
  rail-button-focus:
    backgroundColor: "#a6e3a140"
    width: "4"
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

Catnip's interface is the spot a cat actually chooses: a warm, soft-lit place inside a disciplined structure. The structure is the terminal grid — deep velvet dark, exact cell alignment, keyboard-first economy. The warmth is pastel light falling onto it: catnip green, seafoam, peach, and butter tints that appear as washes and accents, never as floods. The result is cozy but never messy; every playful touch (emoji icons, "purr purr" copy, the Cat Me tab) sits on top of a quiet, precise frame.

This is a terminal application (Textual/TCSS). Every styled value is theme-driven: TCSS references semantic variables (`$primary`, `$warning`, `$error`, `$panel`, `$surface`, `$boost`), and the custom **catnip** theme defines the house palette those variables resolve to. Users can live-switch to any Textual theme from the customizer, so the layout and tint logic must read correctly under any palette — the catnip theme is the authoritative expression, not the only one.

**Key Characteristics:**
- Deep soft dark ground with pastel garden accents, each hue carrying one meaning.
- Tonal depth only: translucent washes (15/25/40%) and `$boost`, never shadows.
- Soft-spoken controls that commit fully on interaction (tinted at rest, solid on hover/focus).
- Emoji as the icon language; box-drawing `round` borders as the shape language.
- Everything flows with the terminal: fractional/percent widths, fluid at any size.

## Colors

A pastel garden at dusk: six soft hues glowing on three layered darks, with warm off-white text.

### Primary
- **Catnip Green** (#a6e3a1): the life color and the brand's voice — primary actions (Open Folder), focused rail icons, active-tab underline, footer key hints, user chat bubbles, cursor.

### Secondary
- **Seafoam Teal** (#94e2d5): supporting accent; operators, functions, and links in the editor. Used sparingly in chrome.
- **Lavender Sprig** (#cba6f7): keywords and headings in syntax highlighting; the scholarly accent of the editor pane.

### Tertiary
- **Peach Fuzz** (#fab387): the designated "accent" slot; numbers and list markers in the editor, moments of warmth.
- **Butter Cream** (#f9e2af): warning hue; the Open Files pill, types in syntax.
- **Rose Bud** (#f38ba8): error/destructive hue; the New File pill, errors, deletions.

### Neutral
- **Moonlight Fur** (#e2e6de): warm off-white foreground; all body text.
- **Whisker Gray** (#6c7086): muted text — editor gutter, comments, hidden files.
- **Shadow Nap** (#45475a): selection backgrounds and bracket matching.
- **Twilight Panel** (#313244): panel layer; side panel wash at 40% opacity.
- **Dusk Surface** (#252532): raised surface; the Screen background, cursor line, gutter.
- **Midnight Velvet** (#1e1e2e): deepest ground; editor background and text-on-accent color.

### Named Rules
**The Theme Variable Rule.** TCSS never hardcodes a hex value. All color flows through semantic theme variables (`$primary`, `$warning`, `$error`, `$panel`, `$surface`, `$boost`, `$background`) so the customizer's live theme switching restyles every screen. The catnip theme is where hex lives.

**The One Meaning Rule.** Each pastel keeps one job: green = primary/affirm, butter = caution/secondary action, rose = destructive, teal and lavender belong to the editor's syntax voice. Don't borrow a hue for a different meaning because it looks nice.

## Typography

**Display/Body/Mono Font:** the user's terminal monospace font. The app does not choose a family — it inherits whatever the terminal provides.

**Character:** one mono voice at one size; hierarchy is built entirely from weight, color, and space, never from font size.

### Hierarchy
- **Headings** (bold + accent color): section headers in Markdown content render bold lavender/purple; pill labels and key hints are bold.
- **Body** (regular, Moonlight Fur): everything else. Reading content (the Welcome tab) is capped at a 90-cell measure.
- **Muted** (Whisker Gray, italic where supported): dotfiles, gutter numbers, comments, de-emphasized metadata.

### Named Rules
**The One Size Rule.** The terminal has one glyph size. Emphasis comes from bold, color, and surrounding space. Never fake "large text" with figlet banners or doubled rows in app chrome.

## Layout

The shell is a fixed frame around a fluid center: a one-row top bar of pill buttons (padding `1 2 0 2`), a 4-cell emoji icon rail, a collapsible side panel, and a tabbed editor that takes the remaining width (`1fr`). The side panel steps through 0 / 25% / 50% / 100% widths; all widths are relative so the layout reflows live with the terminal. Main content carries `1 1 0 1` padding (`0 1` when the top bar is hidden). Spacing rhythm is the cell: 1 cell of padding inside things, 2 cells where groups separate. The footer is Textual's standard key-hint bar. Everything must remain usable at 80×24.

## Elevation & Depth

No shadows — a terminal has none. Depth is purely tonal: layers step from Midnight Velvet (deepest, editor) through Dusk Surface (screen) to Twilight Panel (raised), and translucent washes signal interactivity — 15% hue tint for a resting pill, 25% for focus, 40% for the side panel's wash, `$boost` for hover on transparent controls. Scrollbars are slim (1 cell) and theme-tinted.

**The Wash Rule.** Depth and state are expressed as translucent color washes over the dark ground, never as borders-everywhere or bright fills at rest.

## Shapes

The form language is the terminal cell. Buttons are borderless one-row pills whose shape is pure background color. Containers that need an outline use box-drawing borders: `round` (rounded corners) for conversational/soft elements like chat bubbles, `panel` for utility panes like the runner output. No other border styles; no heavy double-line frames.

## Components

Component philosophy: **soft-spoken, then certain** — controls rest as quiet tints and commit to a full solid fill the moment you engage them.

### Buttons (top-bar pills)
- **Shape:** borderless one-liner, `height: 1`, `padding: 0 2`, bold label.
- **Rest:** 15% tint of the button's hue as background, full hue as text (e.g. Open Folder: catnip green on #a6e3a126).
- **Hover / Focus:** flips solid — full hue background, Midnight Velvet text. No intermediate state.
- **Hue assignment:** green = Open Folder, butter = Open Files, rose = New File. New top-bar actions claim a hue by meaning, not decoration.

### Icon rail buttons
- **Style:** a single emoji glyph on transparent, `width: 4`, one row, 1-cell bottom margin.
- **Hover:** `$boost` wash. **Focus:** 25% primary tint, no text-style change.
- **Icons:** emoji only (📦 🎨 🚀 🍀 🐱) — this is the icon system; do not introduce drawn/SVG icon sets.

### Tabs
- **Style:** Textual's TabbedContent defaults under the active theme: plain label, primary-colored underline for the active tab. Tabs are titled in plain words ("Welcome", "Cat Me", file names).

### Side panel
- **Style:** 40% Twilight Panel wash over the surface, `padding: 0 1`, 25% width at rest, stepping 0/25/50/100%.
- **Scrollbars:** 1 cell, both axes, on any scrolling surface it hosts.

### Chat bubbles (Cat Me)
- **User:** catnip-green text in a `round` box-drawing border (primary-darken-2), `max-width: 70%`, left-aligned.
- **AI:** borderless, full-measure, 1 cell of top padding — the cat speaks plainly; the user's words get the bubble.

### Runner output
- **Style:** RichLog in a `panel` border of primary-darken-3, `padding: 1 2`, prompt line `➜ (catnip):`.

## Do's and Don'ts

### Do:
- **Do** route every color through a theme variable and verify new chrome under at least one non-catnip theme (the customizer makes this a one-keystroke check).
- **Do** keep controls soft-spoken, then certain: tint at rest (15%), solid on hover/focus, nothing in between.
- **Do** use relative widths (`%`, `1fr`, `auto`) so every screen reflows with the terminal; verify at 80×24 and a wide size.
- **Do** keep the cat voice in copy and emoji in iconography — warmth lives in words and glyphs, not extra decoration.
- **Do** cap prose content at a ~90-cell measure.

### Don't:
- **Don't** hardcode hex values in TCSS; hex belongs only in the theme definitions (core/theme.py).
- **Don't** add shadows, gradients, or figlet-style large type — depth is tonal, type is one size.
- **Don't** mix icon languages: no nerd-font glyphs or ASCII-art icons beside the emoji set.
- **Don't** reassign hue meanings (rose stays destructive; green stays primary/affirm).
- **Don't** let any surface depend on a fixed terminal size or absolute column widths.
