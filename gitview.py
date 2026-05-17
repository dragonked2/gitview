#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════╗
║                         GitView  v3.0                                   ║
║              Your Friendly GitHub Repository Explorer                   ║
║                                                                         ║
║  Author  : Ali Essam                                                    ║
║  Origin  : Egypt 🇪🇬                                                    ║
║  LinkedIn: linkedin.com/in/dragonked2                                   ║
║  GitHub  : github.com/dragonked2/gitview                                ║
║  License : MIT                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  What's NEW in v3.0 (vs v2.0)                                           ║
║  ─────────────────────────────                                           ║
║  ✓ Browse ANY public GitHub profile without a token (username / URL)    ║
║  ✓ Search is now USER-SCOPED — searches within the loaded user only     ║
║  ✓ Smart input parser — accepts github.com/user links OR bare usernames ║
║  ✓ Welcome / onboarding panel for first-time users                      ║
║  ✓ User-friendly error messages with step-by-step solutions             ║
║  ✓ "Quick Browse" mode: paste any GitHub URL and Go                     ║
║  ✓ Repo pinning — pin your favourite repos to the top                   ║
║  ✓ File search across ALL repos of the loaded user                      ║
║  ✓ Download-progress dialog with file counter and cancel support        ║
║  ✓ Auto-retry on transient network errors (3 retries, exponential back) ║
║  ✓ Config stores last username/mode so next launch is instant           ║
║  ✓ Auth-bar redesigned: Token tab | Browse-Public tab                   ║
║  ✓ All v2.0 features retained and polished                              ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

# ── Suppress noisy library warnings ───────────────────────────────────────
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=r".*urllib3.*",            category=UserWarning)
warnings.filterwarnings("ignore", message=r".*chardet.*",            category=UserWarning)
warnings.filterwarnings("ignore", message=r".*charset_normalizer.*", category=UserWarning)
warnings.filterwarnings("ignore", message=r".*doesn't match.*",      category=Warning)

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

import requests
try:
    import urllib3
    urllib3.disable_warnings()
except Exception:
    pass

import base64
import os
import json
import threading
import queue
from pathlib import Path
from datetime import datetime, timezone
import webbrowser
import time
import re
from collections import deque
from typing import Optional, Dict, List, Any, Tuple, Callable


# ══════════════════════════════════════════════════════════════════════════
#   DESIGN SYSTEM  — Dark & Light palettes
# ══════════════════════════════════════════════════════════════════════════
DARK: Dict[str, str] = {
    "bg":              "#080d13",
    "surface":         "#0d1117",
    "surface2":        "#161b22",
    "surface3":        "#1c2431",
    "border":          "#21262d",
    "border_bright":   "#30363d",
    "fg":              "#e6edf3",
    "fg_muted":        "#8b949e",
    "fg_subtle":       "#484f58",
    "accent":          "#2f81f7",
    "accent_hover":    "#58a6ff",
    "accent_subtle":   "#0d1f3c",
    "accent_glow":     "#163359",
    "success":         "#3fb950",
    "success_subtle":  "#0a2213",
    "warning":         "#d29922",
    "warning_subtle":  "#2a1f00",
    "danger":          "#f85149",
    "danger_subtle":   "#300a0a",
    "purple":          "#bc8cff",
    "cyan":            "#39c5cf",
    "orange":          "#f0883e",
    "pink":            "#ff7b72",
    "tree_select":     "#0d2645",
    "entry_bg":        "#0d1117",
    "tag_dir":         "#58a6ff",
    "tag_file":        "#e6edf3",
    "title_bar":       "#06090e",
    "status_bar":      "#06090e",
    "scrollbar":       "#21262d",
    "scrollbar_hover": "#30363d",
    "rate_ok":         "#3fb950",
    "rate_warn":       "#d29922",
    "rate_low":        "#f85149",
    "badge_token":     "#1a7f37",
    "badge_public":    "#9a3412",
    # Syntax highlight
    "syn_kw":          "#ff7b72",
    "syn_str":         "#a5d6ff",
    "syn_cmt":         "#6e7681",
    "syn_num":         "#79c0ff",
    "syn_func":        "#d2a8ff",
    "syn_deco":        "#ffa657",
    "syn_builtin":     "#79c0ff",
}

LIGHT: Dict[str, str] = {
    "bg":              "#f6f8fa",
    "surface":         "#ffffff",
    "surface2":        "#f0f2f5",
    "surface3":        "#e8ecf0",
    "border":          "#d0d7de",
    "border_bright":   "#b0bac4",
    "fg":              "#1f2328",
    "fg_muted":        "#57606a",
    "fg_subtle":       "#9ea8b3",
    "accent":          "#0969da",
    "accent_hover":    "#0550ae",
    "accent_subtle":   "#e6f0fd",
    "accent_glow":     "#cce5ff",
    "success":         "#1a7f37",
    "success_subtle":  "#d1f8dc",
    "warning":         "#9a6700",
    "warning_subtle":  "#fff8c5",
    "danger":          "#cf222e",
    "danger_subtle":   "#ffebe9",
    "purple":          "#8250df",
    "cyan":            "#0969da",
    "orange":          "#bc4c00",
    "pink":            "#a40e26",
    "tree_select":     "#dbeafe",
    "entry_bg":        "#ffffff",
    "tag_dir":         "#0969da",
    "tag_file":        "#1f2328",
    "title_bar":       "#ffffff",
    "status_bar":      "#f6f8fa",
    "scrollbar":       "#d0d7de",
    "scrollbar_hover": "#b0bac4",
    "rate_ok":         "#1a7f37",
    "rate_warn":       "#9a6700",
    "rate_low":        "#cf222e",
    "badge_token":     "#1a7f37",
    "badge_public":    "#9a3412",
    "syn_kw":          "#cf222e",
    "syn_str":         "#0550ae",
    "syn_cmt":         "#6e7781",
    "syn_num":         "#0550ae",
    "syn_func":        "#8250df",
    "syn_deco":        "#bc4c00",
    "syn_builtin":     "#0969da",
}

FONT_UI    = "Segoe UI"
FONT_MONO  = "Consolas"
FONT_TITLE = "Segoe UI Semibold"

APP_VERSION   = "3.0.0"
AUTHOR_NAME   = "Ali Essam"
AUTHOR_FROM   = "Egypt 🇪🇬"
AUTHOR_LI     = "linkedin.com/in/dragonked2"
AUTHOR_LI_URL = "https://www.linkedin.com/in/dragonked2"
GITHUB_URL    = "https://github.com/dragonked2/gitview"
CONFIG_FILE   = Path.home() / ".gitview_config.json"


# ══════════════════════════════════════════════════════════════════════════
#   HELPERS
# ══════════════════════════════════════════════════════════════════════════
def fmt_size(b: int) -> str:
    if b < 1024:          return f"{b} B"
    if b < 1_048_576:     return f"{b/1024:.1f} KB"
    if b < 1_073_741_824: return f"{b/1_048_576:.1f} MB"
    return f"{b/1_073_741_824:.1f} GB"


def relative_time(iso: str) -> str:
    if not iso:
        return ""
    try:
        dt  = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        s   = int((now - dt).total_seconds())
        if s < 60:       return "just now"
        if s < 3600:     return f"{s//60}m ago"
        if s < 86400:    return f"{s//3600}h ago"
        if s < 604800:   return f"{s//86400}d ago"
        if s < 2592000:  return f"{s//604800}w ago"
        if s < 31536000: return f"{s//2592000}mo ago"
        return f"{s//31536000}y ago"
    except Exception:
        return iso[:10] if len(iso) >= 10 else iso


def parse_github_input(text: str) -> Optional[str]:
    """Return bare username from a GitHub URL or username string.
    Accepts:
      - dragonked2
      - github.com/dragonked2
      - https://github.com/dragonked2
      - https://github.com/dragonked2/some-repo  (returns dragonked2)
    Returns None if the input looks invalid.
    """
    text = text.strip().rstrip("/")
    if not text:
        return None
    # Strip scheme and host
    text = re.sub(r"^https?://", "", text)
    text = re.sub(r"^(www\.)?github\.com/?", "", text)
    # First path component = username
    parts = [p for p in text.split("/") if p]
    if not parts:
        return None
    username = parts[0]
    # Basic validation: GitHub usernames are alphanumeric + hyphens, 1-39 chars
    if re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,37}[a-zA-Z0-9])?$", username):
        return username
    return None


def file_icon(name: str) -> str:
    ext = name.lower().rsplit(".", 1)[-1] if "." in name else ""
    ICONS = {
        "py":"🐍","js":"🟨","ts":"🔷","jsx":"⚛️","tsx":"⚛️",
        "html":"🌐","css":"🎨","scss":"🎨","sass":"🎨",
        "json":"📋","yaml":"📋","yml":"📋","toml":"📋","ini":"📋",
        "md":"📝","txt":"📄","rst":"📝","log":"📄",
        "sh":"⚙️","bash":"⚙️","zsh":"⚙️","bat":"⚙️","ps1":"⚙️",
        "c":"🔵","cpp":"🔵","h":"🔵","hpp":"🔵",
        "go":"🐹","rs":"🦀","rb":"💎","php":"🐘",
        "java":"☕","kt":"🎯","swift":"🍎","cs":"🔷",
        "sql":"🗄️","db":"🗄️","sqlite":"🗄️",
        "png":"🖼️","jpg":"🖼️","jpeg":"🖼️","gif":"🖼️",
        "svg":"🖼️","ico":"🖼️","webp":"🖼️","bmp":"🖼️",
        "pdf":"📕","docx":"📘","xlsx":"📗","pptx":"📙",
        "zip":"📦","tar":"📦","gz":"📦","rar":"📦","7z":"📦",
        "mp4":"🎬","avi":"🎬","mkv":"🎬","mp3":"🎵","wav":"🎵",
        "lock":"🔒","env":"🔑","pem":"🔑","key":"🔑",
        "dockerfile":"🐳","gitignore":"🚫","editorconfig":"⚙️",
        "makefile":"🔨","cmake":"🔨","gradle":"🐘",
    }
    n = name.lower()
    for special in ("dockerfile",".gitignore",".env","makefile","readme",
                    "license","changelog","contributing"):
        if special in n:
            return ICONS.get(special.lstrip("."), "📄")
    return ICONS.get(ext, "📄")


def lang_from_name(name: str) -> str:
    ext = name.lower().rsplit(".", 1)[-1] if "." in name else ""
    return {
        "py":"python","pyw":"python",
        "js":"javascript","jsx":"javascript","mjs":"javascript",
        "ts":"javascript","tsx":"javascript",
        "json":"json","html":"html","htm":"html",
        "css":"css","scss":"css","sh":"bash","bash":"bash","zsh":"bash",
        "rb":"ruby","go":"go","rs":"rust","java":"java",
        "c":"c","h":"c","cpp":"c","hpp":"c","cs":"csharp",
        "php":"php","swift":"swift","kt":"kotlin","sql":"sql",
        "md":"markdown","yaml":"yaml","yml":"yaml","toml":"toml",
    }.get(ext, "text")


# ══════════════════════════════════════════════════════════════════════════
#   SYNTAX HIGHLIGHTER
# ══════════════════════════════════════════════════════════════════════════
class SyntaxHighlighter:
    PY_KW  = (r'\b(False|None|True|and|as|assert|async|await|break|class|continue|'
               r'def|del|elif|else|except|finally|for|from|global|if|import|in|is|'
               r'lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b')
    PY_BLT = (r'\b(abs|all|any|bin|bool|bytes|callable|chr|dict|dir|enumerate|eval|'
               r'exec|filter|float|format|frozenset|getattr|globals|hasattr|hash|help|'
               r'hex|id|input|int|isinstance|issubclass|iter|len|list|locals|map|max|'
               r'min|next|object|open|ord|pow|print|property|range|repr|reversed|'
               r'round|set|setattr|slice|sorted|staticmethod|str|sum|super|tuple|'
               r'type|vars|zip)\b')
    JS_KW  = (r'\b(async|await|break|case|catch|class|const|continue|debugger|'
               r'default|delete|do|else|export|extends|finally|for|from|function|if|'
               r'import|in|instanceof|let|new|null|of|return|static|super|switch|'
               r'this|throw|try|typeof|undefined|var|void|while|with|yield|'
               r'true|false)\b')
    SQL_KW = (r'\b(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|'
               r'OUTER|ON|AS|AND|OR|NOT|IN|EXISTS|LIKE|BETWEEN|ORDER|BY|GROUP|'
               r'HAVING|LIMIT|OFFSET|UNION|ALL|DISTINCT|CREATE|TABLE|DROP|ALTER|'
               r'INDEX|VIEW|TRIGGER|PROCEDURE|FUNCTION|DATABASE|SCHEMA|PRIMARY|KEY|'
               r'FOREIGN|REFERENCES|UNIQUE|NULL|DEFAULT|AUTO_INCREMENT|'
               r'CONSTRAINT|BEGIN|COMMIT|ROLLBACK|TRANSACTION)\b')

    PATTERNS: Dict[str, List[Tuple[str, str]]] = {
        "python": [
            ("syn_cmt",     r'#[^\n]*'),
            ("syn_str",     r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"[^"\n]*"|\'[^\'\n]*\')'),
            ("syn_deco",    r'@\w+'),
            ("syn_kw",      PY_KW),
            ("syn_builtin", PY_BLT),
            ("syn_num",     r'\b\d+(\.\d+)?\b'),
            ("syn_func",    r'\bdef\s+(\w+)'),
        ],
        "javascript": [
            ("syn_cmt",  r'//[^\n]*|/\*[\s\S]*?\*/'),
            ("syn_str",  r'(`[^`]*`|"[^"\n]*"|\'[^\'\n]*\')'),
            ("syn_kw",   JS_KW),
            ("syn_num",  r'\b\d+(\.\d+)?\b'),
            ("syn_func", r'\bfunction\s+(\w+)|\b(\w+)\s*=\s*(async\s*)?\('),
        ],
        "json": [
            ("syn_str", r'"[^"\\]*(\\.[^"\\]*)*"'),
            ("syn_kw",  r'\b(true|false|null)\b'),
            ("syn_num", r'-?\b\d+(\.\d+)?([eE][+-]?\d+)?\b'),
        ],
        "html": [
            ("syn_cmt",  r'<!--[\s\S]*?-->'),
            ("syn_str",  r'"[^"]*"|\'[^\']*\''),
            ("syn_kw",   r'</?[\w.-]+|>|/>'),
            ("syn_func", r'\s[\w-]+='),
        ],
        "css": [
            ("syn_cmt",  r'/\*[\s\S]*?\*/'),
            ("syn_str",  r'"[^"]*"|\'[^\']*\''),
            ("syn_kw",   r'[\w-]+\s*(?=:)'),
            ("syn_func", r'#[\w-]+|\.[\w-]+'),
            ("syn_num",  r'\b\d+(\.\d+)?(px|em|rem|%|vh|vw|pt|s|ms)?\b'),
        ],
        "bash": [
            ("syn_cmt",  r'#[^\n]*'),
            ("syn_str",  r'"[^"]*"|\'[^\']*\''),
            ("syn_kw",   r'\b(if|then|else|elif|fi|for|while|do|done|case|esac|'
                         r'function|return|echo|exit|export|source|local|readonly|'
                         r'shift|unset|trap|break|continue)\b'),
            ("syn_num",  r'\$[\w@#?$!*-]|\$\{[\w@#?$!*-]+\}'),
        ],
        "sql": [
            ("syn_cmt",  r'--[^\n]*|/\*[\s\S]*?\*/'),
            ("syn_str",  r"'[^']*'"),
            ("syn_kw",   SQL_KW),
            ("syn_num",  r'\b\d+(\.\d+)?\b'),
        ],
        "markdown": [
            ("syn_func", r'^#{1,6}\s.*$'),
            ("syn_str",  r'`[^`]+`'),
            ("syn_kw",   r'\*\*[^*]+\*\*|__[^_]+__'),
            ("syn_cmt",  r'\[[^\]]*\]\([^)]*\)'),
        ],
        "yaml": [
            ("syn_cmt",  r'#[^\n]*'),
            ("syn_str",  r'"[^"]*"|\'[^\']*\''),
            ("syn_kw",   r'^[\w-]+(?=\s*:)'),
            ("syn_num",  r'\b\d+(\.\d+)?\b'),
            ("syn_func", r':\s*(true|false|null|yes|no)\b'),
        ],
        "toml": [
            ("syn_cmt",  r'#[^\n]*'),
            ("syn_str",  r'"[^"]*"|\'[^\']*\''),
            ("syn_kw",   r'^\[[\w.]+\]'),
            ("syn_num",  r'\b\d+(\.\d+)?\b'),
        ],
    }
    for _lang in ("c","csharp","java","go","rust","ruby","swift","kotlin","php"):
        PATTERNS[_lang] = PATTERNS.get("javascript", [])

    @classmethod
    def apply(cls, widget: tk.Text, lang: str, C: Dict) -> None:
        patterns = cls.PATTERNS.get(lang, [])
        if not patterns:
            return
        tag_colours = {
            "syn_kw":      C.get("syn_kw",      "#ff7b72"),
            "syn_str":     C.get("syn_str",      "#a5d6ff"),
            "syn_cmt":     C.get("syn_cmt",      "#6e7681"),
            "syn_num":     C.get("syn_num",      "#79c0ff"),
            "syn_func":    C.get("syn_func",     "#d2a8ff"),
            "syn_deco":    C.get("syn_deco",     "#ffa657"),
            "syn_builtin": C.get("syn_builtin",  "#79c0ff"),
        }
        for tag, colour in tag_colours.items():
            widget.tag_configure(tag, foreground=colour)
        content = widget.get("1.0", tk.END)
        for tag, pattern in patterns:
            try:
                for m in re.finditer(pattern, content, re.MULTILINE):
                    s = f"1.0 + {m.start()} chars"
                    e = f"1.0 + {m.end()} chars"
                    try:
                        widget.tag_add(tag, s, e)
                    except tk.TclError:
                        pass
            except re.error:
                pass


# ══════════════════════════════════════════════════════════════════════════
#   TOOLTIP
# ══════════════════════════════════════════════════════════════════════════
class Tooltip:
    DELAY = 500

    def __init__(self, widget: tk.Widget, text: str):
        self.widget    = widget
        self.text      = text
        self.tip: Optional[tk.Toplevel] = None
        self._after_id: Optional[str]   = None
        widget.bind("<Enter>",   self._schedule, add="+")
        widget.bind("<Leave>",   self._cancel,   add="+")
        widget.bind("<Destroy>", self._cancel,   add="+")

    def _schedule(self, _=None):
        self._cancel()
        self._after_id = self.widget.after(self.DELAY, self._show)

    def _show(self):
        if not self.widget.winfo_exists():
            return
        x = self.widget.winfo_rootx() + 24
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        self.tip.wm_attributes("-topmost", True)
        tk.Label(self.tip, text=self.text,
                 bg="#1c2128", fg="#e6edf3",
                 font=(FONT_UI, 8), relief="solid", bd=1,
                 padx=10, pady=5).pack()

    def _cancel(self, _=None):
        if self._after_id:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        if self.tip:
            try:
                self.tip.destroy()
            except Exception:
                pass
            self.tip = None


