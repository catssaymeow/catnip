from rich.style import Style
from textual.theme import BUILTIN_THEMES, Theme
from textual.widgets import TextArea
from textual.widgets.text_area import TextAreaTheme

APP_THEMES = sorted(
    [("Catnip", "catnip")] + [(theme.replace("-", " ").title(), theme) for theme
                              in
                              BUILTIN_THEMES.keys()], key=lambda x: x[0])

# editor theme setting that follows whichever app theme is active
MATCH_APP_THEME = "match"

# available themes for the editor
EDITOR_THEMES = [("Match app theme", MATCH_APP_THEME)] + sorted(
    [("Catnip", "catnip")] + [(theme.replace("_", " ").title(), theme)
                              for theme in list(TextArea().available_themes)],
    key=lambda x: x[0])

# app themes that have an editor theme of the same name
_PAIRED_EDITOR_THEMES = {"catnip", "dracula", "monokai"}


def resolve_editor_theme(editor_theme: str, app_theme: str, dark: bool) -> str:
    """Return the TextArea theme to use, following the app theme when set to match."""

    if editor_theme != MATCH_APP_THEME:
        return editor_theme
    if app_theme in _PAIRED_EDITOR_THEMES:
        return app_theme
    return "vscode_dark" if dark else "github_light"

_CATNIP = Theme(
    name="catnip",
    primary="#a6e3a1",      # pastel green
    secondary="#94e2d5",    # pastel teal
    accent="#fab387",       # pastel orange
    foreground="#e2e6de",   # warm off-white
    background="#1e1e2e",   # deep soft dark
    success="#a6e3a1",      # pastel green
    warning="#f9e2af",      # pastel amber
    error="#f38ba8",        # pastel rose
    surface="#252532",      # raised surface
    panel="#313244",        # panel / sidebar
    dark=True,
    variables={
        "block-cursor-text-style": "none",
        # keys are peach everywhere they're written; green stays for "current"
        "footer-key-foreground": "#fab387",
        "input-selection-background": "#423f56",
        # headings bloom like the catnip flower
        "markdown-h1-color": "#c9b0f7",
        "markdown-h2-color": "#c9b0f7",
        "markdown-h3-color": "#c9b0f7",
    },
)

_CATNIP_EDITOR = TextAreaTheme(
    name="catnip",
    base_style=Style(color="#e2e6de", bgcolor="#1e1e2e"),
    gutter_style=Style(color="#a7b0a5", bgcolor="#252532"),
    cursor_style=Style(color="#1e1e2e", bgcolor="#a6e3a1"),
    cursor_line_style=Style(bgcolor="#252532"),
    bracket_matching_style=Style(bgcolor="#423f56", bold=True),
    cursor_line_gutter_style=Style(color="#e2e6de", bgcolor="#252532"),
    selection_style=Style(bgcolor="#423f56"),
    syntax_styles={
        "string": Style(color="#a6e3a1"),
        "string.documentation": Style(color="#a6e3a1"),
        "comment": Style(color="#a7b0a5"),
        "heading.marker": Style(color="#fab387"),
        "keyword": Style(color="#c9b0f7"),
        "keyword.self": Style(color="#c9b0f7"),
        "operator": Style(color="#94e2d5"),
        "conditional": Style(color="#c9b0f7"),
        "keyword.function": Style(color="#c9b0f7"),
        "keyword.return": Style(color="#94e2d5"),
        "keyword.operator": Style(color="#c9b0f7"),
        "repeat": Style(color="#c9b0f7"),
        "exception": Style(color="#c9b0f7"),
        "include": Style(color="#c9b0f7"),
        "number": Style(color="#fab387"),
        "float": Style(color="#fab387"),
        "class": Style(color="#c9b0f7"),
        "type": Style(color="#f9e2af"),
        "type.class": Style(color="#f9e2af"),
        "type.builtin": Style(color="#94e2d5"),
        "variable.builtin": Style(color="#e2e6de", italic=True),
        "function": Style(color="#94e2d5"),
        "function.call": Style(color="#94e2d5"),
        "method": Style(color="#94e2d5"),
        "method.call": Style(color="#94e2d5"),
        "constructor": Style(color="#f9e2af"),
        "boolean": Style(color="#94e2d5"),
        "constant.builtin": Style(color="#fab387"),
        "json.null": Style(color="#fab387"),
        "tag": Style(color="#fab387"),
        "yaml.field": Style(color="#a6e3a1", bold=True),
        "json.label": Style(color="#a6e3a1", bold=True),
        "toml.type": Style(color="#f9e2af"),
        "toml.datetime": Style(color="#c9b0f7", italic=True),
        "css.property": Style(color="#f9e2af"),
        "heading": Style(color="#c9b0f7", bold=True),
        "bold": Style(bold=True),
        "italic": Style(italic=True),
        "strikethrough": Style(strike=True),
        "link.uri": Style(color="#94e2d5", underline=True),
        "link.label": Style(color="#c9b0f7"),
        "list.marker": Style(color="#fab387"),
        "inline_code": Style(color="#fab387"),
        "info_string": Style(color="#fab387", bold=True, italic=True),
        "punctuation.bracket": Style(color="#e2e6de"),
        "punctuation.delimiter": Style(color="#e2e6de"),
        "punctuation.special": Style(color="#e2e6de"),
        "html.end_tag_error": Style(color="#f38ba8", bold=True, underline=True),
        "regex.operator": Style(color="#94e2d5", bold=True),
        "regex.punctuation.bracket": Style(color="#fab387"),
    },
)

CUSTOM_EDITOR_THEMES: list[TextAreaTheme] = [_CATNIP_EDITOR]
CUSTOM_APP_THEMES: list[Theme] = [_CATNIP]
