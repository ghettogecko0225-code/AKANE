"""Look and feel for both apps.

A small palette plus helpers so the desktop and the phone share one visual
identity instead of drifting apart.
"""

DARK = {
    "bg": "#12141c",
    "panel": "#1c2030",
    "card": "#242a3d",
    "accent": "#e0533d",
    "accent_soft": "#3a2b2b",
    "text": "#f2f4fb",
    "text_dim": "#9aa3bd",
    "good": "#4caf7d",
    "bad": "#e2574c",
    "line": "#2e3550",
}

LIGHT = {
    "bg": "#f4f6fb",
    "panel": "#ffffff",
    "card": "#ffffff",
    "accent": "#d94f3d",
    "accent_soft": "#fdeae6",
    "text": "#1b1f2a",
    "text_dim": "#5d6580",
    "good": "#2f9e63",
    "bad": "#c9453a",
    "line": "#dfe3ee",
}

PALETTES = {"dark": DARK, "light": LIGHT}


def palette(name="dark"):
    return PALETTES.get(name, DARK)


def qt_stylesheet(theme="dark"):
    """Qt stylesheet for the desktop app."""
    c = palette(theme)
    return f"""
    QWidget {{ background: {c['bg']}; color: {c['text']}; }}
    QMainWindow {{ background: {c['bg']}; }}
    QListWidget {{
        background: {c['panel']};
        border: 1px solid {c['line']};
        border-radius: 8px;
        padding: 6px;
    }}
    QListWidget::item {{ padding: 7px; border-radius: 6px; }}
    QListWidget::item:selected {{ background: {c['accent_soft']}; color: {c['text']}; }}
    QPushButton {{
        background: {c['panel']};
        border: 1px solid {c['line']};
        border-radius: 8px;
        padding: 9px 14px;
    }}
    QPushButton:hover {{ border-color: {c['accent']}; }}
    QPushButton:pressed {{ background: {c['accent_soft']}; }}
    QPushButton:disabled {{ color: {c['text_dim']}; }}
    QTextEdit, QPlainTextEdit, QLineEdit, QComboBox, QSpinBox {{
        background: {c['panel']};
        border: 1px solid {c['line']};
        border-radius: 8px;
        padding: 6px;
        selection-background-color: {c['accent']};
    }}
    QTabWidget::pane {{ border: 1px solid {c['line']}; border-radius: 8px; }}
    QTabBar::tab {{
        background: {c['panel']};
        padding: 8px 14px;
        border: 1px solid {c['line']};
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }}
    QTabBar::tab:selected {{ background: {c['accent_soft']}; color: {c['text']}; }}
    QLabel {{ color: {c['text']}; }}
    QProgressBar {{
        border: 1px solid {c['line']};
        border-radius: 6px;
        background: {c['panel']};
        text-align: center;
    }}
    QProgressBar::chunk {{ background: {c['accent']}; border-radius: 5px; }}
    """