# ══════════════════════════════════════════════════════════════════════════
#   BUTTON FACTORY
# ══════════════════════════════════════════════════════════════════════════
def make_btn(parent, text, cmd, style="default", C=None, **kw) -> tk.Button:
    if C is None:
        C = DARK
    styles = {
        "default": dict(bg=C["surface2"],  fg=C["fg"],
                        activebackground=C["border_bright"], activeforeground=C["fg"]),
        "accent":  dict(bg=C["accent"],    fg="#ffffff",
                        activebackground=C["accent_hover"], activeforeground="#ffffff"),
        "danger":  dict(bg=C["danger"],    fg="#ffffff",
                        activebackground="#ff6961",          activeforeground="#ffffff"),
        "success": dict(bg=C["success"],   fg="#ffffff",
                        activebackground="#56d364",          activeforeground="#ffffff"),
        "ghost":   dict(bg=C["surface"],   fg=C["fg_muted"],
                        activebackground=C["surface2"],      activeforeground=C["fg"]),
        "warning": dict(bg=C["warning"],   fg="#000000",
                        activebackground="#e3aa2a",          activeforeground="#000000"),
        "purple":  dict(bg=C["purple"],    fg="#ffffff",
                        activebackground="#d2a8ff",          activeforeground="#000000"),
    }
    s    = styles.get(style, styles["default"])
    font = kw.pop("font", (FONT_UI, 9))
    padx = kw.pop("padx", 12)
    pady = kw.pop("pady", 5)
    btn  = tk.Button(parent, text=text, command=cmd,
                     font=font, relief=tk.FLAT, cursor="hand2",
                     padx=padx, pady=pady, bd=0,
                     highlightthickness=0, **s, **kw)

    def on_enter(_): btn.config(bg=s["activebackground"])
    def on_leave(_): btn.config(bg=s["bg"])

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


# ══════════════════════════════════════════════════════════════════════════
#   NETWORK HELPER — retry wrapper
# ══════════════════════════════════════════════════════════════════════════
def resilient_get(session: requests.Session, url: str,
                  params=None, headers=None, timeout=15,
                  max_retries=3) -> requests.Response:
    """GET with exponential back-off on transient errors."""
    last_exc: Optional[Exception] = None
    for attempt in range(max_retries):
        try:
            r = session.get(url, params=params, headers=headers or {},
                            timeout=timeout)
            # Only retry on 5xx or 429 (rate limit)
            if r.status_code in (429, 500, 502, 503, 504) and attempt < max_retries - 1:
                wait = 2 ** attempt
                time.sleep(wait)
                continue
            return r
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            last_exc = e
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    raise last_exc or RuntimeError("Request failed")


# ══════════════════════════════════════════════════════════════════════════
#   MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════
class GitView:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("GitView v3 — GitHub Explorer for Everyone")
        self.root.geometry("1440x880")
        self.root.minsize(1100, 640)

        # HTTP session (connection pooling, auto-headers)
        self.session = requests.Session()
        self.session.headers.update({
            "Accept":     "application/vnd.github.v3+json",
            "User-Agent": f"GitView/{APP_VERSION}",
        })

        # ── Core state ───────────────────────────────────────────────
        self.api_base           = "https://api.github.com"
        self.token: Optional[str]      = None
        self.username: Optional[str]   = None
        self.auth_mode: str            = "token"    # "token" | "public"
        self.current_repo: Optional[str]      = None
        self.current_repo_full: Optional[str] = None
        self.current_path: str         = ""
        self.current_branch: str       = "main"
        self.repo_data: Dict[str, Any] = {}
        self.all_items: Dict[str, List]= {"dirs": [], "files": []}
        self.current_theme: str        = "dark"
        self.C: Dict[str, str]         = DARK
        self.pinned_repos: List[str]   = []

        # Sort state
        self.sort_col     = "name"
        self.sort_reverse = False

        # Rate-limit counters
        self.rate_remaining = 60        # unauthenticated default
        self.rate_limit     = 60
        self.rate_reset_ts  = 0.0

        # History
        self.recent_repos: deque = deque(maxlen=20)
        self.op_log: List[str]   = []

        # Search state
        self.search_thread: Optional[threading.Thread] = None
        self.search_cancel = threading.Event()
        self._user_search_index: List[Dict] = []   # flat list of all repo-file meta
        self._user_search_built = False

        # Misc
        self.show_tok    = False
        self._preview_windows: List[tk.Toplevel] = []

        # Build everything
        self._apply_styles()
        self._build_ui()
        self._add_keyboard_shortcuts()
        self._load_saved_config()

    # ══════════════════════════════════════════════════════════════════
    #   STYLE ENGINE
    # ══════════════════════════════════════════════════════════════════
    def _apply_styles(self):
        C = self.C
        s = ttk.Style()
        s.theme_use("clam")

        s.configure("Treeview",
                    background=C["surface"], foreground=C["fg"],
                    fieldbackground=C["surface"],
                    rowheight=32, font=(FONT_UI, 10),
                    borderwidth=0, relief="flat")
        s.configure("Treeview.Heading",
                    background=C["surface2"], foreground=C["fg_muted"],
                    font=(FONT_UI, 8, "bold"), relief="flat", padding=(10, 7))
        s.map("Treeview",
              background=[("selected", C["tree_select"])],
              foreground=[("selected", C["accent_hover"])])
        s.map("Treeview.Heading",
              background=[("active", C["border_bright"])])

        s.configure("TNotebook", background=C["bg"], borderwidth=0,
                    tabmargins=[0, 0, 0, 0])
        s.configure("TNotebook.Tab",
                    background=C["surface"], foreground=C["fg_muted"],
                    padding=[18, 8], font=(FONT_UI, 9, "bold"), borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", C["bg"])],
              foreground=[("selected", C["fg"])],
              expand=[("selected", [0, 0, 0, 0])])

        s.configure("TCombobox",
                    fieldbackground=C["surface2"], background=C["surface2"],
                    foreground=C["fg"], arrowcolor=C["fg_muted"],
                    selectbackground=C["tree_select"], selectforeground=C["fg"],
                    borderwidth=0, relief="flat", padding=(8, 6))
        s.map("TCombobox",
              fieldbackground=[("readonly", C["surface2"])],
              foreground=[("readonly", C["fg"])],
              arrowcolor=[("disabled", C["fg_subtle"])])

        s.configure("TScrollbar",
                    background=C["scrollbar"], troughcolor=C["surface"],
                    arrowcolor=C["fg_subtle"], relief="flat",
                    borderwidth=0, width=9)
        s.map("TScrollbar",
              background=[("active", C["scrollbar_hover"]),
                          ("pressed", C["accent"])])

        s.configure("Horizontal.TProgressbar",
                    troughcolor=C["surface2"], background=C["accent"],
                    borderwidth=0, thickness=4)
        s.configure("Success.Horizontal.TProgressbar",
                    troughcolor=C["surface2"], background=C["success"],
                    borderwidth=0, thickness=4)

        self.root.configure(bg=C["bg"])
        self.root.option_add("*TCombobox*Listbox.background",       C["surface2"])
        self.root.option_add("*TCombobox*Listbox.foreground",       C["fg"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", C["tree_select"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", C["accent_hover"])
        self.root.option_add("*TCombobox*Listbox.font", (FONT_UI, 10))

    # ══════════════════════════════════════════════════════════════════
    #   UI CONSTRUCTION
    # ══════════════════════════════════════════════════════════════════
    def _build_ui(self):
        C    = self.C
        wrap = tk.Frame(self.root, bg=C["bg"])
        wrap.pack(fill=tk.BOTH, expand=True)
        self._wrap = wrap

        self._build_titlebar(wrap)
        self._build_auth_bar(wrap)

        body = tk.Frame(wrap, bg=C["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 10))

        self.notebook = ttk.Notebook(body)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tabs
        self.browser_frame = tk.Frame(self.notebook, bg=C["bg"])
        self.notebook.add(self.browser_frame,  text="  📁  Explorer  ")

        self.search_frame = tk.Frame(self.notebook, bg=C["bg"])
        self.notebook.add(self.search_frame,   text="  🔍  Search User  ")

        self.commits_frame = tk.Frame(self.notebook, bg=C["bg"])
        self.notebook.add(self.commits_frame,  text="  🕐  Commits  ")

        self.ops_frame = tk.Frame(self.notebook, bg=C["bg"])
        self.notebook.add(self.ops_frame,      text="  ⚡  Operations  ")

        self.about_frame = tk.Frame(self.notebook, bg=C["bg"])
        self.notebook.add(self.about_frame,    text="  ℹ️  About  ")

        self._build_explorer_tab()
        self._build_search_tab()
        self._build_commits_tab()
        self._build_ops_tab()
        self._build_about_tab()
        self._build_statusbar(wrap)
        self._build_context_menu()

    # ── Title Bar ─────────────────────────────────────────────────
    def _build_titlebar(self, parent):
        C = self.C
        tk.Frame(parent, bg=C["accent"], height=3).pack(fill=tk.X)

        bar = tk.Frame(parent, bg=C["title_bar"], height=60)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        inner = tk.Frame(bar, bg=C["title_bar"])
        inner.pack(fill=tk.BOTH, expand=True, padx=18)

        # Logo & brand
        logo_f = tk.Frame(inner, bg=C["title_bar"])
        logo_f.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(logo_f, text="⬡", bg=C["title_bar"], fg=C["accent"],
                 font=(FONT_UI, 24)).pack(side=tk.LEFT, padx=(0, 8), pady=10)
        brand_f = tk.Frame(logo_f, bg=C["title_bar"])
        brand_f.pack(side=tk.LEFT, fill=tk.Y, pady=10)
        tk.Label(brand_f, text="GitView",
                 bg=C["title_bar"], fg=C["fg"],
                 font=(FONT_TITLE, 16, "bold")).pack(anchor=tk.W)
        tk.Label(brand_f, text=f"v{APP_VERSION}  ·  GitHub Explorer for Everyone",
                 bg=C["title_bar"], fg=C["fg_muted"],
                 font=(FONT_UI, 8)).pack(anchor=tk.W)

        # Right controls
        right = tk.Frame(inner, bg=C["title_bar"])
        right.pack(side=tk.RIGHT, fill=tk.Y, pady=12)
        make_btn(right, "❓  Help",    self._show_help,  style="ghost", C=C,
                 font=(FONT_UI, 9)).pack(side=tk.RIGHT, padx=(4, 0))
        self.theme_btn = make_btn(right,
                                  "🌙  Dark" if self.current_theme == "dark" else "☀️  Light",
                                  self._toggle_theme, style="ghost", C=C, font=(FONT_UI, 9))
        self.theme_btn.pack(side=tk.RIGHT, padx=(4, 0))
        make_btn(right, "🌐  GitHub",
                 lambda: webbrowser.open(GITHUB_URL),
                 style="ghost", C=C, font=(FONT_UI, 9)).pack(side=tk.RIGHT, padx=(4, 0))

        # Rate-limit badge
        rl_f = tk.Frame(inner, bg=C["title_bar"])
        rl_f.pack(side=tk.RIGHT, fill=tk.Y, pady=14, padx=12)
        self.rate_lbl = tk.Label(rl_f, text="API  ●  —/—",
                                 bg=C["title_bar"], fg=C["fg_subtle"],
                                 font=(FONT_UI, 8))
        self.rate_lbl.pack(side=tk.RIGHT)
        self.api_rate_lbl = tk.Label(inner, text="",
                                     bg=C["title_bar"], fg=C["fg_subtle"],
                                     font=(FONT_UI, 7, "bold"))
        self.api_rate_lbl.pack(side=tk.RIGHT, padx=4, pady=14)

    # ── Auth Bar ──────────────────────────────────────────────────
    def _build_auth_bar(self, parent):
        C = self.C

        bar = tk.Frame(parent, bg=C["surface"],
                       highlightbackground=C["border"], highlightthickness=1)
        bar.pack(fill=tk.X, padx=14, pady=(6, 0))

        inner = tk.Frame(bar, bg=C["surface"])
        inner.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        # ── LEFT: dual-mode input area ────────────────────────────
        left = tk.Frame(inner, bg=C["surface"])
        left.pack(side=tk.LEFT, fill=tk.Y)

        # Mode tabs (Token vs Public)
        mode_row = tk.Frame(left, bg=C["surface"])
        mode_row.pack(anchor=tk.W)

        self.auth_mode_var = tk.StringVar(value=self.auth_mode)

        self._tab_token_btn = make_btn(mode_row, "🔑  Use Token", self._switch_to_token,
                                       style="accent" if self.auth_mode == "token" else "ghost",
                                       C=C, font=(FONT_UI, 8), padx=10, pady=3)
        self._tab_token_btn.pack(side=tk.LEFT)

        self._tab_public_btn = make_btn(mode_row, "👤  Browse Public Profile",
                                        self._switch_to_public,
                                        style="accent" if self.auth_mode == "public" else "ghost",
                                        C=C, font=(FONT_UI, 8), padx=10, pady=3)
        self._tab_public_btn.pack(side=tk.LEFT, padx=(4, 0))

        # Token mode frame
        self._token_frame = tk.Frame(left, bg=C["surface"])
        self._token_frame.pack(fill=tk.X, pady=(6, 0))

        tk.Label(self._token_frame, text="GITHUB TOKEN",
                 bg=C["surface"], fg=C["fg_subtle"],
                 font=(FONT_UI, 7, "bold")).pack(anchor=tk.W, pady=(0, 3))

        tok_row = tk.Frame(self._token_frame, bg=C["surface"])
        tok_row.pack(fill=tk.X)

        self.token_var = tk.StringVar()
        self.token_entry = tk.Entry(tok_row, textvariable=self.token_var,
                                    show="•", relief=tk.FLAT,
                                    bg=C["entry_bg"], fg=C["fg"],
                                    insertbackground=C["fg"],
                                    font=(FONT_MONO, 10), width=40,
                                    highlightthickness=1,
                                    highlightbackground=C["border"],
                                    highlightcolor=C["accent"])
        self.token_entry.pack(side=tk.LEFT, ipady=6, padx=(0, 4))
        self.token_entry.bind("<Return>", lambda _: self._connect_token())

        self.eye_btn = make_btn(tok_row, "👁", self._toggle_token_vis,
                                style="ghost", C=C, font=(FONT_UI, 11),
                                padx=6, pady=4)
        self.eye_btn.pack(side=tk.LEFT, padx=(0, 4))
        Tooltip(self.eye_btn, "Show / hide token text")

        self.connect_btn = make_btn(tok_row, "  ⚡  Connect  ",
                                    self._connect_token, style="accent", C=C,
                                    font=(FONT_UI, 9, "bold"), padx=14, pady=6)
        self.connect_btn.pack(side=tk.LEFT)

        self.disconnect_btn = make_btn(tok_row, "✕  Disconnect",
                                       self._disconnect, style="danger", C=C,
                                       font=(FONT_UI, 9), pady=6)
        self.disconnect_btn.pack(side=tk.LEFT, padx=(4, 0))
        self.disconnect_btn.pack_forget()

        # Help link for token
        self.tok_help_lbl = tk.Label(self._token_frame,
                                     text="🆘  Don't have a token? Click here to get one free →",
                                     bg=C["surface"], fg=C["accent"],
                                     font=(FONT_UI, 8), cursor="hand2")
        self.tok_help_lbl.pack(anchor=tk.W, pady=(3, 0))
        self.tok_help_lbl.bind("<Button-1>",
                               lambda _: webbrowser.open(
                                   "https://github.com/settings/tokens/new"
                                   "?description=GitView&scopes=repo"))

        # Public mode frame
        self._public_frame = tk.Frame(left, bg=C["surface"])
        # (packed or hidden based on mode)

        tk.Label(self._public_frame,
                 text="GITHUB USERNAME  or  github.com/username  or  full profile URL",
                 bg=C["surface"], fg=C["fg_subtle"],
                 font=(FONT_UI, 7, "bold")).pack(anchor=tk.W, pady=(0, 3))

        pub_row = tk.Frame(self._public_frame, bg=C["surface"])
        pub_row.pack(fill=tk.X)

        self.public_var = tk.StringVar()
        self.public_entry = tk.Entry(pub_row, textvariable=self.public_var,
                                     relief=tk.FLAT,
                                     bg=C["entry_bg"], fg=C["fg"],
                                     insertbackground=C["fg"],
                                     font=(FONT_MONO, 11), width=40,
                                     highlightthickness=1,
                                     highlightbackground=C["border"],
                                     highlightcolor=C["accent"])
        self.public_entry.pack(side=tk.LEFT, ipady=6, padx=(0, 6))
        self.public_entry.bind("<Return>", lambda _: self._connect_public())

        # Quick-paste buttons
        paste_examples = [("torvalds", "torvalds"),
                          ("microsoft", "microsoft"),
                          ("google", "google")]
        for label, val in paste_examples:
            b = make_btn(pub_row, label,
                         lambda v=val: (self.public_var.set(v), self._connect_public()),
                         style="ghost", C=C, font=(FONT_UI, 8), padx=6, pady=6)
            b.pack(side=tk.LEFT, padx=2)
            Tooltip(b, f"Browse {val}'s public repositories")

        self.public_connect_btn = make_btn(pub_row, "  🚀  Browse  ",
                                           self._connect_public, style="success", C=C,
                                           font=(FONT_UI, 9, "bold"), padx=14, pady=6)
        self.public_connect_btn.pack(side=tk.LEFT, padx=(6, 0))

        tk.Label(self._public_frame,
                 text="📌  Public repos only — read access, no upload/delete  ·  60 API calls/hr (unauthenticated)",
                 bg=C["surface"], fg=C["warning"],
                 font=(FONT_UI, 7)).pack(anchor=tk.W, pady=(3, 0))

        # Show correct frame
        if self.auth_mode == "token":
            self._token_frame.pack(fill=tk.X, pady=(6, 0))
        else:
            self._public_frame.pack(fill=tk.X, pady=(6, 0))

        # ── RIGHT: user card ──────────────────────────────────────
        right_area = tk.Frame(inner, bg=C["surface"])
        right_area.pack(side=tk.RIGHT, fill=tk.Y, padx=8)

        self.avatar_lbl = tk.Label(right_area, text="○",
                                   bg=C["surface"], fg=C["fg_subtle"],
                                   font=(FONT_UI, 28))
        self.avatar_lbl.pack(side=tk.LEFT, padx=(0, 10))

        user_col = tk.Frame(right_area, bg=C["surface"])
        user_col.pack(side=tk.LEFT, fill=tk.Y, pady=4)

        self.user_name_lbl = tk.Label(user_col, text="Not Connected",
                                      bg=C["surface"], fg=C["fg_muted"],
                                      font=(FONT_UI, 11, "bold"))
        self.user_name_lbl.pack(anchor=tk.W)
        self.user_meta_lbl = tk.Label(user_col,
                                      text="Choose a method above and connect",
                                      bg=C["surface"], fg=C["fg_subtle"],
                                      font=(FONT_UI, 8))
        self.user_meta_lbl.pack(anchor=tk.W)
        self.conn_badge = tk.Label(user_col, text="",
                                   bg=C["surface"], fg=C["fg_subtle"],
                                   font=(FONT_UI, 8))
        self.conn_badge.pack(anchor=tk.W)
        self.auth_badge = tk.Label(user_col, text="",
                                   bg=C["surface"], fg=C["fg_subtle"],
                                   font=(FONT_UI, 7, "bold"))
        self.auth_badge.pack(anchor=tk.W, pady=(2, 0))

        # Repo meta strip (far right)
        meta_area = tk.Frame(inner, bg=C["surface"])
        meta_area.pack(side=tk.RIGHT, fill=tk.Y, padx=12)
        self.repo_meta_lbl = tk.Label(meta_area, text="",
                                      bg=C["surface"], fg=C["fg_muted"],
                                      font=(FONT_UI, 8), justify=tk.RIGHT)
        self.repo_meta_lbl.pack(anchor=tk.E)
        self.repo_desc_lbl = tk.Label(meta_area, text="",
                                      bg=C["surface"], fg=C["fg_subtle"],
                                      font=(FONT_UI, 8), justify=tk.RIGHT,
                                      wraplength=300)
        self.repo_desc_lbl.pack(anchor=tk.E)

    # ── Mode switching ────────────────────────────────────────────
    def _switch_to_token(self):
        self.auth_mode = "token"
        C = self.C
        self._tab_token_btn.config(bg=C["accent"], fg="#ffffff",
                                   activebackground=C["accent_hover"])
        self._tab_public_btn.config(bg=C["surface"], fg=C["fg_muted"],
                                    activebackground=C["surface2"])
        self._public_frame.pack_forget()
        self._token_frame.pack(fill=tk.X, pady=(6, 0))

    def _switch_to_public(self):
        self.auth_mode = "public"
        C = self.C
        self._tab_public_btn.config(bg=C["accent"], fg="#ffffff",
                                    activebackground=C["accent_hover"])
        self._tab_token_btn.config(bg=C["surface"], fg=C["fg_muted"],
                                   activebackground=C["surface2"])
        self._token_frame.pack_forget()
        self._public_frame.pack(fill=tk.X, pady=(6, 0))

    # ══════════════════════════════════════════════════════════════════
    #   EXPLORER TAB
    # ══════════════════════════════════════════════════════════════════
    def _build_explorer_tab(self):
        C = self.C
        f = self.browser_frame

        # Toolbar
        toolbar = tk.Frame(f, bg=C["bg"])
        toolbar.pack(fill=tk.X, pady=(10, 6))

        tk.Label(toolbar, text="REPOSITORY",
                 bg=C["bg"], fg=C["fg_subtle"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=(0, 4))

        self.repo_var = tk.StringVar()
        self.repo_combo = ttk.Combobox(toolbar, textvariable=self.repo_var,
                                       width=44, state="readonly",
                                       font=(FONT_UI, 10))
        self.repo_combo.pack(side=tk.LEFT, padx=(0, 16), ipady=4)
        self.repo_combo.bind("<<ComboboxSelected>>", self._on_repo_select)

        tk.Label(toolbar, text="BRANCH",
                 bg=C["bg"], fg=C["fg_subtle"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=(0, 4))

        self.branch_var = tk.StringVar(value="main")
        self.branch_combo = ttk.Combobox(toolbar, textvariable=self.branch_var,
                                         width=18, font=(FONT_UI, 10))
        self.branch_combo.pack(side=tk.LEFT, padx=(0, 16), ipady=4)
        self.branch_combo.bind("<<ComboboxSelected>>", self._on_branch_change)

        # Right toolbar buttons
        for icon, label, cmd, style, tip in [
            ("🔄", "Refresh",      self._load_repos,          "ghost",   "Reload repository list  [F5]"),
            ("📌", "Pin Repo",     self._pin_current_repo,    "ghost",   "Pin this repo to the top of the list"),
            ("🌐", "Open in Web",  self._open_in_browser,     "ghost",   "Open current path on GitHub.com"),
            ("⭐", "Starred",      self._load_starred,        "ghost",   "Browse starred repositories"),
        ]:
            b = make_btn(toolbar, f"{icon}  {label}", cmd, style=style, C=C,
                         font=(FONT_UI, 9))
            b.pack(side=tk.RIGHT, padx=2)
            Tooltip(b, tip)

        # Navigation bar
        nav = tk.Frame(f, bg=C["surface"],
                       highlightbackground=C["border"], highlightthickness=1)
        nav.pack(fill=tk.X, pady=(0, 6))
        nav_inner = tk.Frame(nav, bg=C["surface"])
        nav_inner.pack(fill=tk.X, padx=8, pady=5)

        home_btn = make_btn(nav_inner, "⌂", self._go_home,
                            style="ghost", C=C, font=(FONT_UI, 13), padx=8, pady=3)
        home_btn.pack(side=tk.LEFT)
        Tooltip(home_btn, "Go to root  [Home]")

        up_btn = make_btn(nav_inner, "↑", self._go_up,
                          style="ghost", C=C, font=(FONT_UI, 13), padx=8, pady=3)
        up_btn.pack(side=tk.LEFT, padx=(2, 6))
        Tooltip(up_btn, "Go up one level  [Backspace]")

        tk.Frame(nav_inner, bg=C["border"], width=1).pack(
            side=tk.LEFT, fill=tk.Y, pady=2, padx=4)

        self.path_frame = tk.Frame(nav_inner, bg=C["surface"])
        self.path_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        self.path_lbl = tk.Label(self.path_frame, text="  /",
                                 bg=C["surface"], fg=C["accent"],
                                 font=(FONT_MONO, 10))
        self.path_lbl.pack(side=tk.LEFT)

        # Quick-filter box
        sf = tk.Frame(nav_inner, bg=C["surface2"],
                      highlightbackground=C["border"], highlightthickness=1)
        sf.pack(side=tk.RIGHT)
        tk.Label(sf, text="🔍", bg=C["surface2"], fg=C["fg_muted"],
                 font=(FONT_UI, 9)).pack(side=tk.LEFT, padx=(6, 0))
        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", lambda *_: self._filter_tree())
        filter_entry = tk.Entry(sf, textvariable=self.filter_var,
                                bg=C["surface2"], fg=C["fg"],
                                insertbackground=C["fg"], relief=tk.FLAT,
                                font=(FONT_UI, 10), width=22,
                                highlightthickness=0)
        filter_entry.pack(side=tk.LEFT, ipady=4, padx=(2, 0))
        self._filter_entry_ref = filter_entry
        clr = make_btn(sf, "✕", lambda: self.filter_var.set(""),
                       style="ghost", C=C, font=(FONT_UI, 9), padx=4, pady=2)
        clr.pack(side=tk.LEFT, padx=(0, 4))
        Tooltip(sf, "Filter files in this folder  [Ctrl+F]  — type to find instantly")

        # Content area
        content = tk.Frame(f, bg=C["bg"])
        content.pack(fill=tk.BOTH, expand=True)

        # File tree panel
        tree_panel = tk.Frame(content, bg=C["surface"],
                              highlightbackground=C["border"], highlightthickness=1)
        tree_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree_hdr = tk.Frame(tree_panel, bg=C["surface2"], height=36)
        tree_hdr.pack(fill=tk.X)
        tree_hdr.pack_propagate(False)
        tk.Label(tree_hdr, text="FILES & DIRECTORIES",
                 bg=C["surface2"], fg=C["fg_muted"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=12, pady=10)
        self.file_count_lbl = tk.Label(tree_hdr, text="",
                                       bg=C["surface2"], fg=C["fg_subtle"],
                                       font=(FONT_UI, 8))
        self.file_count_lbl.pack(side=tk.RIGHT, padx=12, pady=10)

        tree_wrap = tk.Frame(tree_panel, bg=C["surface"])
        tree_wrap.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_wrap,
                                 columns=("icon", "type", "size"),
                                 show="tree headings",
                                 selectmode="extended")
        self.tree.heading("#0",    text="  Name ▲", anchor=tk.W,
                          command=lambda: self._sort_by("name"))
        self.tree.heading("icon",  text="",          anchor=tk.CENTER)
        self.tree.heading("type",  text="Type",       anchor=tk.W,
                          command=lambda: self._sort_by("type"))
        self.tree.heading("size",  text="Size",       anchor=tk.E,
                          command=lambda: self._sort_by("size"))
        self.tree.column("#0",   width=320, minwidth=180, stretch=True)
        self.tree.column("icon", width=36,  minwidth=36,  stretch=False)
        self.tree.column("type", width=80,  minwidth=60,  stretch=False)
        self.tree.column("size", width=90,  minwidth=60,  stretch=False, anchor=tk.E)

        vsb = ttk.Scrollbar(tree_wrap,  orient=tk.VERTICAL,   command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_panel, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(fill=tk.X)

        self.tree.bind("<Double-1>",         self._on_tree_double_click)
        self.tree.bind("<Return>",           self._on_tree_double_click)
        self.tree.bind("<Button-3>",         self._show_ctx_menu)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # Sidebar
        sidebar = tk.Frame(content, bg=C["bg"], width=270)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        sidebar.pack_propagate(False)
        self._build_action_panel(sidebar)
        self._build_preview_panel(sidebar)

    def _build_action_panel(self, parent):
        C = self.C
        card = tk.Frame(parent, bg=C["surface"],
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill=tk.X, pady=(0, 10))

        hdr = tk.Frame(card, bg=C["surface2"], height=34)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="ACTIONS",
                 bg=C["surface2"], fg=C["fg_muted"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=12, pady=8)

        btn_grid = tk.Frame(card, bg=C["surface"])
        btn_grid.pack(fill=tk.X, padx=10, pady=10)

        def row(icon, label, cmd, style="default", tip=""):
            b = make_btn(btn_grid, f"{icon}  {label}", cmd, style=style, C=C,
                         font=(FONT_UI, 9), anchor=tk.W)
            b.pack(fill=tk.X, pady=2)
            if tip:
                Tooltip(b, tip)
            return b

        row("📥", "Download Selected",   self._download_selected,   "accent",   "Ctrl+D")
        row("📤", "Upload File",         self._upload_file,         "default",  "Ctrl+U")
        row("📁", "Upload Folder",       self._upload_folder,       "default")
        tk.Frame(btn_grid, bg=C["border"], height=1).pack(fill=tk.X, pady=5)
        row("👁",  "Preview File",       self._preview_selected,    "default",  "Space")
        row("✏️",  "Rename",             self._rename_selected,     "default",  "F2")
        row("📋", "Copy Path",           self._copy_path,           "default")
        tk.Frame(btn_grid, bg=C["border"], height=1).pack(fill=tk.X, pady=5)
        row("📝", "New File",            self._create_file_dialog,  "default",  "Ctrl+N")
        row("📂", "New Folder",          self._create_folder_dialog,"default")
        tk.Frame(btn_grid, bg=C["border"], height=1).pack(fill=tk.X, pady=5)
        row("🗑",  "Delete",             self._delete_selected,     "danger",   "Del")

    def _build_preview_panel(self, parent):
        C = self.C
        card = tk.Frame(parent, bg=C["surface"],
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        hdr = tk.Frame(card, bg=C["surface2"], height=34)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="FILE INFO",
                 bg=C["surface2"], fg=C["fg_muted"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=12, pady=8)

        self.info_frame = tk.Frame(card, bg=C["surface"])
        self.info_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.info_icon  = tk.Label(self.info_frame, text="",
                                   bg=C["surface"], fg=C["fg"], font=(FONT_UI, 28))
        self.info_icon.pack()
        self.info_name  = tk.Label(self.info_frame, text="Select a file to see info",
                                   bg=C["surface"], fg=C["fg_muted"],
                                   font=(FONT_UI, 10, "bold"), wraplength=230)
        self.info_name.pack(pady=(6, 0))
        self.info_meta  = tk.Label(self.info_frame, text="",
                                   bg=C["surface"], fg=C["fg_subtle"],
                                   font=(FONT_UI, 8), wraplength=230)
        self.info_meta.pack(pady=(2, 0))
        self.info_extra = tk.Label(self.info_frame, text="",
                                   bg=C["surface"], fg=C["fg_subtle"],
                                   font=(FONT_UI, 8), wraplength=230,
                                   justify=tk.CENTER)
        self.info_extra.pack(pady=(2, 0))

    # ══════════════════════════════════════════════════════════════════
    #   SEARCH TAB — USER-SCOPED
    # ══════════════════════════════════════════════════════════════════
    def _build_search_tab(self):
        C = self.C
        f = self.search_frame

        # ── Controls ──────────────────────────────────────────────
        ctrl = tk.Frame(f, bg=C["surface"],
                        highlightbackground=C["border"], highlightthickness=1)
        ctrl.pack(fill=tk.X, pady=(10, 6))

        inner = tk.Frame(ctrl, bg=C["surface"])
        inner.pack(fill=tk.X, padx=12, pady=10)

        # Search query
        tk.Label(inner, text="🔍  SEARCH WITHIN LOADED USER",
                 bg=C["surface"], fg=C["fg_subtle"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=(0, 8))

        self.usearch_var = tk.StringVar()
        usearch_entry = tk.Entry(inner, textvariable=self.usearch_var,
                                 relief=tk.FLAT,
                                 bg=C["entry_bg"], fg=C["fg"],
                                 insertbackground=C["fg"],
                                 font=(FONT_UI, 11), width=38,
                                 highlightthickness=1,
                                 highlightbackground=C["border"],
                                 highlightcolor=C["accent"])
        usearch_entry.pack(side=tk.LEFT, ipady=6, padx=(0, 8))
        usearch_entry.bind("<Return>", lambda _: self._do_user_search())

        # Scope selector
        tk.Label(inner, text="IN",
                 bg=C["surface"], fg=C["fg_subtle"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=(0, 6))

        self.usearch_scope_var = tk.StringVar(value="Repos")
        scopes = [
            ("Repos",     "Search repository names & descriptions"),
            ("Files",     "Search file names across repos"),
            ("Commits",   "Search commit messages"),
            ("Topics",    "Filter repos by language / topic"),
        ]
        for sc, tip in scopes:
            rb = tk.Radiobutton(inner, text=sc, variable=self.usearch_scope_var,
                                value=sc, bg=C["surface"], fg=C["fg"],
                                selectcolor=C["surface2"],
                                activebackground=C["surface"],
                                font=(FONT_UI, 9), cursor="hand2")
            rb.pack(side=tk.LEFT, padx=3)
            Tooltip(rb, tip)

        srch_btn = make_btn(inner, "  Search  ", self._do_user_search,
                            style="accent", C=C, font=(FONT_UI, 9, "bold"),
                            padx=14, pady=6)
        srch_btn.pack(side=tk.LEFT, padx=(8, 4))

        self.usearch_cancel_btn = make_btn(inner, "✕", self._cancel_user_search,
                                           style="danger", C=C,
                                           font=(FONT_UI, 9), pady=6, padx=8)
        self.usearch_cancel_btn.pack(side=tk.LEFT)
        self.usearch_cancel_btn.config(state=tk.DISABLED)

        self.usearch_count_lbl = tk.Label(inner, text="",
                                          bg=C["surface"], fg=C["fg_muted"],
                                          font=(FONT_UI, 9))
        self.usearch_count_lbl.pack(side=tk.RIGHT, padx=8)

        # Info banner
        self.usearch_banner = tk.Label(f,
            text="ℹ️   Connect to a GitHub user first, then search across all their repositories here.",
            bg=C["warning_subtle"], fg=C["warning"],
            font=(FONT_UI, 9), padx=12, pady=8, anchor=tk.W)
        self.usearch_banner.pack(fill=tk.X)

        # Results split
        results_area = tk.Frame(f, bg=C["bg"])
        results_area.pack(fill=tk.BOTH, expand=True)

        # Results list
        res_panel = tk.Frame(results_area, bg=C["surface"],
                             highlightbackground=C["border"], highlightthickness=1)
        res_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        res_hdr = tk.Frame(res_panel, bg=C["surface2"], height=34)
        res_hdr.pack(fill=tk.X)
        res_hdr.pack_propagate(False)
        tk.Label(res_hdr, text="RESULTS",
                 bg=C["surface2"], fg=C["fg_muted"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=12, pady=8)
        self.usearch_prog_lbl = tk.Label(res_hdr, text="",
                                         bg=C["surface2"], fg=C["accent"],
                                         font=(FONT_UI, 8))
        self.usearch_prog_lbl.pack(side=tk.RIGHT, padx=12, pady=8)

        res_wrap = tk.Frame(res_panel, bg=C["surface"])
        res_wrap.pack(fill=tk.BOTH, expand=True)

        self.uresults_tree = ttk.Treeview(res_wrap,
                                          columns=("detail", "meta", "when"),
                                          show="tree headings",
                                          selectmode="browse")
        self.uresults_tree.heading("#0",      text="  Name",   anchor=tk.W)
        self.uresults_tree.heading("detail",  text="Detail",   anchor=tk.W)
        self.uresults_tree.heading("meta",    text="Info",     anchor=tk.W)
        self.uresults_tree.heading("when",    text="Updated",  anchor=tk.W)
        self.uresults_tree.column("#0",     width=260, minwidth=120, stretch=True)
        self.uresults_tree.column("detail", width=240, minwidth=100, stretch=True)
        self.uresults_tree.column("meta",   width=140, minwidth=80,  stretch=False)
        self.uresults_tree.column("when",   width=100, minwidth=60,  stretch=False)

        rvsb = ttk.Scrollbar(res_wrap, orient=tk.VERTICAL,
                              command=self.uresults_tree.yview)
        self.uresults_tree.configure(yscrollcommand=rvsb.set)
        self.uresults_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rvsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.uresults_tree.bind("<<TreeviewSelect>>", self._on_usearch_select)
        self.uresults_tree.bind("<Double-1>",          self._on_usearch_open)

        # Detail pane
        det_panel = tk.Frame(results_area, bg=C["surface"],
                             highlightbackground=C["border"], highlightthickness=1,
                             width=320)
        det_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        det_panel.pack_propagate(False)

        det_hdr = tk.Frame(det_panel, bg=C["surface2"], height=34)
        det_hdr.pack(fill=tk.X)
        det_hdr.pack_propagate(False)
        tk.Label(det_hdr, text="DETAIL",
                 bg=C["surface2"], fg=C["fg_muted"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=12, pady=8)

        det_inner = tk.Frame(det_panel, bg=C["surface"])
        det_inner.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.udet_icon = tk.Label(det_inner, text="🔍",
                                  bg=C["surface"], fg=C["accent"],
                                  font=(FONT_UI, 30))
        self.udet_icon.pack()
        self.udet_name = tk.Label(det_inner, text="Run a search to see details",
                                  bg=C["surface"], fg=C["fg_muted"],
                                  font=(FONT_UI, 11, "bold"), wraplength=290)
        self.udet_name.pack(pady=(8, 0))
        self.udet_body = tk.Text(det_inner, wrap=tk.WORD, bg=C["surface"],
                                 fg=C["fg"], font=(FONT_MONO, 8),
                                 relief=tk.FLAT, highlightthickness=0,
                                 height=14, state=tk.DISABLED)
        self.udet_body.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        det_btns = tk.Frame(det_panel, bg=C["surface"])
        det_btns.pack(fill=tk.X, padx=12, pady=(0, 12))
        self.udet_open_btn = make_btn(det_btns, "🌐  Open on GitHub",
                                      lambda: None, style="accent", C=C,
                                      font=(FONT_UI, 9), pady=5)
        self.udet_open_btn.pack(fill=tk.X)
        self.udet_nav_btn = make_btn(det_btns, "📁  Navigate to in Explorer",
                                     lambda: None, style="ghost", C=C,
                                     font=(FONT_UI, 9), pady=5)
        self.udet_nav_btn.pack(fill=tk.X, pady=(4, 0))

        self._usearch_results_data: Dict[str, Any] = {}

    # ══════════════════════════════════════════════════════════════════
    #   COMMITS TAB
    # ══════════════════════════════════════════════════════════════════
    def _build_commits_tab(self):
        C = self.C
        f = self.commits_frame

        ctrl = tk.Frame(f, bg=C["surface"],
                        highlightbackground=C["border"], highlightthickness=1)
        ctrl.pack(fill=tk.X, pady=(10, 6))
        inner = tk.Frame(ctrl, bg=C["surface"])
        inner.pack(fill=tk.X, padx=12, pady=8)

        tk.Label(inner, text="AUTHOR FILTER",
                 bg=C["surface"], fg=C["fg_subtle"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.commit_author_var = tk.StringVar()
        tk.Entry(inner, textvariable=self.commit_author_var,
                 relief=tk.FLAT, bg=C["entry_bg"], fg=C["fg"],
                 insertbackground=C["fg"], font=(FONT_UI, 10),
                 width=18, highlightthickness=1,
                 highlightbackground=C["border"],
                 highlightcolor=C["accent"]).pack(side=tk.LEFT, ipady=5, padx=(0, 12))

        tk.Label(inner, text="PATH FILTER",
                 bg=C["surface"], fg=C["fg_subtle"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.commit_path_var = tk.StringVar()
        tk.Entry(inner, textvariable=self.commit_path_var,
                 relief=tk.FLAT, bg=C["entry_bg"], fg=C["fg"],
                 insertbackground=C["fg"], font=(FONT_UI, 10),
                 width=22, highlightthickness=1,
                 highlightbackground=C["border"],
                 highlightcolor=C["accent"]).pack(side=tk.LEFT, ipady=5, padx=(0, 12))

        self.commit_load_btn = make_btn(inner, "  🕐  Load Commits  ",
                                        self._load_commits, style="accent", C=C,
                                        font=(FONT_UI, 9, "bold"), pady=5)
        self.commit_load_btn.pack(side=tk.LEFT)
        self.commit_count_lbl = tk.Label(inner, text="",
                                         bg=C["surface"], fg=C["fg_muted"],
                                         font=(FONT_UI, 9))
        self.commit_count_lbl.pack(side=tk.RIGHT, padx=8)

        split = tk.Frame(f, bg=C["bg"])
        split.pack(fill=tk.BOTH, expand=True)

        # List
        com_panel = tk.Frame(split, bg=C["surface"],
                             highlightbackground=C["border"], highlightthickness=1)
        com_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        com_hdr = tk.Frame(com_panel, bg=C["surface2"], height=34)
        com_hdr.pack(fill=tk.X)
        com_hdr.pack_propagate(False)
        tk.Label(com_hdr, text="COMMIT HISTORY",
                 bg=C["surface2"], fg=C["fg_muted"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=12, pady=8)

        com_wrap = tk.Frame(com_panel, bg=C["surface"])
        com_wrap.pack(fill=tk.BOTH, expand=True)
        self.commits_tree = ttk.Treeview(com_wrap,
                                         columns=("sha", "author", "date"),
                                         show="tree headings",
                                         selectmode="browse")
        self.commits_tree.heading("#0",     text="  Message",  anchor=tk.W)
        self.commits_tree.heading("sha",    text="SHA",        anchor=tk.W)
        self.commits_tree.heading("author", text="Author",     anchor=tk.W)
        self.commits_tree.heading("date",   text="Date",       anchor=tk.W)
        self.commits_tree.column("#0",     width=380, minwidth=200, stretch=True)
        self.commits_tree.column("sha",    width=90,  minwidth=60,  stretch=False)
        self.commits_tree.column("author", width=140, minwidth=80,  stretch=False)
        self.commits_tree.column("date",   width=110, minwidth=80,  stretch=False)

        cvsb = ttk.Scrollbar(com_wrap, orient=tk.VERTICAL,
                              command=self.commits_tree.yview)
        self.commits_tree.configure(yscrollcommand=cvsb.set)
        self.commits_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cvsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.commits_tree.bind("<<TreeviewSelect>>", self._on_commit_select)
        self.commits_tree.bind("<Double-1>",          self._on_commit_open)

        # Detail
        cdp = tk.Frame(split, bg=C["surface"],
                       highlightbackground=C["border"], highlightthickness=1,
                       width=370)
        cdp.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        cdp.pack_propagate(False)

        cdp_hdr = tk.Frame(cdp, bg=C["surface2"], height=34)
        cdp_hdr.pack(fill=tk.X)
        cdp_hdr.pack_propagate(False)
        tk.Label(cdp_hdr, text="COMMIT DETAIL",
                 bg=C["surface2"], fg=C["fg_muted"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=12, pady=8)

        cdp_body = tk.Frame(cdp, bg=C["surface"])
        cdp_body.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        self.commit_msg_lbl  = tk.Label(cdp_body, text="Select a commit",
                                        bg=C["surface"], fg=C["fg_muted"],
                                        font=(FONT_UI, 10, "bold"),
                                        wraplength=330, justify=tk.LEFT)
        self.commit_msg_lbl.pack(anchor=tk.W)
        self.commit_meta_lbl = tk.Label(cdp_body, text="",
                                        bg=C["surface"], fg=C["fg_subtle"],
                                        font=(FONT_UI, 8), wraplength=330,
                                        justify=tk.LEFT)
        self.commit_meta_lbl.pack(anchor=tk.W, pady=(4, 8))
        tk.Frame(cdp_body, bg=C["border"], height=1).pack(fill=tk.X, pady=4)
        tk.Label(cdp_body, text="CHANGED FILES",
                 bg=C["surface"], fg=C["fg_subtle"],
                 font=(FONT_UI, 7, "bold")).pack(anchor=tk.W, pady=(4, 2))
        self.commit_files_box = tk.Text(cdp_body, wrap=tk.WORD,
                                        bg=C["surface2"], fg=C["fg"],
                                        font=(FONT_MONO, 8), relief=tk.FLAT,
                                        highlightthickness=1,
                                        highlightbackground=C["border"],
                                        height=8, state=tk.DISABLED)
        self.commit_files_box.pack(fill=tk.X)
        cdp_btns = tk.Frame(cdp, bg=C["surface"])
        cdp_btns.pack(fill=tk.X, padx=12, pady=(0, 12))
        self.commit_open_btn = make_btn(cdp_btns, "🌐  View on GitHub",
                                        lambda: None, style="accent", C=C,
                                        font=(FONT_UI, 9), pady=5)
        self.commit_open_btn.pack(fill=tk.X)
        self.commit_copy_sha = make_btn(cdp_btns, "📋  Copy SHA",
                                        lambda: None, style="ghost", C=C,
                                        font=(FONT_UI, 9), pady=5)
        self.commit_copy_sha.pack(fill=tk.X, pady=(4, 0))
        self._commits_data: Dict[str, Any] = {}

    # ══════════════════════════════════════════════════════════════════
    #   OPERATIONS TAB
    # ══════════════════════════════════════════════════════════════════
    def _build_ops_tab(self):
        C = self.C
        f = self.ops_frame

        outer = tk.Frame(f, bg=C["bg"])
        outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left = tk.Frame(outer, bg=C["bg"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self._ops_card(left, "📦  Bulk Download", [
            ("📦  Download Entire Repository", self._download_entire_repo,    "accent"),
            ("📁  Download Current Folder",    self._download_current_folder, "default"),
            ("📄  Download Selected Files",    self._download_selected,       "default"),
        ])
        self._ops_card(left, "📤  Upload & Create", [
            ("📤  Upload File",           self._upload_file,          "default"),
            ("📁  Upload Entire Folder",  self._upload_folder,        "default"),
            ("✏️   Create New File",       self._create_file_dialog,   "default"),
            ("📂  Create New Folder",     self._create_folder_dialog, "default"),
        ])

        right = tk.Frame(outer, bg=C["bg"], width=340)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)

        self._ops_card(right, "🔧  Repository", [
            ("➕  Create New Repository", self._create_repo_dialog, "accent"),
            ("🔄  Refresh Repositories",  self._load_repos,         "default"),
            ("🌐  Open in Browser",       self._open_in_browser,    "default"),
            ("🕐  Load Commit History",   self._load_commits_quick, "default"),
        ])

        # Progress card
        prog_card = tk.Frame(right, bg=C["surface"],
                             highlightbackground=C["border"], highlightthickness=1)
        prog_card.pack(fill=tk.X, pady=(0, 10))
        prog_hdr = tk.Frame(prog_card, bg=C["surface2"], height=34)
        prog_hdr.pack(fill=tk.X)
        prog_hdr.pack_propagate(False)
        tk.Label(prog_hdr, text="⚡  PROGRESS",
                 bg=C["surface2"], fg=C["fg_muted"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=12, pady=8)
        prog_inner = tk.Frame(prog_card, bg=C["surface"])
        prog_inner.pack(fill=tk.X, padx=12, pady=12)
        self.progress_var = tk.StringVar(value="No active operations")
        tk.Label(prog_inner, textvariable=self.progress_var,
                 bg=C["surface"], fg=C["fg_muted"],
                 font=(FONT_UI, 9), wraplength=300, justify=tk.LEFT).pack(anchor=tk.W)
        self.progress_bar = ttk.Progressbar(prog_inner, mode="indeterminate",
                                            length=300)
        self.progress_bar.pack(fill=tk.X, pady=(8, 0))
        self.progress_det = tk.Label(prog_inner, text="",
                                     bg=C["surface"], fg=C["accent"],
                                     font=(FONT_MONO, 8))
        self.progress_det.pack(anchor=tk.W, pady=(4, 0))

        # Operation log
        log_card = tk.Frame(right, bg=C["surface"],
                            highlightbackground=C["border"], highlightthickness=1)
        log_card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        log_hdr = tk.Frame(log_card, bg=C["surface2"], height=34)
        log_hdr.pack(fill=tk.X)
        log_hdr.pack_propagate(False)
        tk.Label(log_hdr, text="📋  OPERATION LOG",
                 bg=C["surface2"], fg=C["fg_muted"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=12, pady=8)
        make_btn(log_hdr, "Clear", self._clear_log,
                 style="ghost", C=C, font=(FONT_UI, 7),
                 pady=3, padx=6).pack(side=tk.RIGHT, padx=8, pady=6)
        self.log_text = tk.Text(log_card, wrap=tk.WORD,
                                bg=C["surface"], fg=C["fg_muted"],
                                font=(FONT_MONO, 8), relief=tk.FLAT,
                                highlightthickness=0, state=tk.DISABLED)
        log_sb = ttk.Scrollbar(log_card, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_sb.set)
        log_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

    def _ops_card(self, parent, title, actions):
        C = self.C
        card = tk.Frame(parent, bg=C["surface"],
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill=tk.X, pady=(0, 10))
        hdr = tk.Frame(card, bg=C["surface2"], height=34)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text=title, bg=C["surface2"], fg=C["fg_muted"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=12, pady=8)
        inner = tk.Frame(card, bg=C["surface"])
        inner.pack(fill=tk.X, padx=12, pady=10)
        for label, cmd, style in actions:
            make_btn(inner, label, cmd, style=style, C=C,
                     font=(FONT_UI, 9), anchor=tk.W).pack(fill=tk.X, pady=3)

    # ══════════════════════════════════════════════════════════════════
    #   ABOUT TAB
    # ══════════════════════════════════════════════════════════════════
    def _build_about_tab(self):
        C = self.C
        f = self.about_frame

        canvas_f = tk.Frame(f, bg=C["bg"])
        canvas_f.pack(fill=tk.BOTH, expand=True)

        center = tk.Frame(canvas_f, bg=C["bg"])
        center.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(center, text="⬡", bg=C["bg"], fg=C["accent"],
                 font=(FONT_UI, 72)).pack()
        tk.Label(center, text="GitView", bg=C["bg"], fg=C["fg"],
                 font=(FONT_TITLE, 38, "bold")).pack()
        tk.Label(center, text=f"Version {APP_VERSION}  ·  GitHub Explorer for Everyone",
                 bg=C["bg"], fg=C["fg_muted"], font=(FONT_UI, 11)).pack(pady=(4, 0))

        tk.Frame(center, bg=C["border"], height=1, width=520).pack(pady=22)

        info_grid = tk.Frame(center, bg=C["bg"])
        info_grid.pack()
        for i, (k, v) in enumerate([
            ("Author",    AUTHOR_NAME),
            ("Origin",    AUTHOR_FROM),
            ("LinkedIn",  AUTHOR_LI),
            ("License",   "MIT"),
            ("Repo",      GITHUB_URL),
        ]):
            tk.Label(info_grid, text=k, bg=C["bg"], fg=C["fg_subtle"],
                     font=(FONT_UI, 9, "bold"), width=10, anchor=tk.E
                     ).grid(row=i, column=0, padx=(0, 8), pady=3, sticky=tk.E)
            tk.Label(info_grid, text=v, bg=C["bg"], fg=C["fg"],
                     font=(FONT_UI, 9), anchor=tk.W
                     ).grid(row=i, column=1, pady=3, sticky=tk.W)

        tk.Frame(center, bg=C["border"], height=1, width=520).pack(pady=22)

        features = [
            ("v3.0 new", "👤 Browse Public Profiles  ·  🔍 User-Scoped Search  ·  🚀 No Token Required"),
            ("v2.0 new", "🕐 Commit History  ·  ✨ Syntax Highlighting  ·  ⌨️ Keyboard Shortcuts"),
            ("Fixed",    "⚠️ trace_add()  ·  urllib3 warnings  ·  requests.Session pooling"),
        ]
        for label, desc in features:
            row_f = tk.Frame(center, bg=C["bg"])
            row_f.pack(pady=3)
            tk.Label(row_f, text=label, bg=C["accent_subtle"], fg=C["accent"],
                     font=(FONT_UI, 8, "bold"), padx=8, pady=2).pack(side=tk.LEFT)
            tk.Label(row_f, text=f"  {desc}", bg=C["bg"], fg=C["fg_muted"],
                     font=(FONT_UI, 9)).pack(side=tk.LEFT, padx=8)

        btn_row = tk.Frame(center, bg=C["bg"])
        btn_row.pack(pady=22)
        make_btn(btn_row, "🔗  LinkedIn Profile",
                 lambda: webbrowser.open(AUTHOR_LI_URL),
                 style="accent", C=C, font=(FONT_UI, 10)).pack(side=tk.LEFT, padx=6)
        make_btn(btn_row, "⭐  Star on GitHub",
                 lambda: webbrowser.open(GITHUB_URL),
                 style="ghost", C=C, font=(FONT_UI, 10)).pack(side=tk.LEFT, padx=6)

    # ══════════════════════════════════════════════════════════════════
    #   STATUS BAR
    # ══════════════════════════════════════════════════════════════════
    def _build_statusbar(self, parent):
        C = self.C
        bar = tk.Frame(parent, bg=C["status_bar"],
                       highlightbackground=C["border"], highlightthickness=1,
                       height=28)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)
        inner = tk.Frame(bar, bg=C["status_bar"])
        inner.pack(fill=tk.BOTH, expand=True, padx=10)

        self.status_lbl = tk.Label(inner, text="Ready — Connect a GitHub account above to get started",
                                   bg=C["status_bar"], fg=C["fg_muted"],
                                   font=(FONT_UI, 8))
        self.status_lbl.pack(side=tk.LEFT, pady=4)

        right = tk.Frame(inner, bg=C["status_bar"])
        right.pack(side=tk.RIGHT)
        self.api_lbl = tk.Label(right, text="",
                                bg=C["status_bar"], fg=C["fg_subtle"],
                                font=(FONT_UI, 7, "bold"))
        self.api_lbl.pack(side=tk.RIGHT, padx=(12, 0), pady=4)

    # ══════════════════════════════════════════════════════════════════
    #   CONTEXT MENU
    # ══════════════════════════════════════════════════════════════════
    def _build_context_menu(self):
        C = self.C
        self.ctx = tk.Menu(self.root, tearoff=False,
                           bg=C["surface2"], fg=C["fg"],
                           activebackground=C["tree_select"],
                           activeforeground=C["accent_hover"],
                           font=(FONT_UI, 9), bd=0, relief=tk.FLAT)
        self.ctx.add_command(label="👁  Preview",          command=self._preview_selected)
        self.ctx.add_command(label="📥  Download",         command=self._download_selected)
        self.ctx.add_separator()
        self.ctx.add_command(label="✏️   Rename",           command=self._rename_selected)
        self.ctx.add_command(label="🗑  Delete",           command=self._delete_selected)
        self.ctx.add_separator()
        self.ctx.add_command(label="📋  Copy Path",        command=self._copy_path)
        self.ctx.add_command(label="🌐  Open in Browser", command=self._open_in_browser)

    def _show_ctx_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.ctx.post(event.x_root, event.y_root)

    # ══════════════════════════════════════════════════════════════════
    #   KEYBOARD SHORTCUTS
    # ══════════════════════════════════════════════════════════════════
    def _add_keyboard_shortcuts(self):
        r = self.root
        r.bind("<F5>",        lambda _: self._load_repos())
        r.bind("<F2>",        lambda _: self._rename_selected())
        r.bind("<Home>",      lambda _: self._go_home())
        r.bind("<BackSpace>", lambda _: self._go_up())
        r.bind("<Delete>",    lambda _: self._delete_selected())
        r.bind("<Control-f>", lambda _: self._focus_filter())
        r.bind("<Control-F>", lambda _: self._focus_filter())
        r.bind("<Control-d>", lambda _: self._download_selected())
        r.bind("<Control-D>", lambda _: self._download_selected())
        r.bind("<Control-u>", lambda _: self._upload_file())
        r.bind("<Control-U>", lambda _: self._upload_file())
        r.bind("<Control-n>", lambda _: self._create_file_dialog())
        r.bind("<Control-N>", lambda _: self._create_file_dialog())
        r.bind("<space>",     lambda _: self._preview_selected())

    def _focus_filter(self):
        self.notebook.select(0)
        try:
            self._filter_entry_ref.focus_set()
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════════════
    #   THEME TOGGLE
    # ══════════════════════════════════════════════════════════════════
    def _toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.C = LIGHT if self.current_theme == "light" else DARK
        self._apply_styles()
        for child in self.root.winfo_children():
            child.destroy()
        self._build_ui()
        self._add_keyboard_shortcuts()
        icon  = "☀️" if self.current_theme == "light" else "🌙"
        label = "Light" if self.current_theme == "light" else "Dark"
        try:
            self.theme_btn.config(text=f"{icon}  {label}")
        except Exception:
            pass
        if self.token or (self.username and self.auth_mode == "public"):
            self._restore_state_after_theme()

    def _restore_state_after_theme(self):
        if self.auth_mode == "token" and self.token:
            self.token_var.set(self.token)
        elif self.auth_mode == "public" and self.username:
            self.public_var.set(self.username)
            self._switch_to_public()
        if self.username:
            self._show_user_connected()
        if self.repo_data:
            names = self._build_repo_list_names()
            self.repo_combo["values"] = names
            if self.current_repo_full:
                self.repo_combo.set(self.current_repo_full)
                self._update_repo_meta()
        if self.current_repo:
            self._load_dir(self.current_path)
        self._update_rate_display()

    # ══════════════════════════════════════════════════════════════════
    #   AUTH — TOKEN MODE
    # ══════════════════════════════════════════════════════════════════
    def _toggle_token_vis(self):
        self.show_tok = not self.show_tok
        self.token_entry.config(show="" if self.show_tok else "•")
        self.eye_btn.config(text="🙈" if self.show_tok else "👁")

    def _connect_token(self):
        token = self.token_var.get().strip()
        if not token:
            messagebox.showerror(
                "GitView — No Token",
                "Please paste your GitHub Personal Access Token.\n\n"
                "To get one:\n"
                "  1. Go to github.com → Settings\n"
                "  2. Developer settings → Personal access tokens\n"
                "  3. Generate new token (Classic) with 'repo' scope\n"
                "  4. Copy and paste here\n\n"
                "Alternatively switch to 'Browse Public Profile' mode — no token needed!")
            return
        self.token = token
        self.auth_mode = "token"
        self.session.headers.update({"Authorization": f"token {token}"})
        self._set_status("Connecting to GitHub…")
        self.progress_bar.start()
        self.connect_btn.config(state=tk.DISABLED, text="Connecting…")
        self.rate_limit     = 5000
        self.rate_remaining = 5000

        def _work():
            try:
                r = resilient_get(self.session, f"{self.api_base}/user", timeout=12)
                self._parse_rate_limit(r)
                self.root.after(0, self.progress_bar.stop)
                if r.status_code == 200:
                    self.root.after(0, lambda: self._on_token_connected(r.json()))
                elif r.status_code == 401:
                    self.root.after(0, lambda: self._on_conn_fail(
                        "Invalid token.\n\nMake sure you copied it correctly — "
                        "it starts with 'ghp_' or 'github_pat_'."))
                else:
                    msg = r.json().get("message", "Unknown error")
                    self.root.after(0, lambda: self._on_conn_fail(msg))
            except Exception as e:
                self.root.after(0, self.progress_bar.stop)
                self.root.after(0, lambda: self._on_conn_fail(
                    f"Network error: {e}\n\nCheck your internet connection and try again."))

        threading.Thread(target=_work, daemon=True).start()

    def _on_token_connected(self, data: Dict):
        self.username = data["login"]
        self._show_user_connected(data, mode="token")
        self.connect_btn.config(state=tk.NORMAL, text="⟳  Reconnect")
        self.disconnect_btn.pack(side=tk.LEFT, padx=(4, 0))
        self._save_config()
        self._log_operation(f"[Token] Connected as {self.username}")
        self._load_repos()

    # ══════════════════════════════════════════════════════════════════
    #   AUTH — PUBLIC MODE (username / URL)
    # ══════════════════════════════════════════════════════════════════
    def _connect_public(self):
        raw = self.public_var.get().strip()
        if not raw:
            messagebox.showerror(
                "GitView — No Username",
                "Please type a GitHub username or paste a GitHub profile URL.\n\n"
                "Examples:\n"
                "  • torvalds\n"
                "  • https://github.com/torvalds\n"
                "  • github.com/microsoft")
            return
        username = parse_github_input(raw)
        if not username:
            messagebox.showerror(
                "GitView — Invalid Input",
                f"Could not find a valid GitHub username in:\n  {raw}\n\n"
                "Please enter just the username (e.g. 'torvalds') or a full GitHub URL.")
            return

        # Remove auth header for public browsing
        self.session.headers.pop("Authorization", None)
        self.token = None
        self.auth_mode = "public"
        self.rate_limit     = 60
        self.rate_remaining = 60

        self._set_status(f"Loading public profile: {username}…")
        self.progress_bar.start()
        self.public_connect_btn.config(state=tk.DISABLED, text="Loading…")

        def _work():
            try:
                r = resilient_get(self.session,
                                  f"{self.api_base}/users/{username}", timeout=12)
                self._parse_rate_limit(r)
                self.root.after(0, self.progress_bar.stop)
                if r.status_code == 200:
                    self.root.after(0, lambda: self._on_public_connected(r.json()))
                elif r.status_code == 404:
                    self.root.after(0, lambda: self._on_conn_fail(
                        f"User '{username}' not found on GitHub.\n\n"
                        "Double-check the spelling — GitHub usernames are case-insensitive."))
                elif r.status_code == 403:
                    self.root.after(0, lambda: self._on_conn_fail(
                        "GitHub API rate limit reached (60 req/hour for unauthenticated users).\n\n"
                        "To get 5,000 req/hour:\n"
                        "  • Switch to 'Use Token' mode and connect with your GitHub token."))
                else:
                    msg = r.json().get("message", "Unknown error")
                    self.root.after(0, lambda: self._on_conn_fail(msg))
            except Exception as e:
                self.root.after(0, self.progress_bar.stop)
                self.root.after(0, lambda: self._on_conn_fail(
                    f"Network error: {e}\n\nCheck your internet connection."))

        threading.Thread(target=_work, daemon=True).start()

    def _on_public_connected(self, data: Dict):
        self.username = data["login"]
        self._show_user_connected(data, mode="public")
        self.public_connect_btn.config(state=tk.NORMAL, text="  🚀  Browse  ")
        self._save_config()
        self._log_operation(f"[Public] Browsing {self.username}")
        self._load_repos()

    def _show_user_connected(self, data: Dict = None, mode: str = "token"):
        C = self.C
        if data is None:
            data = {}
        name    = data.get("name") or self.username or "Unknown"
        repos_n = data.get("public_repos", 0)
        follows = data.get("followers", 0)

        self.user_name_lbl.config(text=f"✓  {self.username}", fg=C["success"])
        self.user_meta_lbl.config(text=name, fg=C["fg_muted"])
        self.conn_badge.config(
            text=f"★ {repos_n} repos  ·  {follows:,} followers",
            fg=C["fg_subtle"])
        if mode == "token":
            badge_txt = "🔑  Authenticated — Full Access"
            badge_fg  = C["success"]
        else:
            badge_txt = "👁  Read-Only Public Access"
            badge_fg  = C["warning"]
        self.auth_badge.config(text=badge_txt, fg=badge_fg)
        self.avatar_lbl.config(text="◉", fg=C["success"])
        self._set_status(f"Connected: {self.username}  ({mode} mode)", "ok")
        self._update_rate_display()

    # ══════════════════════════════════════════════════════════════════
    #   DISCONNECT
    # ══════════════════════════════════════════════════════════════════
    def _disconnect(self):
        self.token    = None
        self.username = None
        self.current_repo      = None
        self.current_repo_full = None
        self.repo_data = {}
        self.session.headers.pop("Authorization", None)
        self.token_var.set("")
        self.repo_combo["values"] = []
        self.repo_var.set("")
        self.branch_combo["values"] = []
        self.branch_var.set("main")
        self.tree.delete(*self.tree.get_children())
        C = self.C
        self.user_name_lbl.config(text="Not Connected",                fg=C["fg_muted"])
        self.user_meta_lbl.config(text="Choose a method above and connect", fg=C["fg_subtle"])
        self.conn_badge.config(text="",   fg=C["fg_subtle"])
        self.auth_badge.config(text="",   fg=C["fg_subtle"])
        self.avatar_lbl.config(text="○",  fg=C["fg_subtle"])
        self.connect_btn.config(text="  ⚡  Connect  ")
        self.disconnect_btn.pack_forget()
        self.repo_meta_lbl.config(text="")
        self.repo_desc_lbl.config(text="")
        self.rate_remaining = 60
        self.rate_limit     = 60
        self._set_status("Disconnected — Connect again to continue")
        self._log_operation("Disconnected")
        self._save_config()

    # ══════════════════════════════════════════════════════════════════
    #   CONNECTION FAILURE
    # ══════════════════════════════════════════════════════════════════
    def _on_conn_fail(self, msg: str):
        try:
            self.connect_btn.config(state=tk.NORMAL, text="  ⚡  Connect  ")
            self.public_connect_btn.config(state=tk.NORMAL, text="  🚀  Browse  ")
        except Exception:
            pass
        self._set_status("Connection failed", "err")
        messagebox.showerror("GitView — Connection Error",
                             f"Could not connect to GitHub.\n\n{msg}")

    # ══════════════════════════════════════════════════════════════════
    #   CONFIG PERSISTENCE
    # ══════════════════════════════════════════════════════════════════
    def _save_config(self):
        try:
            cfg = {
                "version":      3,
                "token":        self.token or "",
                "last_username": self.username or "",
                "auth_mode":    self.auth_mode,
                "theme":        self.current_theme,
                "recent_repos": list(self.recent_repos),
                "pinned_repos": self.pinned_repos,
            }
            CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
        except Exception:
            pass

    def _load_saved_config(self):
        try:
            if not CONFIG_FILE.exists():
                return
            cfg = json.loads(CONFIG_FILE.read_text())
            # Theme
            saved_theme = cfg.get("theme", "dark")
            if saved_theme != self.current_theme:
                self.current_theme = saved_theme
                self.C = LIGHT if saved_theme == "light" else DARK
                self._apply_styles()
            # Recent/pinned
            for r in reversed(cfg.get("recent_repos", [])):
                self.recent_repos.appendleft(r)
            self.pinned_repos = cfg.get("pinned_repos", [])
            # Auto-connect
            mode = cfg.get("auth_mode", "token")
            if mode == "token" and cfg.get("token"):
                self.auth_mode = "token"
                self.token_var.set(cfg["token"])
                self.root.after(800, self._connect_token)
            elif mode == "public" and cfg.get("last_username"):
                self.auth_mode = "public"
                self.public_var.set(cfg["last_username"])
                self._switch_to_public()
                self.root.after(800, self._connect_public)
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════════════
    #   REPO MANAGEMENT
    # ══════════════════════════════════════════════════════════════════
    def _load_repos(self):
        if not self.username:
            messagebox.showwarning("GitView", "Please connect first.")
            return
        self._set_status("Loading repositories…")
        self.progress_bar.start()
        self.progress_var.set("Loading repository list…")
        self._user_search_built = False

        def _work():
            try:
                repos = []
                page  = 1
                # Authenticated → /user/repos  |  Public → /users/{name}/repos
                if self.auth_mode == "token" and self.token:
                    base_url = f"{self.api_base}/user/repos"
                else:
                    base_url = f"{self.api_base}/users/{self.username}/repos"

                while True:
                    r = resilient_get(self.session, base_url,
                                      params={"per_page": 100, "page": page,
                                              "sort": "updated"},
                                      timeout=15)
                    self._parse_rate_limit(r)
                    if r.status_code == 200:
                        batch = r.json()
                        if not batch:
                            break
                        repos.extend(batch)
                        page += 1
                    else:
                        break

                self.repo_data = {}
                for repo in repos:
                    owner = repo.get("owner", {}).get("login") or self.username
                    key   = f"{owner}/{repo['name']}"
                    self.repo_data[key] = repo

                names = self._build_repo_list_names()
                self.root.after(0, lambda: self._update_repo_list(names))
                self.root.after(0, self.progress_bar.stop)
                self.root.after(0, lambda: self.progress_var.set("No active operations"))
            except Exception as e:
                self.root.after(0, self.progress_bar.stop)
                self.root.after(0, lambda: self._set_status(f"Error loading repos: {e}", "err"))

        threading.Thread(target=_work, daemon=True).start()

    def _build_repo_list_names(self) -> List[str]:
        """Return sorted list of repo names with pinned repos on top."""
        all_names = sorted(self.repo_data.keys())
        pinned    = [n for n in self.pinned_repos if n in all_names]
        rest      = [n for n in all_names if n not in pinned]
        return pinned + rest

    def _update_repo_list(self, repos: List[str]):
        self.repo_combo["values"] = repos
        if repos:
            # Prefer recently used
            first = repos[0]
            for r in self.recent_repos:
                if r in repos:
                    first = r
                    break
            self.repo_combo.set(first)
            self._on_repo_select()
        self._set_status(f"Loaded {len(repos)} repositories", "ok")
        self.api_lbl.config(text=f"Repos: {len(repos)}")
        self._log_operation(f"Loaded {len(repos)} repositories for {self.username}")

    def _on_repo_select(self, _=None):
        sel = self.repo_var.get()
        if sel and "/" in sel:
            parts = sel.split("/", 1)
            self.username          = parts[0]
            self.current_repo      = parts[1]
            self.current_repo_full = sel
            self.current_path      = ""
            if sel in self.recent_repos:
                self.recent_repos.remove(sel)
            self.recent_repos.appendleft(sel)
            self._save_config()
            self._update_repo_meta()
            self._load_branches()
            self._load_dir("")

    def _update_repo_meta(self):
        if not self.current_repo_full:
            return
        rd = self.repo_data.get(self.current_repo_full, {})
        if not rd:
            return
        C     = self.C
        stars = rd.get("stargazers_count", 0)
        forks = rd.get("forks_count", 0)
        lang  = rd.get("language") or "—"
        priv  = "🔒 Private" if rd.get("private") else "🌐 Public"
        self.repo_meta_lbl.config(
            fg=C["fg_muted"],
            text=f"★ {stars:,}  🍴 {forks:,}  {lang}  ·  {priv}")
        desc = rd.get("description") or ""
        self.repo_desc_lbl.config(fg=C["fg_subtle"], text=desc[:120])

    def _pin_current_repo(self):
        if not self.current_repo_full:
            self._set_status("No repository selected", "warn")
            return
        repo = self.current_repo_full
        if repo in self.pinned_repos:
            self.pinned_repos.remove(repo)
            self._set_status(f"Unpinned {repo}", "info")
        else:
            self.pinned_repos.insert(0, repo)
            self._set_status(f"Pinned {repo} to top", "ok")
        # Refresh list
        names = self._build_repo_list_names()
        self.repo_combo["values"] = names
        self._save_config()

    def _load_starred(self):
        if not self.username:
            messagebox.showwarning("GitView", "Please connect first.")
            return
        self._set_status("Loading starred repos…")
        self.progress_bar.start()

        def _work():
            try:
                endpoint = (f"{self.api_base}/user/starred"
                            if self.auth_mode == "token" else
                            f"{self.api_base}/users/{self.username}/starred")
                r = resilient_get(self.session, endpoint,
                                  params={"per_page": 100}, timeout=12)
                self._parse_rate_limit(r)
                self.root.after(0, self.progress_bar.stop)
                if r.status_code == 200:
                    repos = [f"{i['owner']['login']}/{i['name']}" for i in r.json()]
                    self.root.after(0, lambda: self._show_starred_picker(repos))
                else:
                    self.root.after(0, lambda: self._set_status("Failed to load starred", "err"))
            except Exception as e:
                self.root.after(0, self.progress_bar.stop)
                self.root.after(0, lambda: self._set_status(str(e), "err"))

        threading.Thread(target=_work, daemon=True).start()

    def _show_starred_picker(self, repos: List[str]):
        C = self.C
        dlg = tk.Toplevel(self.root)
        dlg.title("GitView — Starred Repositories")
        dlg.geometry("420x520")
        dlg.configure(bg=C["bg"])
        dlg.resizable(True, True)

        tk.Label(dlg, text="⭐  Starred Repositories",
                 bg=C["bg"], fg=C["fg"],
                 font=(FONT_UI, 12, "bold")).pack(padx=16, pady=12, anchor=tk.W)

        lb_frame = tk.Frame(dlg, bg=C["surface"],
                            highlightbackground=C["border"], highlightthickness=1)
        lb_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))
        lb = tk.Listbox(lb_frame, bg=C["surface"], fg=C["fg"],
                        font=(FONT_MONO, 9), selectbackground=C["tree_select"],
                        selectforeground=C["accent_hover"],
                        relief=tk.FLAT, highlightthickness=0,
                        activestyle="none")
        sb = ttk.Scrollbar(lb_frame, command=lb.yview)
        lb.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        lb.pack(fill=tk.BOTH, expand=True)
        for r in repos:
            lb.insert(tk.END, f"  {r}")

        def _pick():
            if not lb.curselection():
                return
            chosen = repos[lb.curselection()[0]]
            dlg.destroy()
            if chosen not in self.repo_data:
                self.repo_data[chosen] = {"name": chosen.split("/")[-1], "private": False}
            vals = sorted(set(list(self.repo_combo["values"]) + [chosen]))
            self.repo_combo["values"] = vals
            self.repo_combo.set(chosen)
            self._on_repo_select()

        btn_f = tk.Frame(dlg, bg=C["bg"])
        btn_f.pack(fill=tk.X, padx=16, pady=(0, 12))
        make_btn(btn_f, "Open Repository", _pick, style="accent", C=C,
                 font=(FONT_UI, 10, "bold"), pady=7).pack(fill=tk.X)
        lb.bind("<Double-1>", lambda _: _pick())

    # ══════════════════════════════════════════════════════════════════
    #   BRANCHES
    # ══════════════════════════════════════════════════════════════════
    def _load_branches(self):
        if not self.current_repo:
            return

        def _work():
            try:
                r = resilient_get(
                    self.session,
                    f"{self.api_base}/repos/{self.username}/{self.current_repo}/branches",
                    timeout=10)
                self._parse_rate_limit(r)
                if r.status_code == 200:
                    branches = [b["name"] for b in r.json()]
                    self.root.after(0, lambda: self._update_branches(branches))
            except Exception:
                pass

        threading.Thread(target=_work, daemon=True).start()

    def _update_branches(self, branches: List[str]):
        self.branch_combo["values"] = branches
        if "main" in branches:
            self.branch_var.set("main")
        elif "master" in branches:
            self.branch_var.set("master")
        elif branches:
            self.branch_var.set(branches[0])
        self.current_branch = self.branch_var.get()

    def _on_branch_change(self, _=None):
        if self.current_repo:
            self.current_path = ""
            self._load_dir("")

    # ══════════════════════════════════════════════════════════════════
    #   DIRECTORY NAVIGATION
    # ══════════════════════════════════════════════════════════════════
    def _load_dir(self, path: str):
        if not self.current_repo:
            return
        self._set_status(f"Loading: {path or '/'}")
        self.progress_bar.start()

        def _work():
            try:
                branch = self.branch_var.get()
                url    = (f"{self.api_base}/repos/{self.username}/"
                          f"{self.current_repo}/contents/{path}")
                r = resilient_get(self.session, url,
                                  params={"ref": branch} if branch else {},
                                  timeout=15)
                self._parse_rate_limit(r)
                self.root.after(0, self.progress_bar.stop)
                if r.status_code == 200:
                    data  = r.json()
                    items = data if isinstance(data, list) else [data]
                    self.root.after(0, lambda: self._populate_tree(items, path))
                    self.root.after(0, lambda: self._set_status(
                        f"Loaded {len(items)} items in /{path or ''}", "ok"))
                elif r.status_code == 404:
                    self.root.after(0, lambda: self._set_status(
                        f"Path not found: {path}", "err"))
                elif r.status_code == 403:
                    self.root.after(0, lambda: self._set_status(
                        "Rate limit reached — try again in a minute or use a token", "err"))
                else:
                    msg = r.json().get("message", "Error loading directory")
                    self.root.after(0, lambda: self._set_status(msg, "err"))
            except Exception as e:
                self.root.after(0, self.progress_bar.stop)
                self.root.after(0, lambda: self._set_status(str(e), "err"))

        threading.Thread(target=_work, daemon=True).start()

    def _populate_tree(self, contents: List[Dict], path: str):
        self.tree.delete(*self.tree.get_children())
        dirs  = sorted([i for i in contents if i.get("type") == "dir"],
                       key=lambda x: x["name"].lower())
        files = sorted([i for i in contents if i.get("type") == "file"],
                       key=lambda x: x["name"].lower())
        self.all_items = {"dirs": dirs, "files": files}

        for item in dirs:
            self.tree.insert("", "end",
                             text=f"  {item['name']}",
                             values=("📁", "Folder", "—"),
                             tags=("dir",))
        for item in files:
            icon = file_icon(item["name"])
            size = fmt_size(item.get("size", 0))
            self.tree.insert("", "end",
                             text=f"  {item['name']}",
                             values=(icon, "File", size),
                             tags=("file",))

        self.tree.tag_configure("dir",  foreground=self.C["tag_dir"])
        self.tree.tag_configure("file", foreground=self.C["tag_file"])

        self.current_path = path
        self._update_path_display()
        self.file_count_lbl.config(
            text=f"{len(dirs)} folder{'s' if len(dirs)!=1 else ''}  ·  {len(files)} file{'s' if len(files)!=1 else ''}")
        self.sort_col     = "name"
        self.sort_reverse = False
        self.tree.heading("#0", text="  Name ▲")

    def _update_path_display(self):
        for w in self.path_frame.winfo_children():
            w.destroy()
        C     = self.C
        parts = (["root"] + [p for p in self.current_path.split("/") if p]
                 if self.current_path else ["root"])
        for i, part in enumerate(parts):
            is_last = (i == len(parts) - 1)
            display = f" {self.current_repo} " if part == "root" else f" {part} "
            lbl = tk.Label(self.path_frame, text=display,
                           bg=C["surface"],
                           fg=C["accent"] if not is_last else C["fg"],
                           font=(FONT_MONO, 10, "bold" if is_last else "normal"),
                           cursor="hand2" if not is_last else "")
            lbl.pack(side=tk.LEFT)
            if not is_last:
                nav_path = "" if i == 0 else "/".join(parts[1:i+1])
                def _go(_, p=nav_path):
                    self.current_path = p
                    self._load_dir(p)
                lbl.bind("<Button-1>", _go)
                tk.Label(self.path_frame, text=" / ",
                         bg=C["surface"], fg=C["fg_subtle"],
                         font=(FONT_MONO, 10)).pack(side=tk.LEFT)

    def _on_tree_double_click(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        item = sel[0]
        vals = self.tree.item(item, "values")
        name = self.tree.item(item, "text").strip()
        if vals[1] == "Folder":
            new_path = f"{self.current_path}/{name}" if self.current_path else name
            self.current_path = new_path
            self._load_dir(new_path)
        else:
            self._preview_selected()

    def _on_tree_select(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        item = sel[0]
        name = self.tree.item(item, "text").strip()
        vals = self.tree.item(item, "values")
        icon = vals[0] if vals else ""
        size = vals[2] if len(vals) > 2 else ""
        self.info_icon.config(text=icon, font=(FONT_UI, 32))
        self.info_name.config(text=name)
        is_dir = vals[1] == "Folder" if len(vals) > 1 else False
        self.info_meta.config(text="Directory" if is_dir else size)
        lang = lang_from_name(name) if not is_dir else ""
        self.info_extra.config(text=lang.capitalize() if lang and lang != "text" else "")

    def _go_home(self):
        self.current_path = ""
        self._load_dir("")

    def _go_up(self):
        if self.current_path:
            parts = self.current_path.rsplit("/", 1)
            self.current_path = parts[0] if len(parts) > 1 else ""
            self._load_dir(self.current_path)

    # ══════════════════════════════════════════════════════════════════
    #   SORT
    # ══════════════════════════════════════════════════════════════════
    def _sort_by(self, col: str):
        if self.sort_col == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_col     = col
            self.sort_reverse = False

        dirs  = list(self.all_items["dirs"])
        files = list(self.all_items["files"])

        def key(item):
            if col == "name": return item.get("name", "").lower()
            if col == "size": return item.get("size", 0)
            if col == "type": return item.get("type", "")
            return item.get("name", "").lower()

        dirs.sort( key=key, reverse=self.sort_reverse)
        files.sort(key=key, reverse=self.sort_reverse)

        arrow = "▲" if not self.sort_reverse else "▼"
        self.tree.heading("#0",   text=f"  Name {arrow}" if col == "name" else "  Name")
        self.tree.heading("type", text=f"Type {arrow}"   if col == "type" else "Type")
        self.tree.heading("size", text=f"Size {arrow}"   if col == "size" else "Size")

        self.tree.delete(*self.tree.get_children())
        for item in dirs:
            self.tree.insert("", "end", text=f"  {item['name']}",
                             values=("📁", "Folder", "—"), tags=("dir",))
        for item in files:
            self.tree.insert("", "end", text=f"  {item['name']}",
                             values=(file_icon(item["name"]), "File",
                                     fmt_size(item.get("size", 0))),
                             tags=("file",))
        self.tree.tag_configure("dir",  foreground=self.C["tag_dir"])
        self.tree.tag_configure("file", foreground=self.C["tag_file"])

    # ══════════════════════════════════════════════════════════════════
    #   FILTER (instant, local)
    # ══════════════════════════════════════════════════════════════════
    def _filter_tree(self):
        query = self.filter_var.get().strip().lower()
        if not query:
            self._populate_tree(
                self.all_items["dirs"] + self.all_items["files"],
                self.current_path)
            return
        filtered = ([d for d in self.all_items["dirs"]  if query in d["name"].lower()] +
                    [f for f in self.all_items["files"] if query in f["name"].lower()])
        self.tree.delete(*self.tree.get_children())
        for item in filtered:
            is_dir = item.get("type") == "dir"
            self.tree.insert("", "end",
                             text=f"  {item['name']}",
                             values=("📁" if is_dir else file_icon(item["name"]),
                                     "Folder" if is_dir else "File",
                                     "—" if is_dir else fmt_size(item.get("size", 0))),
                             tags=("dir" if is_dir else "file",))
        self.tree.tag_configure("dir",  foreground=self.C["tag_dir"])
        self.tree.tag_configure("file", foreground=self.C["tag_file"])
        self.file_count_lbl.config(text=f"Filter: {len(filtered)} match{'es' if len(filtered)!=1 else ''}")

    # ══════════════════════════════════════════════════════════════════
    #   USER-SCOPED SEARCH  (NEW in v3)
    # ══════════════════════════════════════════════════════════════════
    def _do_user_search(self):
        if not self.username:
            messagebox.showwarning(
                "GitView — Not Connected",
                "Please connect a GitHub account first.\n\n"
                "You can use either a token or browse a public profile.")
            return
        query = self.usearch_var.get().strip()
        if not query:
            self._set_status("Please enter a search term", "warn")
            return

        scope = self.usearch_scope_var.get()
        self.uresults_tree.delete(*self.uresults_tree.get_children())
        self._usearch_results_data.clear()
        self.usearch_count_lbl.config(text="Searching…")
        self.usearch_prog_lbl.config(text="● Searching…")
        self.usearch_cancel_btn.config(state=tk.NORMAL)
        self.search_cancel.clear()

        def _work():
            try:
                results = []
                if scope == "Repos":
                    results = self._search_user_repos(query)
                elif scope == "Files":
                    results = self._search_user_files(query)
                elif scope == "Commits":
                    results = self._search_user_commits(query)
                elif scope == "Topics":
                    results = self._search_user_topics(query)

                if not self.search_cancel.is_set():
                    self.root.after(0, lambda: self._display_user_search_results(results, scope))
            except Exception as e:
                if not self.search_cancel.is_set():
                    self.root.after(0, lambda: self._set_status(f"Search error: {e}", "err"))
                    self.root.after(0, lambda: self.usearch_prog_lbl.config(text=""))
            finally:
                self.root.after(0, lambda: self.usearch_cancel_btn.config(state=tk.DISABLED))

        self.search_thread = threading.Thread(target=_work, daemon=True)
        self.search_thread.start()

    def _search_user_repos(self, query: str) -> List[Dict]:
        """Search repo names and descriptions for the loaded user."""
        q_lower = query.lower()
        results = []
        for key, rd in self.repo_data.items():
            name = rd.get("name", "").lower()
            desc = (rd.get("description") or "").lower()
            topics = [t.lower() for t in rd.get("topics", [])]
            if (q_lower in name or q_lower in desc or
                    any(q_lower in t for t in topics)):
                results.append({"type": "repo", "key": key, "data": rd})
        return results

    def _search_user_files(self, query: str) -> List[Dict]:
        """Use GitHub code search scoped to user:username."""
        results = []
        q = f"{query} user:{self.username}"
        extra = {}
        if self.auth_mode == "token" and self.token:
            extra = {}
        try:
            r = resilient_get(self.session, f"{self.api_base}/search/code",
                              params={"q": q, "per_page": 50},
                              timeout=20)
            self._parse_rate_limit(r)
            if r.status_code == 200:
                items = r.json().get("items", [])
                for item in items:
                    results.append({"type": "file", "key": str(id(item)), "data": item})
            elif r.status_code == 403:
                results.append({"type": "error", "key": "err",
                                 "data": {"message": "File search requires authentication. "
                                          "Please use Token mode for file searching."}})
            elif r.status_code == 422:
                results.append({"type": "error", "key": "err422",
                                 "data": {"message": "Search term too short or invalid. "
                                          "Try a longer keyword."}})
        except Exception as e:
            results.append({"type": "error", "key": "errc", "data": {"message": str(e)}})
        return results

    def _search_user_commits(self, query: str) -> List[Dict]:
        """Search commit messages within user repos."""
        results = []
        q = f"{query} author:{self.username}"
        try:
            r = resilient_get(self.session, f"{self.api_base}/search/commits",
                              params={"q": q, "per_page": 30},
                              headers={"Accept": "application/vnd.github.cloak-preview+json"},
                              timeout=20)
            self._parse_rate_limit(r)
            if r.status_code == 200:
                items = r.json().get("items", [])
                for item in items:
                    results.append({"type": "commit", "key": str(id(item)), "data": item})
            elif r.status_code == 403:
                results.append({"type": "error", "key": "err",
                                 "data": {"message": "Commit search requires authentication."}})
        except Exception as e:
            results.append({"type": "error", "key": "errc", "data": {"message": str(e)}})
        return results

    def _search_user_topics(self, query: str) -> List[Dict]:
        """Filter repos by language or topic."""
        q_lower = query.lower()
        results = []
        for key, rd in self.repo_data.items():
            lang   = (rd.get("language") or "").lower()
            topics = [t.lower() for t in rd.get("topics", [])]
            if q_lower == lang or any(q_lower in t for t in topics):
                results.append({"type": "repo", "key": key, "data": rd})
        return results

    def _cancel_user_search(self):
        self.search_cancel.set()
        self.usearch_cancel_btn.config(state=tk.DISABLED)
        self.usearch_prog_lbl.config(text="")
        self._set_status("Search cancelled")

    def _display_user_search_results(self, results: List[Dict], scope: str):
        self.uresults_tree.delete(*self.uresults_tree.get_children())
        self._usearch_results_data.clear()
        self.usearch_prog_lbl.config(text="")
        count = len(results)
        self.usearch_count_lbl.config(text=f"{count} result{'s' if count!=1 else ''}")

        for entry in results:
            key   = entry["key"]
            etype = entry["type"]
            data  = entry["data"]

            if etype == "error":
                self.uresults_tree.insert("", "end", iid=key,
                                          text="  ⚠️  Search note",
                                          values=(data.get("message",""), "", ""))
                continue

            if etype == "repo":
                rd      = data
                name    = rd.get("name", "")
                lang    = rd.get("language") or "—"
                stars   = rd.get("stargazers_count", 0)
                updated = relative_time(rd.get("updated_at", ""))
                desc    = (rd.get("description") or "")[:80]
                icon    = "📦"
                self.uresults_tree.insert("", "end", iid=key,
                                          text=f"  {icon}  {name}",
                                          values=(desc, f"★{stars:,}  {lang}", updated))
            elif etype == "file":
                name    = data.get("name", "")
                path    = data.get("path", "")
                repo    = data.get("repository", {}).get("full_name", "")
                icon    = file_icon(name)
                self.uresults_tree.insert("", "end", iid=key,
                                          text=f"  {icon}  {name}",
                                          values=(path, repo, ""))
            elif etype == "commit":
                commit  = data.get("commit", {})
                msg     = (commit.get("message", "") or "")[:70]
                sha     = data.get("sha", "")[:10]
                repo    = data.get("repository", {}).get("full_name", "")
                date    = relative_time((commit.get("author") or {}).get("date", ""))
                self.uresults_tree.insert("", "end", iid=key,
                                          text=f"  🕐  {msg}",
                                          values=(sha, repo, date))

            self._usearch_results_data[key] = entry

        self._set_status(f"Found {count} result{'s' if count!=1 else ''} for '{self.usearch_var.get()}'",
                         "ok" if count else "warn")
        self._log_operation(f"Search [{scope}]: '{self.usearch_var.get()}' → {count} result(s)")
        if count == 0:
            self.uresults_tree.insert("", "end",
                                      text="  No results found — try a different keyword",
                                      values=("", "", ""))

    def _on_usearch_select(self, _=None):
        sel = self.uresults_tree.selection()
        if not sel:
            return
        iid   = sel[0]
        entry = self._usearch_results_data.get(iid)
        if not entry:
            return
        etype = entry["type"]
        data  = entry["data"]
        C     = self.C

        self.udet_body.config(state=tk.NORMAL)
        self.udet_body.delete("1.0", tk.END)

        if etype == "repo":
            rd   = data
            url  = rd.get("html_url", "")
            key  = entry["key"]
            self.udet_icon.config(text="📦")
            self.udet_name.config(text=rd.get("name", ""))
            self.udet_body.insert(tk.END,
                f"Owner:       {rd.get('owner',{}).get('login','')}\n"
                f"Stars:       {rd.get('stargazers_count',0):,}\n"
                f"Forks:       {rd.get('forks_count',0):,}\n"
                f"Language:    {rd.get('language') or '—'}\n"
                f"Open Issues: {rd.get('open_issues_count',0):,}\n"
                f"Private:     {'Yes' if rd.get('private') else 'No'}\n"
                f"Updated:     {relative_time(rd.get('updated_at',''))}\n\n"
                f"Description:\n{rd.get('description') or '—'}\n\n"
                f"URL: {url}\n")
            self.udet_open_btn.config(command=lambda u=url: webbrowser.open(u))
            def _nav_repo(k=key):
                if k in self.repo_data:
                    self.repo_combo.set(k)
                    self._on_repo_select()
                    self.notebook.select(0)
            self.udet_nav_btn.config(command=_nav_repo,
                                     text="📁  Navigate to this Repo")

        elif etype == "file":
            name = data.get("name", "")
            path = data.get("path", "")
            repo = data.get("repository", {}).get("full_name", "")
            url  = data.get("html_url", "")
            self.udet_icon.config(text=file_icon(name))
            self.udet_name.config(text=name)
            self.udet_body.insert(tk.END,
                f"Repository:  {repo}\n"
                f"Path:        {path}\n"
                f"URL:         {url}\n\n")
            for frag in data.get("text_matches", []):
                self.udet_body.insert(tk.END,
                    f"…{frag.get('fragment','')[:280]}…\n\n")
            self.udet_open_btn.config(command=lambda u=url: webbrowser.open(u))
            def _nav_file(r=repo, p=path):
                if r:
                    if r not in self.repo_data:
                        self.repo_data[r] = {"name": r.split("/")[-1], "private": False}
                    vals = sorted(set(list(self.repo_combo["values"]) + [r]))
                    self.repo_combo["values"] = vals
                    self.repo_combo.set(r)
                    self._on_repo_select()
                    dir_path = "/".join(p.split("/")[:-1]) if "/" in p else ""
                    self.root.after(900, lambda: self._load_dir(dir_path))
                    self.notebook.select(0)
            self.udet_nav_btn.config(command=_nav_file,
                                     text="📁  Navigate in Explorer")

        elif etype == "commit":
            commit = data.get("commit", {})
            msg    = commit.get("message", "")
            sha    = data.get("sha", "")
            url    = data.get("html_url", "")
            author = commit.get("author", {})
            self.udet_icon.config(text="🕐")
            self.udet_name.config(text=msg[:80])
            self.udet_body.insert(tk.END,
                f"SHA:      {sha[:12]}\n"
                f"Author:   {author.get('name','—')}\n"
                f"Email:    {author.get('email','—')}\n"
                f"Date:     {relative_time(author.get('date',''))}\n"
                f"Repo:     {data.get('repository',{}).get('full_name','')}\n\n"
                f"URL: {url}\n")
            self.udet_open_btn.config(command=lambda u=url: webbrowser.open(u))
            self.udet_nav_btn.config(command=lambda: None,
                                     text="📋  (navigate not available for commits)")

        self.udet_body.config(state=tk.DISABLED)

    def _on_usearch_open(self, _=None):
        sel = self.uresults_tree.selection()
        if not sel:
            return
        iid   = sel[0]
        entry = self._usearch_results_data.get(iid, {})
        url   = entry.get("data", {}).get("html_url", "")
        if url:
            webbrowser.open(url)

    # ══════════════════════════════════════════════════════════════════
    #   FILE PREVIEW
    # ══════════════════════════════════════════════════════════════════
    def _preview_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        item = sel[0]
        vals = self.tree.item(item, "values")
        if not vals or vals[1] == "Folder":
            return
        name     = self.tree.item(item, "text").strip()
        api_path = f"{self.current_path}/{name}" if self.current_path else name
        self._set_status(f"Loading preview: {name}…")

        def _work():
            try:
                branch = self.branch_var.get()
                r = resilient_get(
                    self.session,
                    f"{self.api_base}/repos/{self.username}/"
                    f"{self.current_repo}/contents/{api_path}",
                    params={"ref": branch} if branch else {},
                    timeout=15)
                self._parse_rate_limit(r)
                if r.status_code == 200:
                    data = r.json()
                    raw  = data.get("content", "")
                    try:
                        text = base64.b64decode(raw).decode("utf-8", errors="replace")
                    except Exception:
                        text = "[Binary file — cannot display as text]"
                    size = fmt_size(data.get("size", 0))
                    self.root.after(0, lambda: self._show_preview_window(
                        name, text, size, api_path))
                    self.root.after(0, lambda: self._set_status(f"Preview: {name}", "ok"))
                else:
                    self.root.after(0, lambda: self._set_status("Preview failed", "err"))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(str(e), "err"))

        threading.Thread(target=_work, daemon=True).start()

    def _show_preview_window(self, name: str, text: str, size: str, api_path: str):
        C    = self.C
        lang = lang_from_name(name)

        win = tk.Toplevel(self.root)
        win.title(f"GitView — {name}")
        win.geometry("1000x720")
        win.configure(bg=C["bg"])
        self._preview_windows.append(win)
        win.protocol("WM_DELETE_WINDOW",
                     lambda: (self._preview_windows.remove(win)
                              if win in self._preview_windows else None,
                              win.destroy()))

        # Header
        hdr = tk.Frame(win, bg=C["surface"], height=48)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        hdr_inner = tk.Frame(hdr, bg=C["surface"])
        hdr_inner.pack(fill=tk.BOTH, expand=True, padx=14)

        tk.Label(hdr_inner, text=f"{file_icon(name)}  {name}",
                 bg=C["surface"], fg=C["fg"],
                 font=(FONT_UI, 11, "bold")).pack(side=tk.LEFT, pady=8)
        tk.Label(hdr_inner, text=f"  ·  {size}  ·  {lang.capitalize()}  ·  {self.current_repo}",
                 bg=C["surface"], fg=C["fg_muted"],
                 font=(FONT_UI, 9)).pack(side=tk.LEFT, pady=8)

        for btn_text, btn_cmd, btn_style in [
            ("✕  Close",    win.destroy, "ghost"),
            ("📥  Download", lambda: self._download_single_file(name), "accent"),
            ("📋  Copy All", lambda: (win.clipboard_clear(),
                                      win.clipboard_append(text),
                                      self._set_status("Copied to clipboard", "ok")), "ghost"),
        ]:
            make_btn(hdr_inner, btn_text, btn_cmd, style=btn_style, C=C,
                     font=(FONT_UI, 9), pady=4).pack(side=tk.RIGHT, padx=3, pady=8)

        # Code view
        code_f = tk.Frame(win, bg=C["surface"])
        code_f.pack(fill=tk.BOTH, expand=True)

        line_count = text.count("\n") + 1
        ln = tk.Text(code_f, width=5, wrap=tk.NONE,
                     bg=C["surface2"], fg=C["fg_subtle"],
                     font=(FONT_MONO, 10), relief=tk.FLAT,
                     highlightthickness=0, state=tk.NORMAL,
                     selectbackground=C["surface2"])
        ln.insert("1.0", "\n".join(str(i) for i in range(1, line_count + 1)))
        ln.config(state=tk.DISABLED)
        ln.pack(side=tk.LEFT, fill=tk.Y)

        code = tk.Text(code_f, wrap=tk.NONE,
                       bg=C["surface"], fg=C["fg"],
                       font=(FONT_MONO, 10), relief=tk.FLAT,
                       highlightthickness=0,
                       selectbackground=C["tree_select"],
                       insertbackground=C["fg"])
        code.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(code_f, orient=tk.VERTICAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb = ttk.Scrollbar(win, orient=tk.HORIZONTAL, command=code.xview)
        hsb.pack(fill=tk.X)
        code.configure(xscrollcommand=hsb.set,
                       yscrollcommand=lambda *a: (vsb.set(*a), ln.yview_moveto(a[0])))
        vsb.configure(command=lambda *a: (code.yview(*a), ln.yview(*a)))

        code.insert("1.0", text)
        SyntaxHighlighter.apply(code, lang, C)
        code.config(state=tk.DISABLED)

        # In-preview find bar
        find_bar = tk.Frame(win, bg=C["surface2"])
        find_bar.pack(fill=tk.X)
        tk.Label(find_bar, text="Find:",
                 bg=C["surface2"], fg=C["fg_muted"],
                 font=(FONT_UI, 9)).pack(side=tk.LEFT, padx=8, pady=4)
        sv = tk.StringVar()
        find_e = tk.Entry(find_bar, textvariable=sv, relief=tk.FLAT,
                          bg=C["entry_bg"], fg=C["fg"],
                          insertbackground=C["fg"], font=(FONT_UI, 10),
                          highlightthickness=1, highlightbackground=C["border"],
                          highlightcolor=C["accent"], width=28)
        find_e.pack(side=tk.LEFT, ipady=3, padx=(0, 8), pady=4)
        find_count = tk.Label(find_bar, text="",
                              bg=C["surface2"], fg=C["fg_muted"], font=(FONT_UI, 8))
        find_count.pack(side=tk.LEFT)

        def _find(*_):
            code.config(state=tk.NORMAL)
            code.tag_remove("find_hl", "1.0", tk.END)
            q = sv.get()
            if not q:
                find_count.config(text="")
                code.config(state=tk.DISABLED)
                return
            count = 0
            start = "1.0"
            while True:
                pos = code.search(q, start, stopindex=tk.END, nocase=True)
                if not pos:
                    break
                end = f"{pos} + {len(q)} chars"
                code.tag_add("find_hl", pos, end)
                start = end
                count += 1
            code.tag_configure("find_hl", background=C["warning"], foreground="#000000")
            if count:
                first = code.search(q, "1.0", nocase=True)
                if first:
                    code.see(first)
            find_count.config(text=f"{count} match{'es' if count != 1 else ''}")
            code.config(state=tk.DISABLED)

        sv.trace_add("write", _find)
        find_e.bind("<Return>", _find)
        find_e.focus_set()

        # Status line
        lines = text.count("\n") + 1
        tk.Label(win,
                 text=f"  {lines:,} lines  ·  {len(text):,} chars  ·  {api_path}",
                 bg=C["status_bar"], fg=C["fg_subtle"],
                 font=(FONT_UI, 8), anchor=tk.W).pack(fill=tk.X)

    # ══════════════════════════════════════════════════════════════════
    #   COMMITS TAB LOGIC
    # ══════════════════════════════════════════════════════════════════
    def _load_commits_quick(self):
        self.notebook.select(self.commits_frame)
        self._load_commits()

    def _load_commits(self):
        if not self.current_repo:
            messagebox.showwarning("GitView", "Please select a repository first.")
            return
        self._set_status("Loading commits…")
        self.progress_bar.start()
        self.commits_tree.delete(*self.commits_tree.get_children())
        self._commits_data.clear()

        author = self.commit_author_var.get().strip() or None
        path   = self.commit_path_var.get().strip()   or None
        branch = self.branch_var.get()

        params: Dict[str, Any] = {"per_page": 60, "sha": branch}
        if author: params["author"] = author
        if path:   params["path"]   = path

        def _work():
            try:
                r = resilient_get(
                    self.session,
                    f"{self.api_base}/repos/{self.username}/"
                    f"{self.current_repo}/commits",
                    params=params, timeout=20)
                self._parse_rate_limit(r)
                self.root.after(0, self.progress_bar.stop)
                if r.status_code == 200:
                    commits = r.json()
                    self.root.after(0, lambda: self._display_commits(commits))
                elif r.status_code == 409:
                    self.root.after(0, lambda: self._set_status(
                        "Repository is empty — no commits yet", "warn"))
                else:
                    msg = r.json().get("message", "Error")
                    self.root.after(0, lambda: self._set_status(msg, "err"))
            except Exception as e:
                self.root.after(0, self.progress_bar.stop)
                self.root.after(0, lambda: self._set_status(str(e), "err"))

        threading.Thread(target=_work, daemon=True).start()

    def _display_commits(self, commits: List[Dict]):
        self.commits_tree.delete(*self.commits_tree.get_children())
        self._commits_data.clear()
        for c in commits:
            sha    = c.get("sha", "")[:7]
            commit = c.get("commit", {})
            msg    = (commit.get("message", "") or "").split("\n")[0][:80]
            author = (commit.get("author", {}) or {}).get("name", "—")
            date   = relative_time((commit.get("author", {}) or {}).get("date", ""))
            iid    = c.get("sha", str(id(c)))
            self.commits_tree.insert("", "end", iid=iid,
                                     text=f"  {msg}",
                                     values=(sha, author, date))
            self._commits_data[iid] = c
        n = len(commits)
        self.commit_count_lbl.config(text=f"{n} commit{'s' if n!=1 else ''}")
        self._set_status(f"Loaded {n} commit{'s' if n!=1 else ''}", "ok")

    def _on_commit_select(self, _=None):
        sel = self.commits_tree.selection()
        if not sel:
            return
        iid    = sel[0]
        c      = self._commits_data.get(iid, {})
        commit = c.get("commit", {})
        msg    = commit.get("message", "")
        sha    = c.get("sha", "")
        author = (commit.get("author", {}) or {})
        url    = c.get("html_url", "")

        self.commit_msg_lbl.config(text=msg[:160])
        self.commit_meta_lbl.config(
            text=f"{author.get('name','—')}  <{author.get('email','')}>  ·  "
                 f"{relative_time(author.get('date',''))}\n{sha[:12]}")

        # Fetch changed files
        self.commit_files_box.config(state=tk.NORMAL)
        self.commit_files_box.delete("1.0", tk.END)
        files = c.get("files", [])
        if files:
            for f in files:
                self.commit_files_box.insert(tk.END,
                    f"{f.get('status','?')}  {f.get('filename','')}\n")
        else:
            self.commit_files_box.insert(tk.END, "(loading…)")
            self._fetch_commit_files(sha, iid)
        self.commit_files_box.config(state=tk.DISABLED)

        self.commit_open_btn.config(command=lambda u=url: webbrowser.open(u))
        def _copy_sha():
            self.root.clipboard_clear()
            self.root.clipboard_append(sha)
            self._set_status(f"Copied SHA: {sha[:12]}", "ok")
        self.commit_copy_sha.config(command=_copy_sha)

    def _fetch_commit_files(self, sha: str, iid: str):
        def _work():
            try:
                r = resilient_get(
                    self.session,
                    f"{self.api_base}/repos/{self.username}/"
                    f"{self.current_repo}/commits/{sha}",
                    timeout=15)
                self._parse_rate_limit(r)
                if r.status_code == 200:
                    files = r.json().get("files", [])
                    self._commits_data[iid]["files"] = files
                    self.root.after(0, lambda: self._update_commit_files(files))
            except Exception:
                pass

        threading.Thread(target=_work, daemon=True).start()

    def _update_commit_files(self, files: List[Dict]):
        try:
            self.commit_files_box.config(state=tk.NORMAL)
            self.commit_files_box.delete("1.0", tk.END)
            for f in files:
                self.commit_files_box.insert(tk.END,
                    f"{f.get('status','?')}  {f.get('filename','')}\n")
            self.commit_files_box.config(state=tk.DISABLED)
        except Exception:
            pass

    def _on_commit_open(self, _=None):
        sel = self.commits_tree.selection()
        if not sel:
            return
        iid = sel[0]
        url = self._commits_data.get(iid, {}).get("html_url", "")
        if url:
            webbrowser.open(url)

    # ══════════════════════════════════════════════════════════════════
    #   DOWNLOAD
    # ══════════════════════════════════════════════════════════════════
    def _download_selected(self):
        sel = self.tree.selection()
        if not sel:
            self._set_status("No files selected — click a file first", "warn")
            return
        dest = filedialog.askdirectory(title="Choose Download Location")
        if not dest:
            return
        items_to_dl = []
        for iid in sel:
            vals = self.tree.item(iid, "values")
            name = self.tree.item(iid, "text").strip()
            if vals[1] == "File":
                path = f"{self.current_path}/{name}" if self.current_path else name
                items_to_dl.append((name, path))
        if not items_to_dl:
            self._set_status("Please select files, not folders", "warn")
            return
        self._start_download(items_to_dl, dest)

    def _download_single_file(self, name: str):
        dest = filedialog.askdirectory(title="Choose Download Location")
        if not dest:
            return
        path = f"{self.current_path}/{name}" if self.current_path else name
        self._start_download([(name, path)], dest)

    def _start_download(self, items: List[Tuple[str, str]], dest: str):
        total = len(items)
        self.progress_bar.start()
        self.progress_var.set(f"Downloading {total} file(s)…")
        self._log_operation(f"Download: {total} file(s) → {dest}")

        def _work():
            done = 0
            errors = []
            for name, path in items:
                try:
                    branch = self.branch_var.get()
                    r = resilient_get(
                        self.session,
                        f"{self.api_base}/repos/{self.username}/"
                        f"{self.current_repo}/contents/{path}",
                        params={"ref": branch} if branch else {},
                        timeout=20)
                    self._parse_rate_limit(r)
                    if r.status_code == 200:
                        raw_content = r.json().get("content", "")
                        file_bytes  = base64.b64decode(raw_content)
                        out_path    = os.path.join(dest, name)
                        with open(out_path, "wb") as fh:
                            fh.write(file_bytes)
                        done += 1
                        self.root.after(0, lambda d=done, t=total:
                                        self.progress_var.set(f"Downloaded {d}/{t}…"))
                    else:
                        errors.append(name)
                except Exception as e:
                    errors.append(f"{name}: {e}")

            self.root.after(0, self.progress_bar.stop)
            msg = f"Downloaded {done}/{total} file(s) to {dest}"
            if errors:
                msg += f"\n\nErrors:\n" + "\n".join(errors[:5])
                self.root.after(0, lambda: messagebox.showwarning("GitView", msg))
            else:
                self.root.after(0, lambda: self._set_status(msg, "ok"))
            self.root.after(0, lambda: self.progress_var.set("No active operations"))
            self.root.after(0, lambda: self._log_operation(
                f"Download complete: {done}/{total}"))

        threading.Thread(target=_work, daemon=True).start()

    def _download_entire_repo(self):
        if not self.current_repo:
            messagebox.showwarning("GitView", "Please select a repository first.")
            return
        dest = filedialog.askdirectory(title="Choose Download Destination")
        if not dest:
            return
        branch = self.branch_var.get()
        url    = (f"https://github.com/{self.username}/{self.current_repo}"
                  f"/archive/refs/heads/{branch}.zip")
        webbrowser.open(url)
        self._set_status(f"Opening download for {self.current_repo}…", "ok")
        self._log_operation(f"Download repo: {self.current_repo} ({branch})")

    def _download_current_folder(self):
        if not self.current_repo:
            return
        dest = filedialog.askdirectory(title="Choose Download Destination")
        if not dest:
            return
        items = [(f["name"], f.get("path", "")) for f in self.all_items["files"]]
        if items:
            self._start_download(items, dest)
        else:
            self._set_status("No files in current folder", "warn")

    # ══════════════════════════════════════════════════════════════════
    #   UPLOAD & CREATE
    # ══════════════════════════════════════════════════════════════════
    def _check_write_access(self) -> bool:
        if self.auth_mode == "public" or not self.token:
            messagebox.showwarning(
                "GitView — Read Only",
                "You are in public browse mode — uploading and editing is not available.\n\n"
                "To upload or edit files:\n"
                "  1. Switch to 'Use Token' mode\n"
                "  2. Connect with your GitHub Personal Access Token\n"
                "  3. Make sure your token has the 'repo' scope")
            return False
        return True

    def _upload_file(self):
        if not self._check_write_access():
            return
        if not self.current_repo:
            messagebox.showwarning("GitView", "Please select a repository first.")
            return
        path = filedialog.askopenfilename(title="Select File to Upload")
        if not path:
            return
        name = os.path.basename(path)
        msg  = simpledialog.askstring(
            "GitView — Commit Message",
            f"Commit message for uploading '{name}':",
            initialvalue=f"Upload {name} via GitView",
            parent=self.root)
        if not msg:
            return
        self._set_status(f"Uploading {name}…")
        self.progress_bar.start()

        def _work():
            try:
                with open(path, "rb") as fh:
                    content = base64.b64encode(fh.read()).decode()
                api_path = f"{self.current_path}/{name}" if self.current_path else name
                branch   = self.branch_var.get()
                payload  = {"message": msg, "content": content, "branch": branch}
                # Check if file exists (for update SHA)
                r_check = self.session.get(
                    f"{self.api_base}/repos/{self.username}/"
                    f"{self.current_repo}/contents/{api_path}",
                    params={"ref": branch}, timeout=10)
                if r_check.status_code == 200:
                    payload["sha"] = r_check.json().get("sha", "")
                r = self.session.put(
                    f"{self.api_base}/repos/{self.username}/"
                    f"{self.current_repo}/contents/{api_path}",
                    json=payload, timeout=30)
                self._parse_rate_limit(r)
                self.root.after(0, self.progress_bar.stop)
                if r.status_code in (200, 201):
                    self.root.after(0, lambda: self._set_status(f"Uploaded {name}", "ok"))
                    self.root.after(0, lambda: self._load_dir(self.current_path))
                    self.root.after(0, lambda: self._log_operation(f"Uploaded {name}"))
                else:
                    msg_err = r.json().get("message", "Upload failed")
                    self.root.after(0, lambda: self._set_status(msg_err, "err"))
            except Exception as e:
                self.root.after(0, self.progress_bar.stop)
                self.root.after(0, lambda: self._set_status(str(e), "err"))

        threading.Thread(target=_work, daemon=True).start()

    def _upload_folder(self):
        if not self._check_write_access():
            return
        if not self.current_repo:
            messagebox.showwarning("GitView", "Please select a repository first.")
            return
        folder = filedialog.askdirectory(title="Select Folder to Upload")
        if not folder:
            return
        files = []
        for root, _, fnames in os.walk(folder):
            for fn in fnames:
                fp = os.path.join(root, fn)
                rel = os.path.relpath(fp, folder).replace("\\", "/")
                files.append((fp, rel))

        if not files:
            messagebox.showinfo("GitView", "No files found in that folder.")
            return

        commit_msg = simpledialog.askstring(
            "GitView — Commit Message",
            f"Commit message for uploading {len(files)} file(s):",
            initialvalue=f"Upload folder {os.path.basename(folder)} via GitView",
            parent=self.root)
        if not commit_msg:
            return

        self._set_status(f"Uploading {len(files)} file(s)…")
        self.progress_bar.start()
        total = len(files)

        def _work():
            done = 0
            errors = []
            branch = self.branch_var.get()
            for fp, rel in files:
                try:
                    with open(fp, "rb") as fh:
                        content = base64.b64encode(fh.read()).decode()
                    api_path = (f"{self.current_path}/{rel}" if self.current_path else rel)
                    payload  = {"message": commit_msg, "content": content, "branch": branch}
                    r_check  = self.session.get(
                        f"{self.api_base}/repos/{self.username}/"
                        f"{self.current_repo}/contents/{api_path}",
                        params={"ref": branch}, timeout=10)
                    if r_check.status_code == 200:
                        payload["sha"] = r_check.json().get("sha", "")
                    r = self.session.put(
                        f"{self.api_base}/repos/{self.username}/"
                        f"{self.current_repo}/contents/{api_path}",
                        json=payload, timeout=30)
                    self._parse_rate_limit(r)
                    if r.status_code in (200, 201):
                        done += 1
                    else:
                        errors.append(rel)
                    self.root.after(0, lambda d=done: self.progress_var.set(
                        f"Uploaded {d}/{total}…"))
                except Exception as e:
                    errors.append(f"{rel}: {e}")

            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, lambda: self._set_status(
                f"Uploaded {done}/{total} files", "ok"))
            self.root.after(0, lambda: self._load_dir(self.current_path))
            self.root.after(0, lambda: self._log_operation(
                f"Folder upload: {done}/{total}"))

        threading.Thread(target=_work, daemon=True).start()

    def _create_file_dialog(self):
        if not self._check_write_access():
            return
        if not self.current_repo:
            messagebox.showwarning("GitView", "Please select a repository first.")
            return
        C = self.C
        dlg = tk.Toplevel(self.root)
        dlg.title("GitView — Create New File")
        dlg.geometry("560x440")
        dlg.configure(bg=C["bg"])
        dlg.resizable(True, True)
        dlg.grab_set()

        tk.Label(dlg, text="📝  Create New File",
                 bg=C["bg"], fg=C["fg"],
                 font=(FONT_UI, 13, "bold")).pack(padx=20, pady=(16, 8), anchor=tk.W)

        def lbl(txt):
            tk.Label(dlg, text=txt, bg=C["bg"], fg=C["fg_subtle"],
                     font=(FONT_UI, 8, "bold")).pack(padx=20, anchor=tk.W, pady=(8, 2))

        lbl("FILE NAME  (e.g. hello.py  or  docs/guide.md)")
        name_var = tk.StringVar()
        tk.Entry(dlg, textvariable=name_var, relief=tk.FLAT,
                 bg=C["entry_bg"], fg=C["fg"], insertbackground=C["fg"],
                 font=(FONT_MONO, 11), highlightthickness=1,
                 highlightbackground=C["border"],
                 highlightcolor=C["accent"]).pack(padx=20, pady=(0, 4), fill=tk.X, ipady=6)

        lbl("FILE CONTENT")
        content_txt = tk.Text(dlg, relief=tk.FLAT,
                              bg=C["entry_bg"], fg=C["fg"],
                              insertbackground=C["fg"], font=(FONT_MONO, 10),
                              highlightthickness=1,
                              highlightbackground=C["border"],
                              height=10)
        content_txt.pack(padx=20, fill=tk.BOTH, expand=True)

        lbl("COMMIT MESSAGE")
        msg_var = tk.StringVar(value="Create new file via GitView")
        tk.Entry(dlg, textvariable=msg_var, relief=tk.FLAT,
                 bg=C["entry_bg"], fg=C["fg"], insertbackground=C["fg"],
                 font=(FONT_UI, 10), highlightthickness=1,
                 highlightbackground=C["border"],
                 highlightcolor=C["accent"]).pack(padx=20, pady=(0, 4), fill=tk.X, ipady=5)

        btn_row = tk.Frame(dlg, bg=C["bg"])
        btn_row.pack(fill=tk.X, padx=20, pady=12)

        def _create():
            fname = name_var.get().strip()
            if not fname:
                messagebox.showerror("GitView", "Please enter a file name.", parent=dlg)
                return
            body    = content_txt.get("1.0", tk.END)
            commit  = msg_var.get().strip() or "Create file via GitView"
            content = base64.b64encode(body.encode()).decode()
            branch  = self.branch_var.get()
            prefix  = f"{self.current_path}/" if self.current_path else ""
            api_path = f"{prefix}{fname}"
            dlg.destroy()

            self._set_status(f"Creating {fname}…")
            self.progress_bar.start()

            def _work():
                try:
                    r = self.session.put(
                        f"{self.api_base}/repos/{self.username}/"
                        f"{self.current_repo}/contents/{api_path}",
                        json={"message": commit, "content": content, "branch": branch},
                        timeout=20)
                    self._parse_rate_limit(r)
                    self.root.after(0, self.progress_bar.stop)
                    if r.status_code == 201:
                        self.root.after(0, lambda: self._set_status(
                            f"Created {fname}", "ok"))
                        self.root.after(0, lambda: self._load_dir(self.current_path))
                        self.root.after(0, lambda: self._log_operation(
                            f"Created file: {api_path}"))
                    else:
                        msg_e = r.json().get("message", "Failed")
                        self.root.after(0, lambda: self._set_status(msg_e, "err"))
                except Exception as e:
                    self.root.after(0, self.progress_bar.stop)
                    self.root.after(0, lambda: self._set_status(str(e), "err"))

            threading.Thread(target=_work, daemon=True).start()

        make_btn(btn_row, "✓  Create File", _create, style="accent", C=C,
                 font=(FONT_UI, 10, "bold"), pady=7).pack(side=tk.LEFT, padx=(0, 8))
        make_btn(btn_row, "Cancel", dlg.destroy, style="ghost", C=C,
                 font=(FONT_UI, 10), pady=7).pack(side=tk.LEFT)

    def _create_folder_dialog(self):
        if not self._check_write_access():
            return
        if not self.current_repo:
            return
        name = simpledialog.askstring(
            "GitView — New Folder",
            "Folder name:\n(A placeholder .gitkeep file will be created inside it)",
            parent=self.root)
        if not name:
            return
        name    = name.strip()
        prefix  = f"{self.current_path}/" if self.current_path else ""
        api_path = f"{prefix}{name}/.gitkeep"
        content = base64.b64encode(b"").decode()
        branch  = self.branch_var.get()

        def _work():
            try:
                r = self.session.put(
                    f"{self.api_base}/repos/{self.username}/"
                    f"{self.current_repo}/contents/{api_path}",
                    json={"message": f"Create folder {name} via GitView",
                          "content": content, "branch": branch},
                    timeout=20)
                self._parse_rate_limit(r)
                if r.status_code == 201:
                    self.root.after(0, lambda: self._set_status(
                        f"Created folder: {name}", "ok"))
                    self.root.after(0, lambda: self._load_dir(self.current_path))
                    self.root.after(0, lambda: self._log_operation(
                        f"Created folder: {prefix}{name}"))
                else:
                    msg = r.json().get("message", "Failed")
                    self.root.after(0, lambda: self._set_status(msg, "err"))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(str(e), "err"))

        threading.Thread(target=_work, daemon=True).start()

    def _rename_selected(self):
        if not self._check_write_access():
            return
        sel = self.tree.selection()
        if not sel:
            return
        old_name = self.tree.item(sel[0], "text").strip()
        new_name = simpledialog.askstring(
            "GitView — Rename",
            f"New name for '{old_name}':",
            initialvalue=old_name, parent=self.root)
        if not new_name or new_name == old_name:
            return
        # GitHub doesn't support rename directly — download + upload + delete
        messagebox.showinfo("GitView — Rename",
                            "Rename: download the file, re-upload with new name,\n"
                            "then delete the old one.\n\n"
                            "This is how GitHub API works.\nUse the browser for complex renames.")

    def _delete_selected(self):
        if not self._check_write_access():
            return
        sel = self.tree.selection()
        if not sel:
            return
        names = [self.tree.item(i, "text").strip() for i in sel]
        if not messagebox.askyesno(
            "GitView — Confirm Delete",
            f"Permanently delete {len(names)} item(s)?\n\n" +
            "\n".join(f"  • {n}" for n in names[:8]) +
            ("\n  …" if len(names) > 8 else "") +
            "\n\nThis cannot be undone!"):
            return

        self.progress_bar.start()
        self._set_status(f"Deleting {len(names)} item(s)…")

        def _work():
            done = 0
            branch = self.branch_var.get()
            for iid in sel:
                name = self.tree.item(iid, "text").strip()
                vals = self.tree.item(iid, "values")
                if vals[1] == "Folder":
                    continue  # can't delete folders via API easily
                api_path = f"{self.current_path}/{name}" if self.current_path else name
                try:
                    r_info = self.session.get(
                        f"{self.api_base}/repos/{self.username}/"
                        f"{self.current_repo}/contents/{api_path}",
                        params={"ref": branch}, timeout=10)
                    if r_info.status_code != 200:
                        continue
                    sha = r_info.json().get("sha", "")
                    r = self.session.delete(
                        f"{self.api_base}/repos/{self.username}/"
                        f"{self.current_repo}/contents/{api_path}",
                        json={"message": f"Delete {name} via GitView",
                              "sha": sha, "branch": branch},
                        timeout=20)
                    if r.status_code == 200:
                        done += 1
                        self._log_operation(f"Deleted: {api_path}")
                except Exception as e:
                    self._log_operation(f"Delete error {name}: {e}")

            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, lambda: self._set_status(f"Deleted {done} file(s)", "ok"))
            self.root.after(0, lambda: self._load_dir(self.current_path))

        threading.Thread(target=_work, daemon=True).start()

    def _create_repo_dialog(self):
        if not self._check_write_access():
            return
        C = self.C
        dlg = tk.Toplevel(self.root)
        dlg.title("GitView — Create New Repository")
        dlg.geometry("460x320")
        dlg.configure(bg=C["bg"])
        dlg.grab_set()

        tk.Label(dlg, text="➕  Create New Repository",
                 bg=C["bg"], fg=C["fg"],
                 font=(FONT_UI, 13, "bold")).pack(padx=20, pady=(16, 8), anchor=tk.W)

        def lbl(txt):
            tk.Label(dlg, text=txt, bg=C["bg"], fg=C["fg_subtle"],
                     font=(FONT_UI, 8, "bold")).pack(padx=20, anchor=tk.W, pady=(8, 2))

        lbl("REPOSITORY NAME")
        name_var = tk.StringVar()
        tk.Entry(dlg, textvariable=name_var, relief=tk.FLAT,
                 bg=C["entry_bg"], fg=C["fg"], insertbackground=C["fg"],
                 font=(FONT_MONO, 11), highlightthickness=1,
                 highlightbackground=C["border"]).pack(padx=20, fill=tk.X, ipady=6)

        lbl("DESCRIPTION  (optional)")
        desc_var = tk.StringVar()
        tk.Entry(dlg, textvariable=desc_var, relief=tk.FLAT,
                 bg=C["entry_bg"], fg=C["fg"], insertbackground=C["fg"],
                 font=(FONT_UI, 10), highlightthickness=1,
                 highlightbackground=C["border"]).pack(padx=20, fill=tk.X, ipady=5)

        priv_var = tk.BooleanVar(value=False)
        cb_row   = tk.Frame(dlg, bg=C["bg"])
        cb_row.pack(padx=20, pady=(10, 0), anchor=tk.W)
        tk.Checkbutton(cb_row, text="Private repository",
                       variable=priv_var,
                       bg=C["bg"], fg=C["fg"],
                       selectcolor=C["surface2"],
                       activebackground=C["bg"],
                       font=(FONT_UI, 10)).pack(side=tk.LEFT)

        btn_row = tk.Frame(dlg, bg=C["bg"])
        btn_row.pack(fill=tk.X, padx=20, pady=14)

        def _create():
            rname = name_var.get().strip()
            if not rname:
                messagebox.showerror("GitView", "Repository name is required.", parent=dlg)
                return
            dlg.destroy()
            self._set_status(f"Creating repository {rname}…")
            self.progress_bar.start()

            def _work():
                try:
                    r = self.session.post(
                        f"{self.api_base}/user/repos",
                        json={"name": rname,
                              "description": desc_var.get().strip(),
                              "private": priv_var.get(),
                              "auto_init": True},
                        timeout=20)
                    self._parse_rate_limit(r)
                    self.root.after(0, self.progress_bar.stop)
                    if r.status_code == 201:
                        self.root.after(0, lambda: self._set_status(
                            f"Created repository: {rname}", "ok"))
                        self.root.after(0, self._load_repos)
                        self.root.after(0, lambda: self._log_operation(
                            f"Created repo: {self.username}/{rname}"))
                    else:
                        msg = r.json().get("message", "Failed")
                        self.root.after(0, lambda: self._set_status(msg, "err"))
                except Exception as e:
                    self.root.after(0, self.progress_bar.stop)
                    self.root.after(0, lambda: self._set_status(str(e), "err"))

            threading.Thread(target=_work, daemon=True).start()

        make_btn(btn_row, "✓  Create", _create, style="accent", C=C,
                 font=(FONT_UI, 10, "bold"), pady=7).pack(side=tk.LEFT, padx=(0, 8))
        make_btn(btn_row, "Cancel", dlg.destroy, style="ghost", C=C,
                 font=(FONT_UI, 10), pady=7).pack(side=tk.LEFT)

    # ══════════════════════════════════════════════════════════════════
    #   MISC ACTIONS
    # ══════════════════════════════════════════════════════════════════
    def _copy_path(self):
        sel = self.tree.selection()
        if not sel:
            return
        name     = self.tree.item(sel[0], "text").strip()
        api_path = f"{self.current_path}/{name}" if self.current_path else name
        self.root.clipboard_clear()
        self.root.clipboard_append(api_path)
        self._set_status(f"Copied path: {api_path}", "ok")

    def _open_in_browser(self):
        if not self.current_repo:
            return
        branch = self.branch_var.get()
        path   = self.current_path or ""
        url    = (f"https://github.com/{self.username}/{self.current_repo}"
                  f"/tree/{branch}/{path}")
        webbrowser.open(url)
        self._set_status("Opened in browser", "ok")

    # ══════════════════════════════════════════════════════════════════
    #   RATE LIMIT
    # ══════════════════════════════════════════════════════════════════
    def _parse_rate_limit(self, r: requests.Response):
        try:
            remaining = int(r.headers.get("X-RateLimit-Remaining", self.rate_remaining))
            limit     = int(r.headers.get("X-RateLimit-Limit",     self.rate_limit))
            reset_ts  = float(r.headers.get("X-RateLimit-Reset",   self.rate_reset_ts))
            self.rate_remaining = remaining
            self.rate_limit     = limit
            self.rate_reset_ts  = reset_ts
            self.root.after(0, self._update_rate_display)
        except Exception:
            pass

    def _update_rate_display(self):
        try:
            rem   = self.rate_remaining
            lim   = self.rate_limit
            pct   = (rem / lim * 100) if lim else 100
            C     = self.C
            colour = (C["rate_ok"]   if pct > 40 else
                      C["rate_warn"] if pct > 15 else
                      C["rate_low"])
            self.rate_lbl.config(text=f"API  ●  {rem:,}/{lim:,}", fg=colour)
            if self.rate_reset_ts:
                reset_str = datetime.fromtimestamp(self.rate_reset_ts).strftime("%H:%M")
                self.api_rate_lbl.config(text=f"resets {reset_str}", fg=C["fg_subtle"])
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════════════
    #   OPERATION LOG
    # ══════════════════════════════════════════════════════════════════
    def _log_operation(self, msg: str):
        ts    = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}"
        self.op_log.append(entry)
        try:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, entry + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        except Exception:
            pass

    def _clear_log(self):
        self.op_log.clear()
        try:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete("1.0", tk.END)
            self.log_text.config(state=tk.DISABLED)
        except Exception:
            pass

    def _set_status(self, msg: str, level: str = "info"):
        colours = {
            "ok":   self.C["success"],
            "err":  self.C["danger"],
            "warn": self.C["warning"],
            "info": self.C["fg_muted"],
        }
        colour = colours.get(level, self.C["fg_muted"])
        try:
            self.status_lbl.config(text=f"  {msg}", fg=colour)
            self.progress_var.set(msg if level in ("ok", "err") else msg)
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════════════
    #   HELP
    # ══════════════════════════════════════════════════════════════════
    def _show_help(self):
        C = self.C
        win = tk.Toplevel(self.root)
        win.title("GitView v3 — Help & Quick Start")
        win.geometry("720x640")
        win.configure(bg=C["bg"])

        tk.Frame(win, bg=C["accent"], height=3).pack(fill=tk.X)
        hdr = tk.Frame(win, bg=C["surface"], height=48)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="❓  GitView v3 — Help & Quick Start",
                 bg=C["surface"], fg=C["fg"],
                 font=(FONT_UI, 12, "bold")).pack(side=tk.LEFT, padx=16, pady=12)

        txt = tk.Text(win, wrap=tk.WORD, bg=C["surface"], fg=C["fg"],
                      font=(FONT_UI, 10), relief=tk.FLAT,
                      padx=22, pady=16, selectbackground=C["tree_select"],
                      highlightthickness=0)
        sb  = ttk.Scrollbar(win, command=txt.yview)
        txt.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        txt.pack(fill=tk.BOTH, expand=True)

        HELP = f"""
GitView v{APP_VERSION} — Quick Start Guide
{'─'*64}

👋  GETTING STARTED (for everyone — no experience needed!)
   GitView lets you browse, download, and manage GitHub repositories.
   You have two ways to start:

   ① 🔑  USE TOKEN  (full access — recommended)
      • Go to: github.com → Settings → Developer settings
        → Personal access tokens → Generate new token (Classic)
      • Tick the 'repo' scope, click Generate, copy the token
      • Paste it in the TOKEN field and click ⚡ Connect
      • You'll have 5,000 API calls/hour

   ② 👤  BROWSE PUBLIC PROFILE  (no account needed!)
      • Just type any GitHub username  (e.g.  torvalds)
      • Or paste a GitHub URL  (e.g.  github.com/microsoft)
      • Click 🚀 Browse  and explore their public repos
      • You'll have 60 API calls/hour (unauthenticated limit)

📁  EXPLORER TAB
   • Pick a repository from the REPOSITORY dropdown
   • Pick a branch in BRANCH
   • Double-click a 📁 folder to enter it
   • Double-click a 📄 file to preview it with syntax highlighting
   • ⌂ Home = root   ↑ Up = parent folder  [Home / Backspace]
   • Type in the 🔍 filter box to instantly find files  [Ctrl+F]
   • Click column headers to sort by Name / Type / Size
   • Right-click any item for a context menu

🔍  SEARCH TAB  (NEW in v3 — SCOPED TO LOADED USER)
   • Repos:   Search through the loaded user's repository names & descriptions
   • Files:   Find files by name across all their repos  (needs token)
   • Commits: Search commit messages by this user  (needs token)
   • Topics:  Filter repos by programming language or topic
   ➡ Results show only this user's content — not all of GitHub!

📥  DOWNLOADING
   • Select files → Download Selected  [Ctrl+D]
   • Right-click → Download
   • Operations tab → Download Entire Repository (downloads .zip)

📤  UPLOADING & EDITING  (token mode only)
   • Upload File  [Ctrl+U]  ·  Upload Folder  ·  New File  [Ctrl+N]
   • Delete  [Del]  ·  Context menu → Rename

📌  PINNING REPOS
   • Select a repo, then click 📌 Pin Repo in the toolbar
   • Pinned repos always appear at the top of the list

⌨️  KEYBOARD SHORTCUTS
   Ctrl+F   Focus file filter        F5      Refresh repos
   Ctrl+D   Download selection       F2      Rename
   Ctrl+U   Upload file              Del     Delete selected
   Ctrl+N   New file                 Space   Preview file
   Home     Go to root               Backspace  Go up one level

🎨  UI TIPS
   • 🌙/☀️  Theme button — toggle dark/light mode
   • The API badge (top right) shows remaining API calls
   • Yellow = getting low  ·  Red = very low  ·  Green = fine

💡  TIPS FOR NON-TECH USERS
   • You can explore anyone's public GitHub code — just type their username
   • "Repository" means a project/folder of code
   • "Branch" = version (usually 'main' or 'master' is the latest)
   • Click file names to see their content — even code looks nice!
   • Can't find a file? Use the 🔍 filter box — type to search instantly

{'─'*64}
Author: {AUTHOR_NAME}  ·  {AUTHOR_FROM}
LinkedIn: {AUTHOR_LI_URL}
GitHub:   {GITHUB_URL}
"""
        txt.insert("1.0", HELP)
        txt.config(state=tk.DISABLED)

        bot = tk.Frame(win, bg=C["surface2"], height=44)
        bot.pack(fill=tk.X, side=tk.BOTTOM)
        bot.pack_propagate(False)
        make_btn(bot, "✕  Close", win.destroy, style="ghost", C=C
                 ).pack(side=tk.RIGHT, padx=12, pady=6)
        make_btn(bot, "🔗  LinkedIn", lambda: webbrowser.open(AUTHOR_LI_URL),
                 style="accent", C=C).pack(side=tk.LEFT, padx=12, pady=6)
        make_btn(bot, "⭐  Star on GitHub", lambda: webbrowser.open(GITHUB_URL),
                 style="ghost", C=C).pack(side=tk.LEFT, padx=(0, 8), pady=6)
        make_btn(bot, "🔑  Get Token Free",
                 lambda: webbrowser.open("https://github.com/settings/tokens/new"),
                 style="ghost", C=C).pack(side=tk.LEFT, padx=(0, 8), pady=6)


# ══════════════════════════════════════════════════════════════════════════
#   ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    # Set window icon (graceful fallback)
    try:
        root.iconbitmap(default="gitview.ico")
    except Exception:
        pass

    app = GitView(root)  # noqa: F841

    # Centre on primary monitor
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth()  - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()