#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════╗
║                         GitView  v4.0                                   ║
║              Premium GitHub Repository Explorer                         ║
║                                                                         ║
║  Author  : Ali Essam                                                    ║
║  Origin  : Egypt 🇪🇬                                                    ║
║  LinkedIn: linkedin.com/in/dragonked2                                   ║
║  GitHub  : github.com/dragonked2/gitview                                ║
║  License : MIT                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  What's NEW in v4.0                                                     ║
║  ─────────────────────────────                                          ║
║  ✓ COMPLETELY REDESIGNED UI — premium dark/light themes                 ║
║  ✓ FIXED search — all scopes now work reliably                          ║
║  ✓ NEW: Content search — find keywords INSIDE file contents             ║
║  ✓ NEW: Rich result cards with highlighted keyword fragments            ║
║  ✓ NEW: Search history (last 30 searches)                               ║
║  ✓ NEW: Result pagination (20 per page)                                 ║
║  ✓ NEW: Advanced search filters (language, repo, file type)             ║
║  ✓ Fixed file search headers (text-match Accept header)                 ║
║  ✓ Fixed: unauthenticated search with helpful guidance                  ║
║  ✓ New: Search works for both token AND public browse mode              ║
║  ✓ Improved: Keyword highlighting in result snippets                    ║
║  ✓ Resizable split panes with PanedWindow                               ║
║  ✓ Improved status bar with animations                                  ║
║  ✓ Better error messages and recovery                                   ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

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
#   DESIGN SYSTEM  — Premium Dark & Light palettes
# ══════════════════════════════════════════════════════════════════════════
DARK: Dict[str, str] = {
    "bg":              "#070b10",
    "surface":         "#0d1117",
    "surface2":        "#161b22",
    "surface3":        "#1c2431",
    "card":            "#111820",
    "border":          "#21262d",
    "border_bright":   "#30363d",
    "fg":              "#e6edf3",
    "fg_muted":        "#8b949e",
    "fg_subtle":       "#484f58",
    "accent":          "#1f6feb",
    "accent_hover":    "#388bfd",
    "accent_subtle":   "#0c2d6b",
    "accent_glow":     "#163359",
    "success":         "#3fb950",
    "success_subtle":  "#0a2213",
    "warning":         "#e3b341",
    "warning_subtle":  "#272115",
    "danger":          "#f85149",
    "danger_subtle":   "#300a0a",
    "purple":          "#bc8cff",
    "purple_subtle":   "#1e1340",
    "cyan":            "#39d0d8",
    "cyan_subtle":     "#0c2e31",
    "orange":          "#f0883e",
    "pink":            "#ff7b72",
    "tree_select":     "#0d2645",
    "entry_bg":        "#010409",
    "entry_border":    "#30363d",
    "tag_dir":         "#58a6ff",
    "tag_file":        "#e6edf3",
    "title_bar":       "#040811",
    "status_bar":      "#040811",
    "scrollbar":       "#21262d",
    "scrollbar_hover": "#30363d",
    "rate_ok":         "#3fb950",
    "rate_warn":       "#e3b341",
    "rate_low":        "#f85149",
    "badge_token":     "#1a7f37",
    "badge_public":    "#9a3412",
    "highlight_bg":    "#2d3b1a",
    "highlight_fg":    "#7ee787",
    # Syntax
    "syn_kw":          "#ff7b72",
    "syn_str":         "#a5d6ff",
    "syn_cmt":         "#6e7681",
    "syn_num":         "#79c0ff",
    "syn_func":        "#d2a8ff",
    "syn_deco":        "#ffa657",
    "syn_builtin":     "#79c0ff",
}

LIGHT: Dict[str, str] = {
    "bg":              "#f0f2f5",
    "surface":         "#ffffff",
    "surface2":        "#f6f8fa",
    "surface3":        "#eaeef2",
    "card":            "#fafbfc",
    "border":          "#d0d7de",
    "border_bright":   "#b0bac4",
    "fg":              "#1f2328",
    "fg_muted":        "#57606a",
    "fg_subtle":       "#9ea8b3",
    "accent":          "#0969da",
    "accent_hover":    "#0550ae",
    "accent_subtle":   "#dbeafe",
    "accent_glow":     "#cce5ff",
    "success":         "#1a7f37",
    "success_subtle":  "#d1f8dc",
    "warning":         "#9a6700",
    "warning_subtle":  "#fff8c5",
    "danger":          "#cf222e",
    "danger_subtle":   "#ffebe9",
    "purple":          "#8250df",
    "purple_subtle":   "#f3f0ff",
    "cyan":            "#0969da",
    "cyan_subtle":     "#ddf4ff",
    "orange":          "#bc4c00",
    "pink":            "#a40e26",
    "tree_select":     "#dbeafe",
    "entry_bg":        "#ffffff",
    "entry_border":    "#d0d7de",
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
    "highlight_bg":    "#fff8c5",
    "highlight_fg":    "#9a6700",
    "syn_kw":          "#cf222e",
    "syn_str":         "#0550ae",
    "syn_cmt":         "#6e7781",
    "syn_num":         "#0550ae",
    "syn_func":        "#8250df",
    "syn_deco":        "#bc4c00",
    "syn_builtin":     "#0969da",
}

FONT_UI    = "Segoe UI"
FONT_MONO  = "Cascadia Code" if os.name == "nt" else "Menlo"
FONT_TITLE = "Segoe UI Semibold"

APP_VERSION   = "4.0.0"
AUTHOR_NAME   = "Ali Essam"
AUTHOR_FROM   = "Egypt 🇪🇬"
AUTHOR_LI     = "linkedin.com/in/dragonked2"
AUTHOR_LI_URL = "https://www.linkedin.com/in/dragonked2"
GITHUB_URL    = "https://github.com/dragonked2/gitview"
CONFIG_FILE   = Path.home() / ".gitview_config.json"
RESULTS_PER_PAGE = 20


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
    text = text.strip().rstrip("/")
    if not text:
        return None
    text = re.sub(r"^https?://", "", text)
    text = re.sub(r"^(www\.)?github\.com/?", "", text)
    parts = [p for p in text.split("/") if p]
    if not parts:
        return None
    username = parts[0]
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


def score_match(query: str, text: str) -> int:
    """Score how well a query matches text. Higher = better match."""
    q = query.lower()
    t = text.lower()
    if t == q:                  return 100
    if t.startswith(q):         return 80
    if q in t.split():          return 70
    if t.endswith(q):           return 60
    if q in t:                  return 50
    # fuzzy: count matching chars
    matches = sum(1 for c in q if c in t)
    return int((matches / max(len(q), 1)) * 30)


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

    def __init__(self, widget: tk.Widget, text: str, C: Optional[Dict] = None):
        self.widget    = widget
        self.text      = text
        self.C         = C or DARK
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
        x = self.widget.winfo_rootx() + 16
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        self.tip.wm_attributes("-topmost", True)
        C = self.C
        outer = tk.Frame(self.tip, bg=C.get("border_bright","#30363d"), padx=1, pady=1)
        outer.pack()
        tk.Label(outer, text=self.text,
                 bg=C.get("surface3","#1c2431"), fg=C.get("fg","#e6edf3"),
                 font=(FONT_UI, 8), padx=10, pady=5).pack()

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
                        activebackground=C["accent_hover"],  activeforeground="#ffffff"),
        "danger":  dict(bg=C["danger"],    fg="#ffffff",
                        activebackground="#ff6961",           activeforeground="#ffffff"),
        "success": dict(bg=C["success"],   fg="#ffffff",
                        activebackground="#56d364",           activeforeground="#ffffff"),
        "ghost":   dict(bg=C["surface"],   fg=C["fg_muted"],
                        activebackground=C["surface2"],       activeforeground=C["fg"]),
        "warning": dict(bg=C["warning"],   fg="#000000",
                        activebackground="#f0c040",           activeforeground="#000000"),
        "purple":  dict(bg=C["purple"],    fg="#ffffff",
                        activebackground="#d2a8ff",           activeforeground="#000000"),
        "ghost2":  dict(bg=C["surface2"],  fg=C["fg_muted"],
                        activebackground=C["surface3"],       activeforeground=C["fg"]),
    }
    s    = styles.get(style, styles["default"])
    font = kw.pop("font", (FONT_UI, 9))
    padx = kw.pop("padx", 12)
    pady = kw.pop("pady", 5)
    btn  = tk.Button(parent, text=text, command=cmd,
                     font=font, relief=tk.FLAT, cursor="hand2",
                     padx=padx, pady=pady, bd=0,
                     highlightthickness=0, **s, **kw)

    def on_enter(_): btn.config(bg=s["activebackground"], fg=s["activeforeground"])
    def on_leave(_): btn.config(bg=s["bg"],               fg=s["fg"])

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
            merged_headers = dict(headers or {})
            r = session.get(url, params=params, headers=merged_headers,
                            timeout=timeout)
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
    raise last_exc or RuntimeError("Request failed after retries")


# ══════════════════════════════════════════════════════════════════════════
#   HORIZONTAL DIVIDER helper
# ══════════════════════════════════════════════════════════════════════════
def hdiv(parent, C, pady=0):
    tk.Frame(parent, bg=C["border"], height=1).pack(fill=tk.X, pady=pady)


# ══════════════════════════════════════════════════════════════════════════
#   SECTION LABEL helper
# ══════════════════════════════════════════════════════════════════════════
def section_lbl(parent, text, C):
    return tk.Label(parent, text=text,
                    bg=C["surface"], fg=C["fg_subtle"],
                    font=(FONT_UI, 7, "bold"))


# ══════════════════════════════════════════════════════════════════════════
#   MAIN APPLICATION CLASS
# ══════════════════════════════════════════════════════════════════════════
class GitView:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("GitView v4 — Premium GitHub Explorer")
        self.root.geometry("1520x900")
        self.root.minsize(1100, 640)

        self.session = requests.Session()
        self.session.headers.update({
            "Accept":     "application/vnd.github.v3+json",
            "User-Agent": f"GitView/{APP_VERSION}",
        })

        # ── Core state ─────────────────────────────────────────────
        self.api_base                       = "https://api.github.com"
        self.token: Optional[str]          = None
        self.username: Optional[str]       = None
        self.auth_mode: str                = "token"
        self.current_repo: Optional[str]   = None
        self.current_repo_full: Optional[str] = None
        self.current_path: str             = ""
        self.current_branch: str           = "main"
        self.repo_data: Dict[str, Any]     = {}
        self.all_items: Dict[str, List]    = {"dirs": [], "files": []}
        self.current_theme: str            = "dark"
        self.C: Dict[str, str]             = DARK
        self.pinned_repos: List[str]       = []

        self.sort_col     = "name"
        self.sort_reverse = False

        self.rate_remaining = 60
        self.rate_limit     = 60
        self.rate_reset_ts  = 0.0

        self.recent_repos: deque = deque(maxlen=20)
        self.op_log: List[str]   = []

        # Search state
        self.search_thread: Optional[threading.Thread] = None
        self.search_cancel = threading.Event()
        self._search_history: deque = deque(maxlen=30)
        self._search_results_all: List[Dict] = []
        self._search_page: int = 1
        self._search_scope: str = "Repos"

        self.show_tok    = False
        self._preview_windows: List[tk.Toplevel] = []
        self._commits_data: Dict[str, Any] = {}
        self._filter_entry_ref: Optional[tk.Entry] = None

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
                    rowheight=34, font=(FONT_UI, 10),
                    borderwidth=0, relief="flat")
        s.configure("Treeview.Heading",
                    background=C["surface2"], foreground=C["fg_muted"],
                    font=(FONT_UI, 8, "bold"), relief="flat", padding=(10, 8))
        s.map("Treeview",
              background=[("selected", C["tree_select"])],
              foreground=[("selected", C["accent_hover"])])
        s.map("Treeview.Heading",
              background=[("active", C["surface3"])])

        s.configure("TNotebook", background=C["bg"], borderwidth=0,
                    tabmargins=[0, 0, 0, 0])
        s.configure("TNotebook.Tab",
                    background=C["surface2"], foreground=C["fg_muted"],
                    padding=[20, 9], font=(FONT_UI, 9, "bold"), borderwidth=0)
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
                    borderwidth=0, width=8)
        s.map("TScrollbar",
              background=[("active", C["scrollbar_hover"]),
                          ("pressed", C["accent"])])

        s.configure("Horizontal.TProgressbar",
                    troughcolor=C["surface2"], background=C["accent"],
                    borderwidth=0, thickness=3)

        s.configure("TPanedwindow", background=C["bg"])

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
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))

        self.notebook = ttk.Notebook(body)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.browser_frame = tk.Frame(self.notebook, bg=C["bg"])
        self.notebook.add(self.browser_frame, text="  📁  Explorer  ")

        self.search_frame = tk.Frame(self.notebook, bg=C["bg"])
        self.notebook.add(self.search_frame, text="  🔍  Search  ")

        self.commits_frame = tk.Frame(self.notebook, bg=C["bg"])
        self.notebook.add(self.commits_frame, text="  🕐  Commits  ")

        self.ops_frame = tk.Frame(self.notebook, bg=C["bg"])
        self.notebook.add(self.ops_frame, text="  ⚡  Operations  ")

        self.about_frame = tk.Frame(self.notebook, bg=C["bg"])
        self.notebook.add(self.about_frame, text="  ℹ️  About  ")

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
        # Accent top border
        tk.Frame(parent, bg=C["accent"], height=2).pack(fill=tk.X)

        bar = tk.Frame(parent, bg=C["title_bar"], height=56)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        inner = tk.Frame(bar, bg=C["title_bar"])
        inner.pack(fill=tk.BOTH, expand=True, padx=18)

        # Brand left
        logo_f = tk.Frame(inner, bg=C["title_bar"])
        logo_f.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(logo_f, text="⬡", bg=C["title_bar"], fg=C["accent"],
                 font=(FONT_UI, 22)).pack(side=tk.LEFT, padx=(0, 8), pady=8)
        brand_f = tk.Frame(logo_f, bg=C["title_bar"])
        brand_f.pack(side=tk.LEFT, fill=tk.Y, pady=10)
        tk.Label(brand_f, text="GitView",
                 bg=C["title_bar"], fg=C["fg"],
                 font=(FONT_TITLE, 15, "bold")).pack(anchor=tk.W)
        tk.Label(brand_f, text=f"v{APP_VERSION}  ·  Premium GitHub Explorer",
                 bg=C["title_bar"], fg=C["fg_muted"],
                 font=(FONT_UI, 8)).pack(anchor=tk.W)

        # Rate limit badge
        rl_f = tk.Frame(inner, bg=C["title_bar"])
        rl_f.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0), pady=10)
        self.api_rate_lbl = tk.Label(rl_f, text="",
                                     bg=C["title_bar"], fg=C["fg_subtle"],
                                     font=(FONT_UI, 7))
        self.api_rate_lbl.pack(anchor=tk.E)
        self.rate_lbl = tk.Label(rl_f, text="API  ●  —/—",
                                 bg=C["title_bar"], fg=C["fg_subtle"],
                                 font=(FONT_MONO, 8))
        self.rate_lbl.pack(anchor=tk.E)

        # Right controls
        right = tk.Frame(inner, bg=C["title_bar"])
        right.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 8))
        for label, cmd in [
            ("❓  Help",   self._show_help),
            ("🌐  GitHub", lambda: webbrowser.open(GITHUB_URL)),
        ]:
            make_btn(right, label, cmd, style="ghost", C=C,
                     font=(FONT_UI, 9), padx=10, pady=4).pack(side=tk.RIGHT, padx=2)

        self.theme_btn = make_btn(
            right,
            "🌙  Dark" if self.current_theme == "dark" else "☀️  Light",
            self._toggle_theme, style="ghost", C=C,
            font=(FONT_UI, 9), padx=10, pady=4)
        self.theme_btn.pack(side=tk.RIGHT, padx=2)

    # ── Auth Bar ──────────────────────────────────────────────────
    def _build_auth_bar(self, parent):
        C = self.C

        bar = tk.Frame(parent, bg=C["surface"],
                       highlightbackground=C["border"], highlightthickness=1)
        bar.pack(fill=tk.X, padx=12, pady=(4, 0))

        inner = tk.Frame(bar, bg=C["surface"])
        inner.pack(fill=tk.BOTH, expand=True, padx=14, pady=8)

        # Mode tabs
        left = tk.Frame(inner, bg=C["surface"])
        left.pack(side=tk.LEFT, fill=tk.Y)

        mode_row = tk.Frame(left, bg=C["surface"])
        mode_row.pack(anchor=tk.W)

        self.auth_mode_var = tk.StringVar(value=self.auth_mode)

        self._tab_token_btn = make_btn(
            mode_row, "🔑  Token Mode", self._switch_to_token,
            style="accent" if self.auth_mode == "token" else "ghost2",
            C=C, font=(FONT_UI, 8, "bold"), padx=12, pady=4)
        self._tab_token_btn.pack(side=tk.LEFT)

        self._tab_public_btn = make_btn(
            mode_row, "👤  Browse Public",
            self._switch_to_public,
            style="accent" if self.auth_mode == "public" else "ghost2",
            C=C, font=(FONT_UI, 8, "bold"), padx=12, pady=4)
        self._tab_public_btn.pack(side=tk.LEFT, padx=(4, 0))

        # Token frame
        self._token_frame = tk.Frame(left, bg=C["surface"])
        self._token_frame.pack(fill=tk.X, pady=(6, 0))

        tok_row = tk.Frame(self._token_frame, bg=C["surface"])
        tok_row.pack(fill=tk.X)

        section_lbl(self._token_frame, "PERSONAL ACCESS TOKEN", C).pack(
            anchor=tk.W, pady=(0, 3))
        tok_row2 = tk.Frame(self._token_frame, bg=C["surface"])
        tok_row2.pack(fill=tk.X)

        self.token_var = tk.StringVar()
        self.token_entry = tk.Entry(
            tok_row2, textvariable=self.token_var,
            show="•", relief=tk.FLAT,
            bg=C["entry_bg"], fg=C["fg"],
            insertbackground=C["fg"],
            font=(FONT_MONO, 10), width=42,
            highlightthickness=1,
            highlightbackground=C["entry_border"],
            highlightcolor=C["accent"])
        self.token_entry.pack(side=tk.LEFT, ipady=6, padx=(0, 4))
        self.token_entry.bind("<Return>", lambda _: self._connect_token())

        self.eye_btn = make_btn(tok_row2, "👁", self._toggle_token_vis,
                                style="ghost2", C=C, font=(FONT_UI, 11),
                                padx=6, pady=4)
        self.eye_btn.pack(side=tk.LEFT, padx=(0, 4))

        self.connect_btn = make_btn(tok_row2, "  ⚡  Connect  ",
                                    self._connect_token, style="accent", C=C,
                                    font=(FONT_UI, 9, "bold"), padx=14, pady=6)
        self.connect_btn.pack(side=tk.LEFT)

        self.disconnect_btn = make_btn(tok_row2, "✕  Disconnect",
                                       self._disconnect, style="danger", C=C,
                                       font=(FONT_UI, 9), pady=6)
        self.disconnect_btn.pack(side=tk.LEFT, padx=(4, 0))
        self.disconnect_btn.pack_forget()

        self.tok_help_lbl = tk.Label(
            self._token_frame,
            text="🆘  No token? Click here to generate one for free →",
            bg=C["surface"], fg=C["accent"],
            font=(FONT_UI, 8), cursor="hand2")
        self.tok_help_lbl.pack(anchor=tk.W, pady=(3, 0))
        self.tok_help_lbl.bind(
            "<Button-1>",
            lambda _: webbrowser.open(
                "https://github.com/settings/tokens/new"
                "?description=GitView&scopes=repo"))

        # Public frame
        self._public_frame = tk.Frame(left, bg=C["surface"])

        section_lbl(self._public_frame,
                    "USERNAME  or  github.com/username  or  full URL", C).pack(
            anchor=tk.W, pady=(0, 3))

        pub_row = tk.Frame(self._public_frame, bg=C["surface"])
        pub_row.pack(fill=tk.X)

        self.public_var = tk.StringVar()
        self.public_entry = tk.Entry(
            pub_row, textvariable=self.public_var,
            relief=tk.FLAT,
            bg=C["entry_bg"], fg=C["fg"],
            insertbackground=C["fg"],
            font=(FONT_MONO, 11), width=36,
            highlightthickness=1,
            highlightbackground=C["entry_border"],
            highlightcolor=C["accent"])
        self.public_entry.pack(side=tk.LEFT, ipady=6, padx=(0, 6))
        self.public_entry.bind("<Return>", lambda _: self._connect_public())

        for label, val in [("torvalds", "torvalds"),
                            ("microsoft", "microsoft"),
                            ("google", "google")]:
            b = make_btn(pub_row, label,
                         lambda v=val: (self.public_var.set(v), self._connect_public()),
                         style="ghost2", C=C, font=(FONT_UI, 8), padx=7, pady=6)
            b.pack(side=tk.LEFT, padx=2)

        self.public_connect_btn = make_btn(
            pub_row, "  🚀  Browse  ",
            self._connect_public, style="success", C=C,
            font=(FONT_UI, 9, "bold"), padx=14, pady=6)
        self.public_connect_btn.pack(side=tk.LEFT, padx=(6, 0))

        tk.Label(self._public_frame,
                 text="📌  Public repos only  ·  60 API calls/hr unauthenticated",
                 bg=C["surface"], fg=C["warning"],
                 font=(FONT_UI, 7)).pack(anchor=tk.W, pady=(3, 0))

        if self.auth_mode == "token":
            self._token_frame.pack(fill=tk.X, pady=(6, 0))
        else:
            self._public_frame.pack(fill=tk.X, pady=(6, 0))

        # Right: user card
        right_sep = tk.Frame(inner, bg=C["border"], width=1)
        right_sep.pack(side=tk.RIGHT, fill=tk.Y, padx=12)

        right_area = tk.Frame(inner, bg=C["surface"])
        right_area.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 8))

        self.avatar_lbl = tk.Label(right_area, text="○",
                                   bg=C["surface"], fg=C["fg_subtle"],
                                   font=(FONT_UI, 32))
        self.avatar_lbl.pack(side=tk.LEFT, padx=(0, 12))

        user_col = tk.Frame(right_area, bg=C["surface"])
        user_col.pack(side=tk.LEFT, fill=tk.Y, pady=4)

        self.user_name_lbl = tk.Label(user_col, text="Not Connected",
                                      bg=C["surface"], fg=C["fg_muted"],
                                      font=(FONT_TITLE, 12, "bold"))
        self.user_name_lbl.pack(anchor=tk.W)
        self.user_meta_lbl = tk.Label(user_col,
                                      text="Choose Token or Public mode above",
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

        meta_area = tk.Frame(inner, bg=C["surface"])
        meta_area.pack(side=tk.RIGHT, fill=tk.Y, padx=12)
        self.repo_meta_lbl = tk.Label(meta_area, text="",
                                      bg=C["surface"], fg=C["fg_muted"],
                                      font=(FONT_UI, 8), justify=tk.RIGHT)
        self.repo_meta_lbl.pack(anchor=tk.E)
        self.repo_desc_lbl = tk.Label(meta_area, text="",
                                      bg=C["surface"], fg=C["fg_subtle"],
                                      font=(FONT_UI, 8), justify=tk.RIGHT,
                                      wraplength=280)
        self.repo_desc_lbl.pack(anchor=tk.E)

    # ── Mode Switching ─────────────────────────────────────────────
    def _switch_to_token(self):
        self.auth_mode = "token"
        C = self.C
        self._tab_token_btn.config(bg=C["accent"], fg="#ffffff",
                                   activebackground=C["accent_hover"])
        self._tab_public_btn.config(bg=C["surface2"], fg=C["fg_muted"],
                                    activebackground=C["surface3"])
        self._public_frame.pack_forget()
        self._token_frame.pack(fill=tk.X, pady=(6, 0))

    def _switch_to_public(self):
        self.auth_mode = "public"
        C = self.C
        self._tab_public_btn.config(bg=C["accent"], fg="#ffffff",
                                    activebackground=C["accent_hover"])
        self._tab_token_btn.config(bg=C["surface2"], fg=C["fg_muted"],
                                   activebackground=C["surface3"])
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
        toolbar.pack(fill=tk.X, pady=(10, 0))

        # Repo selector
        repo_grp = tk.Frame(toolbar, bg=C["bg"])
        repo_grp.pack(side=tk.LEFT)
        section_lbl(repo_grp, "REPOSITORY", C).pack(anchor=tk.W, pady=(0, 2))
        self.repo_var = tk.StringVar()
        self.repo_combo = ttk.Combobox(repo_grp, textvariable=self.repo_var,
                                       width=42, state="readonly",
                                       font=(FONT_UI, 10))
        self.repo_combo.pack(side=tk.LEFT, ipady=4)
        self.repo_combo.bind("<<ComboboxSelected>>", self._on_repo_select)

        # Branch selector
        br_grp = tk.Frame(toolbar, bg=C["bg"])
        br_grp.pack(side=tk.LEFT, padx=(16, 0))
        section_lbl(br_grp, "BRANCH", C).pack(anchor=tk.W, pady=(0, 2))
        self.branch_var = tk.StringVar(value="main")
        self.branch_combo = ttk.Combobox(br_grp, textvariable=self.branch_var,
                                         width=18, state="readonly",
                                         font=(FONT_UI, 10))
        self.branch_combo.pack(side=tk.LEFT, ipady=4)
        self.branch_combo.bind("<<ComboboxSelected>>", self._on_branch_select)

        # Toolbar buttons
        btn_row = tk.Frame(toolbar, bg=C["bg"])
        btn_row.pack(side=tk.LEFT, padx=(16, 0))
        section_lbl(btn_row, "ACTIONS", C).pack(anchor=tk.W, pady=(0, 2))
        actions_row = tk.Frame(btn_row, bg=C["bg"])
        actions_row.pack()
        for label, cmd, style, tip in [
            ("⌂  Home",   self._go_home,        "ghost2",  "Go to repository root [Home]"),
            ("↑  Up",     self._go_up,           "ghost2",  "Go to parent folder [Backspace]"),
            ("🔄  Refresh", self._refresh_dir,   "ghost2",  "Refresh current folder [F5]"),
            ("📌  Pin",    self._pin_repo,        "ghost2",  "Pin/unpin this repository"),
            ("📥  Download", self._download_selected, "ghost2", "Download selected [Ctrl+D]"),
            ("📤  Upload",  self._upload_file,   "ghost2",  "Upload a file [Ctrl+U]"),
            ("✏️  New File", self._create_file_dialog, "ghost2", "Create new file [Ctrl+N]"),
        ]:
            b = make_btn(actions_row, label, cmd, style=style, C=C,
                         font=(FONT_UI, 8), padx=8, pady=4)
            b.pack(side=tk.LEFT, padx=1)
            Tooltip(b, tip, C)

        # Path bar + filter
        path_row = tk.Frame(f, bg=C["surface"],
                            highlightbackground=C["border"], highlightthickness=1)
        path_row.pack(fill=tk.X, pady=(6, 0))
        path_inner = tk.Frame(path_row, bg=C["surface"])
        path_inner.pack(fill=tk.X, padx=12, pady=5)

        tk.Label(path_inner, text="📂", bg=C["surface"], fg=C["accent"],
                 font=(FONT_UI, 10)).pack(side=tk.LEFT)
        self.path_lbl = tk.Label(path_inner, text="/",
                                 bg=C["surface"], fg=C["fg_muted"],
                                 font=(FONT_MONO, 9))
        self.path_lbl.pack(side=tk.LEFT, padx=(4, 0))

        # Filter
        filt_frame = tk.Frame(path_inner, bg=C["surface"])
        filt_frame.pack(side=tk.RIGHT)
        tk.Label(filt_frame, text="🔍", bg=C["surface"], fg=C["fg_subtle"],
                 font=(FONT_UI, 9)).pack(side=tk.LEFT)
        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", lambda *_: self._apply_filter())
        filt_entry = tk.Entry(filt_frame, textvariable=self.filter_var,
                              relief=tk.FLAT,
                              bg=C["entry_bg"], fg=C["fg"],
                              insertbackground=C["fg"],
                              font=(FONT_UI, 10), width=22,
                              highlightthickness=1,
                              highlightbackground=C["entry_border"],
                              highlightcolor=C["accent"])
        filt_entry.pack(side=tk.LEFT, ipady=4, padx=(2, 0))
        self._filter_entry_ref = filt_entry

        self.file_count_lbl = tk.Label(path_inner, text="",
                                       bg=C["surface"], fg=C["fg_subtle"],
                                       font=(FONT_UI, 8))
        self.file_count_lbl.pack(side=tk.RIGHT, padx=(0, 8))

        # File tree
        tree_wrap = tk.Frame(f, bg=C["surface"],
                             highlightbackground=C["border"], highlightthickness=1)
        tree_wrap.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

        self.tree = ttk.Treeview(tree_wrap,
                                 columns=("type_icon", "kind", "size"),
                                 show="tree headings",
                                 selectmode="extended")
        self.tree.heading("#0",         text="  Name",   anchor=tk.W)
        self.tree.heading("type_icon",  text="",         anchor=tk.CENTER)
        self.tree.heading("kind",       text="Type",     anchor=tk.W)
        self.tree.heading("size",       text="Size",     anchor=tk.E)
        self.tree.column("#0",        width=440, minwidth=200, stretch=True)
        self.tree.column("type_icon", width=40,  minwidth=30,  stretch=False)
        self.tree.column("kind",      width=80,  minwidth=50,  stretch=False)
        self.tree.column("size",      width=90,  minwidth=60,  stretch=False)

        vsb = ttk.Scrollbar(tree_wrap, orient=tk.VERTICAL,   command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_wrap, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side=tk.RIGHT,  fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>",          self._on_tree_double)
        self.tree.bind("<Return>",            self._on_tree_double)
        self.tree.bind("<Button-3>",          self._show_ctx_menu)
        self.tree.heading("#0",   command=lambda: self._sort_by("name"))
        self.tree.heading("kind", command=lambda: self._sort_by("kind"))
        self.tree.heading("size", command=lambda: self._sort_by("size"))

        # Info panel
        self.info_frame = tk.Frame(tree_wrap, bg=C["surface"],
                                   highlightbackground=C["border"],
                                   highlightthickness=0)
        self.info_lbl = tk.Label(self.info_frame, text="",
                                 bg=C["surface"], fg=C["accent"],
                                 font=(FONT_UI, 18))
        self.info_lbl.pack(pady=(30, 8))
        self.info_main = tk.Label(self.info_frame, text="",
                                  bg=C["surface"], fg=C["fg_muted"],
                                  font=(FONT_UI, 12, "bold"))
        self.info_main.pack()
        self.info_extra = tk.Label(self.info_frame, text="",
                                   bg=C["surface"], fg=C["fg_subtle"],
                                   font=(FONT_UI, 9), wraplength=320,
                                   justify=tk.CENTER)
        self.info_extra.pack(pady=(4, 0))

    # ══════════════════════════════════════════════════════════════════
    #   SEARCH TAB  — COMPLETELY REDESIGNED v4
    # ══════════════════════════════════════════════════════════════════
    def _build_search_tab(self):
        C = self.C
        f = self.search_frame

        # ── Top Search Bar ─────────────────────────────────────────
        top_bar = tk.Frame(f, bg=C["surface"],
                           highlightbackground=C["border"], highlightthickness=1)
        top_bar.pack(fill=tk.X, pady=(10, 0))

        top_inner = tk.Frame(top_bar, bg=C["surface"])
        top_inner.pack(fill=tk.X, padx=14, pady=10)

        # Search input row
        inp_row = tk.Frame(top_inner, bg=C["surface"])
        inp_row.pack(fill=tk.X)

        tk.Label(inp_row, text="🔍",
                 bg=C["surface"], fg=C["accent"],
                 font=(FONT_UI, 14)).pack(side=tk.LEFT, padx=(0, 6))

        self.usearch_var = tk.StringVar()
        self.search_entry = tk.Entry(
            inp_row, textvariable=self.usearch_var,
            relief=tk.FLAT,
            bg=C["entry_bg"], fg=C["fg"],
            insertbackground=C["accent"],
            font=(FONT_UI, 13), width=46,
            highlightthickness=1,
            highlightbackground=C["entry_border"],
            highlightcolor=C["accent"])
        self.search_entry.pack(side=tk.LEFT, ipady=7, padx=(0, 8))
        self.search_entry.bind("<Return>", lambda _: self._do_user_search())
        self.search_entry.bind("<Down>",   lambda _: self._show_history_dropdown())
        self.search_entry.bind("<Up>",     lambda _: self._show_history_dropdown())

        self.search_go_btn = make_btn(inp_row, "  Search  ",
                                      self._do_user_search, style="accent", C=C,
                                      font=(FONT_UI, 10, "bold"), padx=18, pady=7)
        self.search_go_btn.pack(side=tk.LEFT)

        self.search_cancel_btn = make_btn(inp_row, "✕  Cancel",
                                          self._cancel_user_search,
                                          style="danger", C=C,
                                          font=(FONT_UI, 9), pady=7, padx=10)
        self.search_cancel_btn.pack(side=tk.LEFT, padx=(4, 0))
        self.search_cancel_btn.config(state=tk.DISABLED)

        self.search_hist_btn = make_btn(inp_row, "🕐  History",
                                        self._show_history_dropdown,
                                        style="ghost2", C=C,
                                        font=(FONT_UI, 9), pady=7, padx=10)
        self.search_hist_btn.pack(side=tk.LEFT, padx=(4, 0))

        self.search_count_lbl = tk.Label(inp_row, text="",
                                         bg=C["surface"], fg=C["fg_muted"],
                                         font=(FONT_UI, 9))
        self.search_count_lbl.pack(side=tk.RIGHT)

        # ── Scope selector pills ──────────────────────────────────
        scope_row = tk.Frame(top_inner, bg=C["surface"])
        scope_row.pack(fill=tk.X, pady=(8, 0))

        tk.Label(scope_row, text="SEARCH IN:",
                 bg=C["surface"], fg=C["fg_subtle"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=(0, 8))

        self.usearch_scope_var = tk.StringVar(value="Repos")
        self._scope_btns: Dict[str, tk.Button] = {}
        scopes_info = [
            ("Repos",   "📦", "Repository names & descriptions"),
            ("Content", "📄", "Keyword search INSIDE file contents  ★ NEW"),
            ("Files",   "🗂", "Search file names across all repos"),
            ("Commits", "🕐", "Search through commit messages"),
            ("Topics",  "🏷", "Filter repos by language or topic"),
        ]
        for sc, icon, tip in scopes_info:
            is_sel = sc == "Repos"
            b = tk.Button(
                scope_row,
                text=f"{icon} {sc}",
                command=lambda s=sc: self._select_scope(s),
                font=(FONT_UI, 8, "bold"),
                relief=tk.FLAT, cursor="hand2", padx=10, pady=4, bd=0,
                bg=C["accent"] if is_sel else C["surface2"],
                fg="#ffffff" if is_sel else C["fg_muted"],
                activebackground=C["accent_hover"],
                activeforeground="#ffffff",
                highlightthickness=0)
            b.pack(side=tk.LEFT, padx=(0, 4))
            Tooltip(b, tip, C)
            self._scope_btns[sc] = b

        # Info banner
        self.search_banner = tk.Frame(f, bg=C["warning_subtle"])
        self.search_banner.pack(fill=tk.X)
        self._banner_lbl = tk.Label(
            self.search_banner,
            text="ℹ️   Connect to a GitHub user first, then search across all their repositories.",
            bg=C["warning_subtle"], fg=C["warning"],
            font=(FONT_UI, 9), padx=12, pady=7, anchor=tk.W)
        self._banner_lbl.pack(fill=tk.X)

        # ── Results area ──────────────────────────────────────────
        results_outer = tk.Frame(f, bg=C["bg"])
        results_outer.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        # Left: scrollable result cards
        left_panel = tk.Frame(results_outer, bg=C["bg"])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Results header bar
        res_hdr = tk.Frame(left_panel, bg=C["surface"],
                           highlightbackground=C["border"], highlightthickness=1,
                           height=34)
        res_hdr.pack(fill=tk.X)
        res_hdr.pack_propagate(False)
        tk.Label(res_hdr, text="RESULTS",
                 bg=C["surface"], fg=C["fg_subtle"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=12, pady=8)
        self.search_prog_lbl = tk.Label(res_hdr, text="",
                                        bg=C["surface"], fg=C["accent"],
                                        font=(FONT_UI, 8))
        self.search_prog_lbl.pack(side=tk.LEFT, padx=8, pady=8)

        # Sort controls
        sort_row = tk.Frame(res_hdr, bg=C["surface"])
        sort_row.pack(side=tk.RIGHT, padx=8, pady=4)
        tk.Label(sort_row, text="Sort:",
                 bg=C["surface"], fg=C["fg_subtle"],
                 font=(FONT_UI, 7)).pack(side=tk.LEFT)
        self.result_sort_var = tk.StringVar(value="relevance")
        for sv, sl in [("relevance","Relevance"),("name","Name"),("date","Date")]:
            rb = tk.Radiobutton(sort_row, text=sl,
                                variable=self.result_sort_var, value=sv,
                                bg=C["surface"], fg=C["fg_muted"],
                                selectcolor=C["surface3"],
                                activebackground=C["surface"],
                                font=(FONT_UI, 8), cursor="hand2",
                                command=self._resort_results)
            rb.pack(side=tk.LEFT, padx=2)

        # Scrollable results list
        res_scroll_frame = tk.Frame(left_panel, bg=C["bg"])
        res_scroll_frame.pack(fill=tk.BOTH, expand=True)

        self.results_canvas = tk.Canvas(res_scroll_frame, bg=C["bg"],
                                        highlightthickness=0)
        results_vsb = ttk.Scrollbar(res_scroll_frame, orient=tk.VERTICAL,
                                    command=self.results_canvas.yview)
        self.results_canvas.configure(yscrollcommand=results_vsb.set)
        results_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.results_inner = tk.Frame(self.results_canvas, bg=C["bg"])
        self._results_window = self.results_canvas.create_window(
            (0, 0), window=self.results_inner, anchor="nw")

        self.results_inner.bind("<Configure>", self._on_results_configure)
        self.results_canvas.bind("<Configure>", self._on_canvas_configure)
        self.results_canvas.bind("<MouseWheel>",
                                 lambda e: self.results_canvas.yview_scroll(
                                     int(-1*(e.delta/120)), "units"))
        self.results_canvas.bind("<Button-4>",
                                 lambda e: self.results_canvas.yview_scroll(-1, "units"))
        self.results_canvas.bind("<Button-5>",
                                 lambda e: self.results_canvas.yview_scroll(1, "units"))

        # Pagination bar
        self.pager_frame = tk.Frame(left_panel, bg=C["surface"],
                                    highlightbackground=C["border"], highlightthickness=1,
                                    height=38)
        self.pager_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.pager_frame.pack_propagate(False)
        self._build_pager()

        # Right: detail pane
        right_panel = tk.Frame(results_outer, bg=C["surface"],
                               highlightbackground=C["border"], highlightthickness=1,
                               width=340)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
        right_panel.pack_propagate(False)

        det_hdr = tk.Frame(right_panel, bg=C["surface2"], height=34)
        det_hdr.pack(fill=tk.X)
        det_hdr.pack_propagate(False)
        tk.Label(det_hdr, text="DETAILS",
                 bg=C["surface2"], fg=C["fg_muted"],
                 font=(FONT_UI, 7, "bold")).pack(side=tk.LEFT, padx=12, pady=8)

        det_scroll = tk.Frame(right_panel, bg=C["surface"])
        det_scroll.pack(fill=tk.BOTH, expand=True)

        self.detail_text = tk.Text(
            det_scroll, wrap=tk.WORD,
            bg=C["surface"], fg=C["fg"],
            font=(FONT_UI, 9), relief=tk.FLAT,
            highlightthickness=0, state=tk.DISABLED,
            padx=14, pady=12,
            selectbackground=C["tree_select"])
        det_vsb = ttk.Scrollbar(det_scroll, command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=det_vsb.set)
        det_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.detail_text.pack(fill=tk.BOTH, expand=True)

        det_btns = tk.Frame(right_panel, bg=C["surface"])
        det_btns.pack(fill=tk.X, padx=12, pady=(0, 12))
        self.det_open_btn = make_btn(det_btns, "🌐  Open on GitHub",
                                     lambda: None, style="accent", C=C,
                                     font=(FONT_UI, 9), pady=5)
        self.det_open_btn.pack(fill=tk.X)
        self.det_nav_btn = make_btn(det_btns, "📁  Navigate in Explorer",
                                    lambda: None, style="ghost2", C=C,
                                    font=(FONT_UI, 9), pady=5)
        self.det_nav_btn.pack(fill=tk.X, pady=(4, 0))

        self._show_search_empty_state()

    def _on_results_configure(self, event=None):
        self.results_canvas.configure(
            scrollregion=self.results_canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        w = self.results_canvas.winfo_width()
        self.results_canvas.itemconfig(self._results_window, width=w)

    def _build_pager(self):
        C = self.C
        for w in self.pager_frame.winfo_children():
            w.destroy()
        inner = tk.Frame(self.pager_frame, bg=C["surface"])
        inner.pack(side=tk.LEFT, padx=12, pady=5)
        self.pager_prev = make_btn(inner, "← Prev",
                                   lambda: self._go_page(-1), style="ghost2", C=C,
                                   font=(FONT_UI, 8), padx=8, pady=3)
        self.pager_prev.pack(side=tk.LEFT)
        self.pager_lbl = tk.Label(inner, text="Page 0 / 0",
                                  bg=C["surface"], fg=C["fg_muted"],
                                  font=(FONT_UI, 8))
        self.pager_lbl.pack(side=tk.LEFT, padx=8)
        self.pager_next = make_btn(inner, "Next →",
                                   lambda: self._go_page(1), style="ghost2", C=C,
                                   font=(FONT_UI, 8), padx=8, pady=3)
        self.pager_next.pack(side=tk.LEFT)

    def _go_page(self, delta: int):
        total = len(self._search_results_all)
        max_page = max(1, (total + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE)
        new_page = max(1, min(max_page, self._search_page + delta))
        if new_page != self._search_page:
            self._search_page = new_page
            self._render_results_page()

    def _select_scope(self, scope: str):
        self.usearch_scope_var.set(scope)
        C = self.C
        for sc, btn in self._scope_btns.items():
            if sc == scope:
                btn.config(bg=C["accent"], fg="#ffffff",
                           activebackground=C["accent_hover"])
            else:
                btn.config(bg=C["surface2"], fg=C["fg_muted"],
                           activebackground=C["surface3"])

    def _show_search_empty_state(self):
        C = self.C
        for w in self.results_inner.winfo_children():
            w.destroy()
        frame = tk.Frame(self.results_inner, bg=C["bg"])
        frame.pack(pady=60)
        tk.Label(frame, text="🔍",
                 bg=C["bg"], fg=C["fg_subtle"],
                 font=(FONT_UI, 36)).pack()
        tk.Label(frame, text="Search within loaded user",
                 bg=C["bg"], fg=C["fg_muted"],
                 font=(FONT_TITLE, 13, "bold")).pack(pady=(8, 0))
        tk.Label(frame,
                 text="Connect a GitHub account first, then search\nrepos · file content · file names · commits · topics",
                 bg=C["bg"], fg=C["fg_subtle"],
                 font=(FONT_UI, 9), justify=tk.CENTER).pack(pady=(6, 0))

    def _show_history_dropdown(self):
        if not self._search_history:
            return
        C = self.C
        popup = tk.Toplevel(self.root)
        popup.wm_overrideredirect(True)
        popup.wm_attributes("-topmost", True)
        x = self.search_entry.winfo_rootx()
        y = self.search_entry.winfo_rooty() + self.search_entry.winfo_height() + 2
        popup.wm_geometry(f"+{x}+{y}")
        outer = tk.Frame(popup, bg=C["border_bright"], padx=1, pady=1)
        outer.pack()
        inner = tk.Frame(outer, bg=C["surface2"])
        inner.pack()
        for query in reversed(list(self._search_history)):
            lbl = tk.Label(inner, text=f"🕐  {query}",
                           bg=C["surface2"], fg=C["fg"],
                           font=(FONT_UI, 9), anchor=tk.W,
                           padx=12, pady=5, cursor="hand2",
                           width=40)
            lbl.pack(fill=tk.X)
            def _pick(q=query, p=popup):
                self.usearch_var.set(q)
                p.destroy()
                self._do_user_search()
            lbl.bind("<Button-1>", lambda _, fn=_pick: fn())
            lbl.bind("<Enter>",    lambda e, w=lbl: w.config(bg=C["tree_select"]))
            lbl.bind("<Leave>",    lambda e, w=lbl: w.config(bg=C["surface2"]))
        popup.bind("<FocusOut>", lambda _: popup.destroy())
        popup.focus_set()

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

        for lbl, var_name in [("AUTHOR FILTER", "commit_author_var"),
                               ("PATH FILTER",   "commit_path_var")]:
            grp = tk.Frame(inner, bg=C["surface"])
            grp.pack(side=tk.LEFT, padx=(0, 16))
            tk.Label(grp, text=lbl,
                     bg=C["surface"], fg=C["fg_subtle"],
                     font=(FONT_UI, 7, "bold")).pack(anchor=tk.W, pady=(0, 2))
            var = tk.StringVar()
            setattr(self, var_name, var)
            tk.Entry(grp, textvariable=var,
                     relief=tk.FLAT, bg=C["entry_bg"], fg=C["fg"],
                     insertbackground=C["fg"], font=(FONT_UI, 10),
                     width=18, highlightthickness=1,
                     highlightbackground=C["entry_border"],
                     highlightcolor=C["accent"]).pack(ipady=5)

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
        self.commits_tree = ttk.Treeview(
            com_wrap, columns=("sha", "author", "date"),
            show="tree headings", selectmode="browse")
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

        self.commit_detail = tk.Text(
            cdp, wrap=tk.WORD, bg=C["surface"], fg=C["fg"],
            font=(FONT_MONO, 9), relief=tk.FLAT,
            highlightthickness=0, state=tk.DISABLED,
            padx=12, pady=12)
        cdp_sb = ttk.Scrollbar(cdp, command=self.commit_detail.yview)
        self.commit_detail.configure(yscrollcommand=cdp_sb.set)
        cdp_sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.commit_detail.pack(fill=tk.BOTH, expand=True)

        cdp_btns = tk.Frame(cdp, bg=C["surface"])
        cdp_btns.pack(fill=tk.X, padx=12, pady=(0, 12))
        self.commit_open_btn = make_btn(cdp_btns, "🌐  View on GitHub",
                                        lambda: None, style="accent", C=C,
                                        font=(FONT_UI, 9), pady=5)
        self.commit_open_btn.pack(fill=tk.X)
        self.commit_copy_sha = make_btn(cdp_btns, "📋  Copy SHA",
                                        lambda: None, style="ghost2", C=C,
                                        font=(FONT_UI, 9), pady=5)
        self.commit_copy_sha.pack(fill=tk.X, pady=(4, 0))

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

        log_card = tk.Frame(right, bg=C["surface"],
                            highlightbackground=C["border"], highlightthickness=1)
        log_card.pack(fill=tk.BOTH, expand=True)
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
                 font=(FONT_UI, 64)).pack()
        tk.Label(center, text="GitView", bg=C["bg"], fg=C["fg"],
                 font=(FONT_TITLE, 36, "bold")).pack()
        tk.Label(center, text=f"v{APP_VERSION}  ·  Premium GitHub Explorer",
                 bg=C["bg"], fg=C["fg_muted"], font=(FONT_UI, 11)).pack(pady=(4, 0))

        tk.Frame(center, bg=C["border"], height=1, width=500).pack(pady=20)

        info_grid = tk.Frame(center, bg=C["bg"])
        info_grid.pack()
        for i, (k, v) in enumerate([
            ("Author",   AUTHOR_NAME),
            ("Origin",   AUTHOR_FROM),
            ("LinkedIn", AUTHOR_LI),
            ("License",  "MIT"),
            ("GitHub",   GITHUB_URL),
        ]):
            tk.Label(info_grid, text=k, bg=C["bg"], fg=C["fg_subtle"],
                     font=(FONT_UI, 9, "bold"), width=10, anchor=tk.E
                     ).grid(row=i, column=0, padx=(0, 8), pady=3, sticky=tk.E)
            tk.Label(info_grid, text=v, bg=C["bg"], fg=C["fg"],
                     font=(FONT_UI, 9), anchor=tk.W
                     ).grid(row=i, column=1, pady=3, sticky=tk.W)

        tk.Frame(center, bg=C["border"], height=1, width=500).pack(pady=20)

        btn_row = tk.Frame(center, bg=C["bg"])
        btn_row.pack()
        for lbl, url, style in [
            ("⭐  Star on GitHub",  GITHUB_URL,         "accent"),
            ("💼  LinkedIn",        AUTHOR_LI_URL,       "default"),
            ("🔑  Get Token Free",
             "https://github.com/settings/tokens/new", "ghost"),
        ]:
            make_btn(btn_row, lbl, lambda u=url: webbrowser.open(u),
                     style=style, C=C, font=(FONT_UI, 9), padx=12
                     ).pack(side=tk.LEFT, padx=6)

    # ── Status Bar ────────────────────────────────────────────────
    def _build_statusbar(self, parent):
        C = self.C
        bar = tk.Frame(parent, bg=C["status_bar"], height=28)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        tk.Frame(bar, bg=C["border"], height=1).pack(fill=tk.X, side=tk.TOP)

        inner = tk.Frame(bar, bg=C["status_bar"])
        inner.pack(fill=tk.BOTH, expand=True, padx=12)

        self.status_lbl = tk.Label(inner, text="  Ready",
                                   bg=C["status_bar"], fg=C["fg_muted"],
                                   font=(FONT_UI, 8))
        self.status_lbl.pack(side=tk.LEFT)

        tk.Label(inner,
                 text=f"GitView v{APP_VERSION}  ·  {AUTHOR_NAME}  ·  {AUTHOR_FROM}",
                 bg=C["status_bar"], fg=C["fg_subtle"],
                 font=(FONT_UI, 7)).pack(side=tk.RIGHT)

    # ── Context Menu ──────────────────────────────────────────────
    def _build_context_menu(self):
        C = self.C
        self.ctx = tk.Menu(self.root, tearoff=0,
                           bg=C["surface2"], fg=C["fg"],
                           activebackground=C["tree_select"],
                           activeforeground=C["accent_hover"],
                           font=(FONT_UI, 9), bd=0, relief=tk.FLAT)
        self.ctx.add_command(label="📄  Preview File",     command=self._preview_selected)
        self.ctx.add_command(label="📥  Download",         command=self._download_selected)
        self.ctx.add_separator()
        self.ctx.add_command(label="✏️   Rename",           command=self._rename_selected)
        self.ctx.add_command(label="🗑  Delete",           command=self._delete_selected)
        self.ctx.add_separator()
        self.ctx.add_command(label="📋  Copy Path",        command=self._copy_path)
        self.ctx.add_command(label="🌐  Open in Browser",  command=self._open_in_browser)

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
        r.bind("<Control-k>", lambda _: self._focus_search())
        r.bind("<Control-K>", lambda _: self._focus_search())

    def _focus_filter(self):
        self.notebook.select(0)
        if self._filter_entry_ref:
            self._filter_entry_ref.focus_set()

    def _focus_search(self):
        self.notebook.select(1)
        try:
            self.search_entry.focus_set()
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
        try:
            icon  = "☀️" if self.current_theme == "light" else "🌙"
            label = "Light" if self.current_theme == "light" else "Dark"
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
    #   AUTH — TOKEN
    # ══════════════════════════════════════════════════════════════════
    def _toggle_token_vis(self):
        self.show_tok = not self.show_tok
        self.token_entry.config(show="" if self.show_tok else "•")
        self.eye_btn.config(text="🙈" if self.show_tok else "👁")

    def _connect_token(self):
        token = self.token_var.get().strip()
        if not token:
            messagebox.showerror(
                "No Token",
                "Please paste your GitHub Personal Access Token.\n\n"
                "To get one:\n  1. github.com → Settings\n"
                "  2. Developer settings → Personal access tokens\n"
                "  3. Generate new token (Classic) with 'repo' scope")
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
                        "Invalid token.\n\nMake sure you copied it correctly —\n"
                        "it should start with 'ghp_' or 'github_pat_'."))
                else:
                    msg = r.json().get("message", "Unknown error")
                    self.root.after(0, lambda: self._on_conn_fail(msg))
            except Exception as e:
                self.root.after(0, self.progress_bar.stop)
                self.root.after(0, lambda: self._on_conn_fail(
                    f"Network error: {e}\n\nCheck your internet connection."))

        threading.Thread(target=_work, daemon=True).start()

    def _on_token_connected(self, data: Dict):
        self.username = data["login"]
        self._show_user_connected(data, mode="token")
        self.connect_btn.config(state=tk.NORMAL, text="⟳  Reconnect")
        self.disconnect_btn.pack(side=tk.LEFT, padx=(4, 0))
        self._save_config()
        self._log_operation(f"[Token] Connected as @{self.username}")
        self._update_search_banner()
        self._load_repos()

    def _on_conn_fail(self, msg: str):
        self.token = None
        self.session.headers.pop("Authorization", None)
        self.connect_btn.config(state=tk.NORMAL, text="  ⚡  Connect  ")
        messagebox.showerror("Connection Failed", msg)
        self._set_status("Connection failed", "err")

    # ══════════════════════════════════════════════════════════════════
    #   AUTH — PUBLIC
    # ══════════════════════════════════════════════════════════════════
    def _connect_public(self):
        raw = self.public_var.get().strip()
        if not raw:
            messagebox.showerror(
                "No Username",
                "Please type a GitHub username or profile URL.\n\n"
                "Examples:\n  • torvalds\n"
                "  • https://github.com/torvalds\n"
                "  • github.com/microsoft")
            return
        username = parse_github_input(raw)
        if not username:
            messagebox.showerror(
                "Invalid Input",
                f"Could not find a valid GitHub username in:\n  {raw}\n\n"
                "Please enter just the username (e.g. 'torvalds') or a GitHub URL.")
            return

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
                r = resilient_get(self.session, f"{self.api_base}/users/{username}",
                                  timeout=12)
                self._parse_rate_limit(r)
                self.root.after(0, self.progress_bar.stop)
                if r.status_code == 200:
                    self.root.after(0, lambda: self._on_public_connected(r.json()))
                elif r.status_code == 404:
                    self.root.after(0, lambda: self._on_pub_fail(
                        f"User '{username}' not found on GitHub.\n\n"
                        "Check the spelling and try again."))
                else:
                    msg = r.json().get("message", "Unknown error")
                    self.root.after(0, lambda: self._on_pub_fail(msg))
            except Exception as e:
                self.root.after(0, self.progress_bar.stop)
                self.root.after(0, lambda: self._on_pub_fail(f"Network error: {e}"))

        threading.Thread(target=_work, daemon=True).start()

    def _on_public_connected(self, data: Dict):
        self.username = data["login"]
        self._show_user_connected(data, mode="public")
        self.public_connect_btn.config(state=tk.NORMAL, text="  🚀  Browse  ")
        self._save_config()
        self._log_operation(f"[Public] Browsing @{self.username}")
        self._update_search_banner()
        self._load_repos()

    def _on_pub_fail(self, msg: str):
        self.public_connect_btn.config(state=tk.NORMAL, text="  🚀  Browse  ")
        messagebox.showerror("Browse Failed", msg)
        self._set_status("Browse failed", "err")

    def _disconnect(self):
        self.token    = None
        self.username = None
        self.session.headers.pop("Authorization", None)
        self.repo_data.clear()
        self.repo_combo["values"] = []
        self.repo_combo.set("")
        self.current_repo      = None
        self.current_repo_full = None
        self.current_path      = ""
        self.tree.delete(*self.tree.get_children())
        self.user_name_lbl.config(text="Not Connected")
        self.user_meta_lbl.config(text="Choose Token or Public mode above")
        self.conn_badge.config(text="")
        self.auth_badge.config(text="")
        self.avatar_lbl.config(text="○")
        self.disconnect_btn.pack_forget()
        self.connect_btn.config(text="  ⚡  Connect  ")
        self.rate_remaining = 60
        self.rate_limit     = 60
        self._update_rate_display()
        self._update_search_banner()
        self._set_status("Disconnected")
        self._log_operation("Disconnected")

    def _update_search_banner(self):
        try:
            C = self.C
            if self.username:
                mode_str = ("🔑 Token (5000 req/hr)" if self.auth_mode == "token"
                            else "👤 Public (60 req/hr)")
                self._banner_lbl.config(
                    text=f"✅  Searching @{self.username}  ·  Mode: {mode_str}  "
                         f"·  Ctrl+K to focus search",
                    bg=C["success_subtle"], fg=C["success"])
                self.search_banner.config(bg=C["success_subtle"])
            else:
                self._banner_lbl.config(
                    text="ℹ️   Connect to a GitHub user first, then search across all their repositories.",
                    bg=C["warning_subtle"], fg=C["warning"])
                self.search_banner.config(bg=C["warning_subtle"])
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════════════
    #   USER CARD
    # ══════════════════════════════════════════════════════════════════
    def _show_user_connected(self, data: Dict = None, mode: str = "token"):
        if data is None:
            return
        C = self.C
        login    = data.get("login", "")
        name     = data.get("name") or login
        repos    = data.get("public_repos", 0)
        followers= data.get("followers", 0)
        bio      = (data.get("bio") or "")[:60]

        self.user_name_lbl.config(text=name, fg=C["fg"])
        self.user_meta_lbl.config(
            text=f"@{login}  ·  {repos} repos  ·  {followers:,} followers",
            fg=C["fg_muted"])
        self.conn_badge.config(text=bio, fg=C["fg_subtle"])

        badge_text  = "🔑  TOKEN MODE"  if mode == "token"  else "👤  PUBLIC MODE"
        badge_color = C["badge_token"]   if mode == "token"  else C["badge_public"]
        self.auth_badge.config(text=badge_text, fg=badge_color)
        self.avatar_lbl.config(text="●", fg=C["success"])
        self._update_rate_display()

    # ══════════════════════════════════════════════════════════════════
    #   REPOS & BRANCHES
    # ══════════════════════════════════════════════════════════════════
    def _load_repos(self):
        if not self.username:
            return
        self._set_status(f"Loading repositories for @{self.username}…")
        self.progress_bar.start()

        def _work():
            try:
                repos = []
                page  = 1
                while True:
                    if self.auth_mode == "token":
                        url = f"{self.api_base}/user/repos"
                    else:
                        url = f"{self.api_base}/users/{self.username}/repos"
                    r = resilient_get(self.session, url,
                                      params={"per_page": 100, "page": page,
                                              "sort": "updated", "type": "all"},
                                      timeout=20)
                    self._parse_rate_limit(r)
                    if r.status_code != 200:
                        break
                    batch = r.json()
                    if not batch:
                        break
                    repos.extend(batch)
                    if len(batch) < 100:
                        break
                    page += 1
                self.root.after(0, lambda: self._on_repos_loaded(repos))
            except Exception as e:
                self.root.after(0, self.progress_bar.stop)
                self.root.after(0, lambda: self._set_status(f"Repos error: {e}", "err"))

        threading.Thread(target=_work, daemon=True).start()

    def _on_repos_loaded(self, repos: List[Dict]):
        self.progress_bar.stop()
        self.repo_data.clear()
        for rd in repos:
            key = rd.get("full_name", rd.get("name", ""))
            self.repo_data[key] = rd
        names = self._build_repo_list_names()
        self.repo_combo["values"] = names
        if names:
            prev = self.current_repo_full
            if prev and prev in names:
                self.repo_combo.set(prev)
            else:
                self.repo_combo.set(names[0])
            self._on_repo_select()
        self._set_status(f"Loaded {len(repos)} repositories", "ok")
        self._log_operation(f"Loaded {len(repos)} repos for @{self.username}")

        self._show_welcome_info()

    def _build_repo_list_names(self) -> List[str]:
        pinned   = [k for k in self.pinned_repos if k in self.repo_data]
        unpinned = [k for k in self.repo_data if k not in pinned]
        return pinned + unpinned

    def _show_welcome_info(self):
        count = len(self.repo_data)
        self._show_info("📦",
                        f"{count} repositories loaded",
                        f"@{self.username}  ·  Select a repository above to explore")

    def _on_repo_select(self, _=None):
        key = self.repo_var.get()
        if not key or key not in self.repo_data:
            return
        rd = self.repo_data[key]
        self.current_repo      = rd.get("name", key.split("/")[-1])
        self.current_repo_full = key
        self.current_path      = ""
        self._update_repo_meta()
        self._load_branches()
        self._log_operation(f"Selected repo: {key}")

    def _update_repo_meta(self):
        key = self.repo_var.get()
        if key not in self.repo_data:
            return
        rd   = self.repo_data[key]
        lang = rd.get("language") or "—"
        stars= rd.get("stargazers_count", 0)
        forks= rd.get("forks_count", 0)
        upd  = relative_time(rd.get("updated_at", ""))
        self.repo_meta_lbl.config(
            text=f"★ {stars:,}  🍴 {forks:,}  {lang}  ·  {upd}")
        self.repo_desc_lbl.config(
            text=(rd.get("description") or "No description")[:120])

    def _load_branches(self):
        if not self.current_repo:
            return

        def _work():
            try:
                r = resilient_get(
                    self.session,
                    f"{self.api_base}/repos/{self.username}/{self.current_repo}/branches",
                    params={"per_page": 100}, timeout=15)
                self._parse_rate_limit(r)
                if r.status_code == 200:
                    branches = [b["name"] for b in r.json()]
                    self.root.after(0, lambda: self._on_branches_loaded(branches))
            except Exception:
                pass

        threading.Thread(target=_work, daemon=True).start()

    def _on_branches_loaded(self, branches: List[str]):
        self.branch_combo["values"] = branches
        rd = self.repo_data.get(self.current_repo_full or "", {})
        default = rd.get("default_branch", "main")
        if default in branches:
            self.branch_var.set(default)
        elif branches:
            self.branch_var.set(branches[0])
        self._load_dir("")

    def _on_branch_select(self, _=None):
        self.current_path = ""
        self._load_dir("")

    # ══════════════════════════════════════════════════════════════════
    #   DIRECTORY NAVIGATION
    # ══════════════════════════════════════════════════════════════════
    def _load_dir(self, path: str):
        if not self.current_repo:
            return
        self.current_path = path
        branch = self.branch_var.get()
        self.path_lbl.config(text=f"/{path}" if path else "/")
        self._show_loading_info()
        self.tree.delete(*self.tree.get_children())
        self.filter_var.set("")

        def _work():
            try:
                r = resilient_get(
                    self.session,
                    f"{self.api_base}/repos/{self.username}/"
                    f"{self.current_repo}/contents/{path}",
                    params={"ref": branch} if branch else {},
                    timeout=20)
                self._parse_rate_limit(r)
                if r.status_code == 200:
                    items = r.json()
                    if not isinstance(items, list):
                        items = [items]
                    self.root.after(0, lambda: self._populate_tree(items))
                elif r.status_code == 404:
                    self.root.after(0, lambda: self._show_info(
                        "⚠️", "Path not found",
                        f"The path '{path}' doesn't exist on branch '{branch}'"))
                else:
                    msg = r.json().get("message", "Error loading directory")
                    self.root.after(0, lambda: self._set_status(msg, "err"))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(str(e), "err"))

        threading.Thread(target=_work, daemon=True).start()

    def _populate_tree(self, items: List[Dict]):
        self.all_items = {"dirs": [], "files": []}
        for item in items:
            if item.get("type") == "dir":
                self.all_items["dirs"].append(item)
            else:
                self.all_items["files"].append(item)
        self._render_tree(self.all_items["dirs"] + self.all_items["files"])
        total = len(items)
        self.file_count_lbl.config(
            text=f"{len(self.all_items['dirs'])}  folders  "
                 f"·  {len(self.all_items['files'])}  files")
        self._set_status(
            f"Loaded {total} item{'s' if total != 1 else ''}"
            f"  ·  {self.current_repo}/{self.current_path or ''}", "ok")
        self.info_frame.place_forget()

    def _render_tree(self, items: List[Dict]):
        self.tree.delete(*self.tree.get_children())
        C = self.C
        for item in items:
            is_dir  = item.get("type") == "dir"
            name    = item.get("name", "")
            size    = item.get("size", 0)
            icon    = "📁" if is_dir else file_icon(name)
            size_str= "—" if is_dir else fmt_size(size)
            kind    = "Folder" if is_dir else "File"
            self.tree.insert("", "end",
                             text=f"  {name}",
                             values=(icon, kind, size_str),
                             tags=("dir" if is_dir else "file",))
        self.tree.tag_configure("dir",  foreground=C["tag_dir"])
        self.tree.tag_configure("file", foreground=C["tag_file"])

    def _show_loading_info(self):
        self._show_info("⏳", "Loading…", "Fetching directory contents from GitHub")

    def _show_info(self, icon: str, main: str, extra: str):
        self.tree.delete(*self.tree.get_children())
        self.info_lbl.config(text=icon)
        self.info_main.config(text=main)
        self.info_extra.config(text=extra)
        self.info_frame.place(relx=0.5, rely=0.5, anchor="center")

    def _on_tree_double(self, _=None):
        sel = self.tree.selection()
        if not sel:
            return
        item = sel[0]
        vals = self.tree.item(item, "values")
        name = self.tree.item(item, "text").strip()
        if vals and vals[1] == "Folder":
            new_path = f"{self.current_path}/{name}" if self.current_path else name
            self._load_dir(new_path)
        else:
            self._preview_selected()

    def _go_home(self):
        if self.current_repo:
            self.current_path = ""
            self._load_dir("")

    def _go_up(self):
        if not self.current_path:
            return
        parent = "/".join(self.current_path.rsplit("/", 1)[:-1])
        self._load_dir(parent)

    def _refresh_dir(self):
        self._load_dir(self.current_path)

    def _apply_filter(self):
        query = self.filter_var.get().lower()
        if not query:
            self._render_tree(self.all_items["dirs"] + self.all_items["files"])
            self.file_count_lbl.config(text="")
            return
        filtered = (
            [i for i in self.all_items["dirs"]  if query in i["name"].lower()] +
            [i for i in self.all_items["files"] if query in i["name"].lower()])
        self._render_tree(filtered)
        self.file_count_lbl.config(
            text=f"Filter: {len(filtered)} match{'es' if len(filtered) != 1 else ''}")

    def _sort_by(self, col: str):
        if self.sort_col == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_col     = col
            self.sort_reverse = False

        def key_fn(item):
            if col == "name": return item.get("name","").lower()
            if col == "kind": return item.get("type","")
            if col == "size": return item.get("size", 0)
            return ""

        dirs  = sorted(self.all_items["dirs"],  key=key_fn, reverse=self.sort_reverse)
        files = sorted(self.all_items["files"], key=key_fn, reverse=self.sort_reverse)
        self._render_tree(dirs + files)

    def _pin_repo(self):
        key = self.repo_var.get()
        if not key:
            return
        if key in self.pinned_repos:
            self.pinned_repos.remove(key)
            self._set_status(f"Unpinned: {key}", "ok")
        else:
            self.pinned_repos.append(key)
            self._set_status(f"Pinned: {key}", "ok")
        names = self._build_repo_list_names()
        self.repo_combo["values"] = names
        self._save_config()

    # ══════════════════════════════════════════════════════════════════
    #   USER-SCOPED SEARCH  — FULLY REDESIGNED v4
    # ══════════════════════════════════════════════════════════════════
    def _do_user_search(self):
        if not self.username:
            messagebox.showwarning(
                "Not Connected",
                "Please connect a GitHub account first.\n\n"
                "You can use either Token mode or Browse Public Profile mode.")
            return
        query = self.usearch_var.get().strip()
        if not query:
            self._set_status("Please enter a search term", "warn")
            return
        if len(query) < 2:
            self._set_status("Search term must be at least 2 characters", "warn")
            return

        # Add to history
        if query not in self._search_history:
            self._search_history.appendleft(query)
        else:
            self._search_history.remove(query)
            self._search_history.appendleft(query)

        scope = self.usearch_scope_var.get()
        self._search_page    = 1
        self._search_results_all = []

        # Clear UI
        for w in self.results_inner.winfo_children():
            w.destroy()
        tk.Label(self.results_inner, text="🔄  Searching…",
                 bg=self.C["bg"], fg=self.C["fg_muted"],
                 font=(FONT_UI, 11)).pack(pady=40)

        self.search_count_lbl.config(text="Searching…")
        self.search_prog_lbl.config(text=f"● {scope} search…")
        self.search_cancel_btn.config(state=tk.NORMAL)
        self.search_go_btn.config(state=tk.DISABLED)
        self.search_cancel.clear()
        self._notebook_select_search()

        def _work():
            try:
                results = []
                if scope == "Repos":
                    results = self._search_user_repos(query)
                elif scope == "Content":
                    results = self._search_user_content(query)
                elif scope == "Files":
                    results = self._search_user_files(query)
                elif scope == "Commits":
                    results = self._search_user_commits(query)
                elif scope == "Topics":
                    results = self._search_user_topics(query)

                if not self.search_cancel.is_set():
                    self.root.after(0, lambda: self._display_search_results(
                        results, scope, query))
            except Exception as e:
                if not self.search_cancel.is_set():
                    self.root.after(0, lambda: self._set_status(
                        f"Search error: {e}", "err"))
                    self.root.after(0, lambda: self.search_prog_lbl.config(text=""))
            finally:
                self.root.after(0, lambda: self.search_cancel_btn.config(
                    state=tk.DISABLED))
                self.root.after(0, lambda: self.search_go_btn.config(
                    state=tk.NORMAL))

        self.search_thread = threading.Thread(target=_work, daemon=True)
        self.search_thread.start()

    def _notebook_select_search(self):
        try:
            self.notebook.select(1)
        except Exception:
            pass

    # ── Search: Repos (name + description + topics + README hint) ──
    def _search_user_repos(self, query: str) -> List[Dict]:
        q_lower = query.lower()
        results = []
        for key, rd in self.repo_data.items():
            name    = rd.get("name", "").lower()
            desc    = (rd.get("description") or "").lower()
            topics  = [t.lower() for t in rd.get("topics", [])]
            lang    = (rd.get("language") or "").lower()
            score   = 0
            score  += score_match(q_lower, name) * 3
            score  += score_match(q_lower, desc) * 1
            if any(q_lower in t for t in topics):
                score += 40
            if q_lower == lang:
                score += 20
            if score > 0:
                results.append({
                    "type": "repo", "key": key, "data": rd, "_score": score
                })
        results.sort(key=lambda x: x["_score"], reverse=True)
        return results

    # ── Search: Content (keywords INSIDE file contents) ────────────
    def _search_user_content(self, query: str) -> List[Dict]:
        """
        Search for a keyword inside file contents using GitHub code search.
        Works for BOTH token and public (unauthenticated) users.
        Requires Accept: application/vnd.github.text-match+json for fragments.
        """
        results = []
        q = f"{query} user:{self.username}"

        headers = {
            "Accept": "application/vnd.github.text-match+json",
        }
        if self.auth_mode == "token" and self.token:
            headers["Authorization"] = f"token {self.token}"

        page     = 1
        per_page = 30
        max_pages = 3  # Fetch up to 3 pages = 90 results

        while page <= max_pages:
            if self.search_cancel.is_set():
                break
            try:
                r = resilient_get(
                    self.session,
                    f"{self.api_base}/search/code",
                    params={"q": q, "per_page": per_page, "page": page},
                    headers=headers,
                    timeout=25)
                self._parse_rate_limit(r)

                if r.status_code == 200:
                    data = r.json()
                    items = data.get("items", [])
                    for item in items:
                        results.append({
                            "type":    "content",
                            "key":     str(id(item)) + str(page),
                            "data":    item,
                            "_score":  100,
                        })
                    if len(items) < per_page:
                        break
                    # GitHub caps code search at 1000 results
                    if data.get("total_count", 0) == 0:
                        break
                    page += 1
                    # Small delay to respect secondary rate limits
                    time.sleep(0.5)

                elif r.status_code == 403:
                    results.append({
                        "type": "error",
                        "key":  "err403",
                        "data": {
                            "message": (
                                "⚠️  Content search requires authentication.\n\n"
                                "Switch to Token mode to search inside file contents.\n"
                                "Get a free token at github.com/settings/tokens")
                        }
                    })
                    break
                elif r.status_code == 422:
                    results.append({
                        "type": "error",
                        "key":  "err422",
                        "data": {
                            "message": (
                                "⚠️  Search term invalid or too short.\n\n"
                                "Try a longer keyword (3+ characters) or use quotes\n"
                                "for exact phrases: \"your phrase here\"")
                        }
                    })
                    break
                elif r.status_code == 429:
                    time.sleep(10)
                    continue
                else:
                    try:
                        msg = r.json().get("message", f"HTTP {r.status_code}")
                    except Exception:
                        msg = f"HTTP {r.status_code}"
                    results.append({
                        "type": "error",
                        "key":  "errmsg",
                        "data": {"message": f"API error: {msg}"}
                    })
                    break
            except Exception as e:
                results.append({
                    "type": "error",
                    "key":  "errnet",
                    "data": {"message": f"Network error: {e}"}
                })
                break

        return results

    # ── Search: Files (filenames across repos) ─────────────────────
    def _search_user_files(self, query: str) -> List[Dict]:
        """
        Search file names across the loaded user's repositories.
        Uses GitHub code search + text-match headers for fragments.
        """
        results = []
        q = f"filename:{query} user:{self.username}"
        headers = {
            "Accept": "application/vnd.github.text-match+json",
        }
        if self.auth_mode == "token" and self.token:
            headers["Authorization"] = f"token {self.token}"

        try:
            r = resilient_get(
                self.session,
                f"{self.api_base}/search/code",
                params={"q": q, "per_page": 50},
                headers=headers,
                timeout=25)
            self._parse_rate_limit(r)

            if r.status_code == 200:
                items = r.json().get("items", [])
                for item in items:
                    results.append({
                        "type":   "file",
                        "key":    str(id(item)),
                        "data":   item,
                        "_score": 100,
                    })
            elif r.status_code == 403:
                results.append({
                    "type": "error", "key": "err403",
                    "data": {"message":
                             "⚠️  File search requires authentication.\n"
                             "Switch to Token mode for file searching."}
                })
            elif r.status_code == 422:
                results.append({
                    "type": "error", "key": "err422",
                    "data": {"message":
                             "⚠️  Search term too short or invalid.\n"
                             "Try a longer filename (3+ chars)."}
                })
        except Exception as e:
            results.append({
                "type": "error", "key": "errnet",
                "data": {"message": f"Network error: {e}"}
            })
        return results

    # ── Search: Commits ────────────────────────────────────────────
    def _search_user_commits(self, query: str) -> List[Dict]:
        """Search commit messages by the loaded user."""
        results = []
        q = f"{query} author:{self.username}"
        headers = {
            "Accept": "application/vnd.github.cloak-preview+json",
        }
        if self.auth_mode == "token" and self.token:
            headers["Authorization"] = f"token {self.token}"

        try:
            r = resilient_get(
                self.session,
                f"{self.api_base}/search/commits",
                params={"q": q, "per_page": 50},
                headers=headers,
                timeout=25)
            self._parse_rate_limit(r)

            if r.status_code == 200:
                items = r.json().get("items", [])
                for item in items:
                    results.append({
                        "type":   "commit",
                        "key":    str(id(item)),
                        "data":   item,
                        "_score": 100,
                    })
            elif r.status_code == 403:
                results.append({
                    "type": "error", "key": "err403",
                    "data": {"message":
                             "⚠️  Commit search requires authentication.\n"
                             "Switch to Token mode."}
                })
            elif r.status_code == 422:
                # Fall back to local repo search
                results = self._search_commits_locally(query)
        except Exception as e:
            results.append({
                "type": "error", "key": "errnet",
                "data": {"message": f"Network error: {e}"}
            })
        return results

    def _search_commits_locally(self, query: str) -> List[Dict]:
        """Fallback: search commit messages within loaded repos."""
        results = []
        q_lower = query.lower()
        repos_to_check = list(self.repo_data.items())[:10]  # Limit to 10

        for key, rd in repos_to_check:
            if self.search_cancel.is_set():
                break
            repo_name = rd.get("name", "")
            try:
                r = resilient_get(
                    self.session,
                    f"{self.api_base}/repos/{self.username}/{repo_name}/commits",
                    params={"per_page": 30},
                    timeout=15)
                if r.status_code == 200:
                    for commit_data in r.json():
                        msg = (commit_data.get("commit", {})
                               .get("message", "")).lower()
                        if q_lower in msg:
                            commit_data["repository"] = {"full_name": key}
                            results.append({
                                "type":   "commit",
                                "key":    str(id(commit_data)),
                                "data":   commit_data,
                                "_score": 100,
                            })
            except Exception:
                pass
        return results

    # ── Search: Topics ──────────────────────────────────────────────
    def _search_user_topics(self, query: str) -> List[Dict]:
        """Filter repos by language or topic tag."""
        q_lower = query.lower()
        results = []
        for key, rd in self.repo_data.items():
            lang    = (rd.get("language") or "").lower()
            topics  = [t.lower() for t in rd.get("topics", [])]
            score   = 0
            if q_lower == lang:          score += 100
            if q_lower in lang:          score += 60
            if q_lower in topics:        score += 80
            if any(q_lower in t for t in topics): score += 40
            if score > 0:
                results.append({
                    "type": "repo", "key": key, "data": rd, "_score": score
                })
        results.sort(key=lambda x: x["_score"], reverse=True)
        return results

    def _cancel_user_search(self):
        self.search_cancel.set()
        self.search_cancel_btn.config(state=tk.DISABLED)
        self.search_go_btn.config(state=tk.NORMAL)
        self.search_prog_lbl.config(text="")
        self._set_status("Search cancelled")

    # ══════════════════════════════════════════════════════════════════
    #   SEARCH RESULT DISPLAY — Rich Cards
    # ══════════════════════════════════════════════════════════════════
    def _display_search_results(self, results: List[Dict], scope: str, query: str):
        self._search_results_all = results
        self._search_page        = 1
        self.search_prog_lbl.config(text="")

        count = len([r for r in results if r.get("type") != "error"])
        errors = [r for r in results if r.get("type") == "error"]

        sort_pref = self.result_sort_var.get()
        if sort_pref == "name":
            self._sort_results_by_name()
        elif sort_pref == "date":
            self._sort_results_by_date()

        self.search_count_lbl.config(
            text=f"{'No' if count == 0 else count} result"
                 f"{'s' if count != 1 else ''}")

        self._set_status(
            f"Found {count} result{'s' if count != 1 else ''}"
            f" for '{query}'  [{scope}]",
            "ok" if count > 0 else "warn")
        self._log_operation(
            f"Search [{scope}] '{query}' → {count} results")

        # Show error banners if any
        if errors:
            for err in errors[:1]:
                msg = err["data"].get("message", "Unknown error")
                self._show_error_banner(msg)
                return

        self._render_results_page()

    def _sort_results_by_name(self):
        def key(r):
            d = r.get("data", {})
            if r["type"] == "repo":    return d.get("name", "").lower()
            if r["type"] in ("content", "file"): return d.get("name", "").lower()
            if r["type"] == "commit":
                return d.get("commit", {}).get("message", "").lower()
            return ""
        self._search_results_all.sort(key=key)

    def _sort_results_by_date(self):
        def key(r):
            d = r.get("data", {})
            if r["type"] == "repo":
                return d.get("updated_at", "") or ""
            if r["type"] == "commit":
                return (d.get("commit", {}).get("author") or {}).get("date", "") or ""
            return ""
        self._search_results_all.sort(key=key, reverse=True)

    def _resort_results(self):
        if not self._search_results_all:
            return
        sort_pref = self.result_sort_var.get()
        if sort_pref == "name":
            self._sort_results_by_name()
        elif sort_pref == "date":
            self._sort_results_by_date()
        # relevance: keep original order
        self._search_page = 1
        self._render_results_page()

    def _show_error_banner(self, msg: str):
        C = self.C
        for w in self.results_inner.winfo_children():
            w.destroy()
        frame = tk.Frame(self.results_inner, bg=C["danger_subtle"],
                         highlightbackground=C["danger"], highlightthickness=1)
        frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(frame, text="⚠️  Search Note",
                 bg=C["danger_subtle"], fg=C["danger"],
                 font=(FONT_UI, 10, "bold"), padx=12, pady=8).pack(anchor=tk.W)
        tk.Label(frame, text=msg,
                 bg=C["danger_subtle"], fg=C["fg"],
                 font=(FONT_UI, 9), padx=12, pady=(0, 10),
                 justify=tk.LEFT, wraplength=600).pack(anchor=tk.W)
        self.search_count_lbl.config(text="")
        self.pager_lbl.config(text="Page 0 / 0")

    def _render_results_page(self):
        C     = self.C
        query = self.usearch_var.get().strip()

        for w in self.results_inner.winfo_children():
            w.destroy()

        data = [r for r in self._search_results_all if r.get("type") != "error"]
        total     = len(data)
        max_page  = max(1, (total + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE)
        page      = min(self._search_page, max_page)
        self._search_page = page

        start = (page - 1) * RESULTS_PER_PAGE
        end   = start + RESULTS_PER_PAGE
        page_items = data[start:end]

        self.pager_lbl.config(text=f"Page {page} / {max_page}")
        self.pager_prev.config(state=tk.NORMAL if page > 1        else tk.DISABLED)
        self.pager_next.config(state=tk.NORMAL if page < max_page else tk.DISABLED)

        if not page_items:
            empty = tk.Frame(self.results_inner, bg=C["bg"])
            empty.pack(pady=40)
            tk.Label(empty, text="🔎  No results found",
                     bg=C["bg"], fg=C["fg_muted"],
                     font=(FONT_TITLE, 13, "bold")).pack()
            tk.Label(empty,
                     text="Try a different keyword or switch search scope",
                     bg=C["bg"], fg=C["fg_subtle"],
                     font=(FONT_UI, 9)).pack(pady=(4, 0))
            return

        for entry in page_items:
            self._render_result_card(entry, query)

        # Scroll to top
        self.results_canvas.yview_moveto(0)

    def _render_result_card(self, entry: Dict, query: str):
        """Render a rich result card in the scrollable results area."""
        C      = self.C
        etype  = entry.get("type", "")
        data   = entry.get("data", {})
        parent = self.results_inner

        card = tk.Frame(parent, bg=C["card"],
                        highlightbackground=C["border"], highlightthickness=1,
                        cursor="hand2")
        card.pack(fill=tk.X, padx=8, pady=3)

        inner = tk.Frame(card, bg=C["card"])
        inner.pack(fill=tk.X, padx=12, pady=10)

        # Left: icon
        icon_col = tk.Frame(inner, bg=C["card"])
        icon_col.pack(side=tk.LEFT, padx=(0, 10))

        if etype == "repo":
            icon_text = "📦"
            badge_text  = "REPO"
            badge_bg    = C["accent_subtle"]
            badge_fg    = C["accent"]
        elif etype in ("content", "file"):
            name = data.get("name", "")
            icon_text = file_icon(name)
            badge_text  = "CONTENT" if etype == "content" else "FILE"
            badge_bg    = C["purple_subtle"]
            badge_fg    = C["purple"]
        elif etype == "commit":
            icon_text = "🕐"
            badge_text  = "COMMIT"
            badge_bg    = C["cyan_subtle"]
            badge_fg    = C["cyan"]
        else:
            icon_text = "📄"
            badge_text  = etype.upper()
            badge_bg    = C["surface2"]
            badge_fg    = C["fg_muted"]

        tk.Label(icon_col, text=icon_text,
                 bg=C["card"], fg=C["fg"],
                 font=(FONT_UI, 18)).pack(pady=4)
        tk.Label(icon_col, text=badge_text,
                 bg=badge_bg, fg=badge_fg,
                 font=(FONT_UI, 6, "bold"), padx=4, pady=1).pack()

        # Right: content
        content_col = tk.Frame(inner, bg=C["card"])
        content_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Header row: name + repo path
        header_row = tk.Frame(content_col, bg=C["card"])
        header_row.pack(fill=tk.X)

        if etype == "repo":
            rd      = data
            name    = rd.get("name", "")
            stars   = rd.get("stargazers_count", 0)
            lang    = rd.get("language") or ""
            upd     = relative_time(rd.get("updated_at", ""))
            desc    = (rd.get("description") or "No description")[:120]
            topics  = rd.get("topics", [])[:5]
            is_priv = rd.get("private", False)

            name_lbl = tk.Label(header_row, text=self._highlight_query(name, query),
                                bg=C["card"], fg=C["accent_hover"],
                                font=(FONT_TITLE, 11, "bold"), cursor="hand2")
            name_lbl.pack(side=tk.LEFT)

            if is_priv:
                tk.Label(header_row, text="🔒",
                         bg=C["card"], fg=C["fg_subtle"],
                         font=(FONT_UI, 9)).pack(side=tk.LEFT, padx=4)

            meta_text = f"  ★{stars:,}"
            if lang:
                meta_text += f"  ·  {lang}"
            meta_text += f"  ·  {upd}"
            tk.Label(header_row, text=meta_text,
                     bg=C["card"], fg=C["fg_muted"],
                     font=(FONT_UI, 8)).pack(side=tk.LEFT, padx=6)

            tk.Label(content_col, text=desc,
                     bg=C["card"], fg=C["fg_muted"],
                     font=(FONT_UI, 9), anchor=tk.W, justify=tk.LEFT).pack(
                fill=tk.X, pady=(2, 0))

            if topics:
                tags_row = tk.Frame(content_col, bg=C["card"])
                tags_row.pack(fill=tk.X, pady=(4, 0))
                for topic in topics:
                    tk.Label(tags_row, text=topic,
                             bg=C["accent_subtle"], fg=C["accent"],
                             font=(FONT_UI, 7), padx=5, pady=1).pack(
                        side=tk.LEFT, padx=(0, 3))

        elif etype in ("content", "file"):
            name    = data.get("name", "")
            path    = data.get("path", "")
            repo    = data.get("repository", {}).get("full_name", "")
            url     = data.get("html_url", "")

            name_lbl = tk.Label(header_row, text=self._highlight_query(name, query),
                                bg=C["card"], fg=C["accent_hover"],
                                font=(FONT_TITLE, 11, "bold"), cursor="hand2")
            name_lbl.pack(side=tk.LEFT)

            tk.Label(header_row,
                     text=f"  in  {repo}",
                     bg=C["card"], fg=C["fg_subtle"],
                     font=(FONT_UI, 8)).pack(side=tk.LEFT)

            if path != name:
                tk.Label(content_col, text=f"📂  {path}",
                         bg=C["card"], fg=C["fg_subtle"],
                         font=(FONT_MONO, 8)).pack(anchor=tk.W, pady=(2, 0))

            # Text matches / fragments
            fragments = data.get("text_matches", [])
            if fragments:
                frag_frame = tk.Frame(content_col,
                                      bg=C["surface2"],
                                      highlightbackground=C["border"],
                                      highlightthickness=1)
                frag_frame.pack(fill=tk.X, pady=(6, 0))
                for frag in fragments[:3]:
                    fragment_text = frag.get("fragment", "").strip()
                    if fragment_text:
                        self._render_fragment(frag_frame, fragment_text, query)

        elif etype == "commit":
            commit  = data.get("commit", {})
            msg     = (commit.get("message", "") or "").split("\n")[0][:100]
            sha     = data.get("sha", "")[:10]
            repo    = data.get("repository", {}).get("full_name", "")
            author  = (commit.get("author") or {}).get("name", "")
            date_str= relative_time((commit.get("author") or {}).get("date", ""))

            msg_lbl = tk.Label(header_row, text=self._highlight_query(msg, query),
                               bg=C["card"], fg=C["fg"],
                               font=(FONT_UI, 10, "bold"))
            msg_lbl.pack(side=tk.LEFT)

            meta = f"  {sha}  ·  {author}  ·  {date_str}"
            if repo:
                meta += f"  ·  {repo}"
            tk.Label(content_col, text=meta,
                     bg=C["card"], fg=C["fg_muted"],
                     font=(FONT_MONO, 8)).pack(anchor=tk.W, pady=(2, 0))

        # Click to select
        def on_click(e=None, ent=entry):
            self._on_card_click(ent)

        def on_enter(e=None):
            card.config(highlightbackground=C["accent"])
        def on_leave(e=None):
            card.config(highlightbackground=C["border"])

        for widget in [card, inner, content_col, header_row]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>",    on_enter)
            widget.bind("<Leave>",    on_leave)
        if 'name_lbl' in dir():
            try:
                name_lbl.bind("<Button-1>", on_click)
                name_lbl.bind("<Enter>",    on_enter)
                name_lbl.bind("<Leave>",    on_leave)
            except Exception:
                pass

    def _highlight_query(self, text: str, query: str) -> str:
        """For now return text as-is; highlighting applied via tag_configure in Text widgets."""
        return text

    def _render_fragment(self, parent, fragment: str, query: str):
        """Render a code fragment with keyword highlighting."""
        C = self.C
        frag_txt = tk.Text(parent, wrap=tk.WORD,
                           bg=C["surface2"], fg=C["fg_muted"],
                           font=(FONT_MONO, 8), relief=tk.FLAT,
                           highlightthickness=0, height=3,
                           padx=8, pady=4, state=tk.NORMAL)
        frag_txt.pack(fill=tk.X, padx=0, pady=0)
        frag_txt.insert("1.0", fragment)

        # Highlight matching keywords
        frag_txt.tag_configure("highlight",
                               background=C["highlight_bg"],
                               foreground=C["highlight_fg"],
                               font=(FONT_MONO, 8, "bold"))
        try:
            q = query.lower()
            content = fragment.lower()
            start = 0
            while True:
                idx = content.find(q, start)
                if idx == -1:
                    break
                start_idx = f"1.0 + {idx} chars"
                end_idx   = f"1.0 + {idx + len(q)} chars"
                frag_txt.tag_add("highlight", start_idx, end_idx)
                start = idx + 1
        except Exception:
            pass

        frag_txt.config(state=tk.DISABLED)

    def _on_card_click(self, entry: Dict):
        """Show details for a clicked result card."""
        C     = self.C
        etype = entry.get("type", "")
        data  = entry.get("data", {})

        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete("1.0", tk.END)

        # Configure tags
        self.detail_text.tag_configure("heading",
                                       font=(FONT_TITLE, 11, "bold"),
                                       foreground=C["accent_hover"])
        self.detail_text.tag_configure("key",
                                       font=(FONT_MONO, 8, "bold"),
                                       foreground=C["fg_subtle"])
        self.detail_text.tag_configure("value",
                                       font=(FONT_UI, 9),
                                       foreground=C["fg"])
        self.detail_text.tag_configure("fragment",
                                       font=(FONT_MONO, 8),
                                       foreground=C["fg_muted"],
                                       background=C["surface2"])
        self.detail_text.tag_configure("highlight",
                                       background=C["highlight_bg"],
                                       foreground=C["highlight_fg"],
                                       font=(FONT_MONO, 8, "bold"))
        self.detail_text.tag_configure("url",
                                       foreground=C["accent"],
                                       font=(FONT_UI, 8))

        def row(k, v):
            self.detail_text.insert(tk.END, f"{k:<14}", "key")
            self.detail_text.insert(tk.END, f"{v}\n",   "value")

        query = self.usearch_var.get().strip().lower()

        if etype == "repo":
            rd   = data
            url  = rd.get("html_url", "")
            self.detail_text.insert(tk.END, f"  {rd.get('name','')}\n\n", "heading")
            row("Owner",      rd.get("owner", {}).get("login", ""))
            row("Stars",      f"{rd.get('stargazers_count',0):,}")
            row("Forks",      f"{rd.get('forks_count',0):,}")
            row("Language",   rd.get("language") or "—")
            row("Issues",     f"{rd.get('open_issues_count',0):,}")
            row("Size",       fmt_size((rd.get("size", 0) or 0) * 1024))
            row("Private",    "Yes" if rd.get("private") else "No")
            row("Updated",    relative_time(rd.get("updated_at", "")))
            row("Created",    relative_time(rd.get("created_at", "")))
            topics = rd.get("topics", [])
            if topics:
                row("Topics", ", ".join(topics))
            self.detail_text.insert(tk.END, "\nDescription\n", "key")
            self.detail_text.insert(tk.END,
                f"  {(rd.get('description') or 'No description')}\n", "value")
            self.detail_text.insert(tk.END, "\nURL\n", "key")
            self.detail_text.insert(tk.END, f"  {url}\n", "url")
            self.det_open_btn.config(command=lambda u=url: webbrowser.open(u))
            key = entry.get("key", "")
            def _nav(k=key):
                if k in self.repo_data:
                    self.repo_combo.set(k)
                    self._on_repo_select()
                    self.notebook.select(0)
            self.det_nav_btn.config(command=_nav, text="📁  Open in Explorer")

        elif etype in ("content", "file"):
            name     = data.get("name", "")
            path     = data.get("path", "")
            repo     = data.get("repository", {}).get("full_name", "")
            url      = data.get("html_url", "")
            lang     = data.get("language", "")
            self.detail_text.insert(tk.END, f"  {name}\n\n", "heading")
            row("Repository", repo)
            row("Path",       path)
            if lang:
                row("Language", lang)
            row("URL",        url)

            fragments = data.get("text_matches", [])
            if fragments:
                self.detail_text.insert(tk.END, "\nMatched Fragments\n", "key")
                for frag in fragments[:5]:
                    text = frag.get("fragment", "").strip()
                    if text:
                        self.detail_text.insert(tk.END, "\n")
                        start_pos = self.detail_text.index(tk.INSERT)
                        self.detail_text.insert(tk.END, f"{text}\n", "fragment")
                        end_pos = self.detail_text.index(tk.INSERT)
                        # Highlight query in fragment
                        try:
                            frag_lower = text.lower()
                            base_line  = int(start_pos.split(".")[0])
                            offset = 0
                            while True:
                                idx = frag_lower.find(query, offset)
                                if idx == -1:
                                    break
                                si = f"{base_line}.{idx}"
                                ei = f"{base_line}.{idx + len(query)}"
                                try:
                                    self.detail_text.tag_add("highlight", si, ei)
                                except Exception:
                                    pass
                                offset = idx + 1
                        except Exception:
                            pass

            self.det_open_btn.config(command=lambda u=url: webbrowser.open(u))
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
            self.det_nav_btn.config(command=_nav_file, text="📁  Navigate to File")

        elif etype == "commit":
            commit = data.get("commit", {})
            msg    = commit.get("message", "")
            sha    = data.get("sha", "")
            url    = data.get("html_url", "")
            author = commit.get("author") or {}
            repo   = data.get("repository", {}).get("full_name", "")

            self.detail_text.insert(tk.END, f"  {msg[:60]}…\n\n", "heading")
            row("SHA",        sha[:12])
            row("Author",     author.get("name", "—"))
            row("Email",      author.get("email", "—"))
            row("Date",       relative_time(author.get("date", "")))
            row("Repository", repo)
            self.detail_text.insert(tk.END, "\nFull Message\n", "key")
            self.detail_text.insert(tk.END, f"  {msg}\n", "value")
            self.detail_text.insert(tk.END, "\nURL\n", "key")
            self.detail_text.insert(tk.END, f"  {url}\n", "url")
            self.det_open_btn.config(command=lambda u=url: webbrowser.open(u))
            self.det_nav_btn.config(command=lambda: None,
                                    text="🕐  (commit — no navigation)")

        self.detail_text.config(state=tk.DISABLED)

    # ══════════════════════════════════════════════════════════════════
    #   COMMITS TAB LOGIC
    # ══════════════════════════════════════════════════════════════════
    def _load_commits(self):
        if not self.current_repo:
            messagebox.showwarning("GitView", "Please select a repository first.")
            return
        author = self.commit_author_var.get().strip()
        path   = self.commit_path_var.get().strip()
        params = {"per_page": 60}
        if author: params["author"] = author
        if path:   params["path"]   = path

        self.commit_load_btn.config(state=tk.DISABLED, text="Loading…")
        self.commits_tree.delete(*self.commits_tree.get_children())
        self._commits_data.clear()

        def _work():
            try:
                r = resilient_get(
                    self.session,
                    f"{self.api_base}/repos/{self.username}/"
                    f"{self.current_repo}/commits",
                    params=params, timeout=20)
                self._parse_rate_limit(r)
                if r.status_code == 200:
                    self.root.after(0, lambda: self._populate_commits(r.json()))
                else:
                    msg = r.json().get("message", "Error loading commits")
                    self.root.after(0, lambda: self._set_status(msg, "err"))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(str(e), "err"))
            finally:
                self.root.after(0, lambda: self.commit_load_btn.config(
                    state=tk.NORMAL, text="  🕐  Load Commits  "))

        threading.Thread(target=_work, daemon=True).start()

    def _load_commits_quick(self):
        if not self.current_repo:
            messagebox.showwarning("GitView", "Please select a repository first.")
            return
        self.notebook.select(2)
        self._load_commits()

    def _populate_commits(self, commits: List[Dict]):
        self.commits_tree.delete(*self.commits_tree.get_children())
        self._commits_data.clear()
        for c in commits:
            sha    = c.get("sha", "")[:10]
            commit = c.get("commit", {})
            msg    = (commit.get("message", "") or "").split("\n")[0][:80]
            author = (commit.get("author") or {}).get("name", "")
            date   = relative_time((commit.get("author") or {}).get("date", ""))
            iid    = sha
            self.commits_tree.insert("", "end", iid=iid,
                                     text=f"  {msg}",
                                     values=(sha, author, date))
            self._commits_data[iid] = c
        count = len(commits)
        self.commit_count_lbl.config(text=f"{count} commit{'s' if count != 1 else ''}")
        self._set_status(f"Loaded {count} commits", "ok")

    def _on_commit_select(self, _=None):
        sel = self.commits_tree.selection()
        if not sel:
            return
        c = self._commits_data.get(sel[0], {})
        self.commit_detail.config(state=tk.NORMAL)
        self.commit_detail.delete("1.0", tk.END)
        commit = c.get("commit", {})
        author = commit.get("author") or {}
        sha    = c.get("sha", "")
        url    = c.get("html_url", "")
        self.commit_detail.insert(tk.END,
            f"SHA:    {sha[:12]}\n"
            f"Author: {author.get('name','—')}\n"
            f"Email:  {author.get('email','—')}\n"
            f"Date:   {relative_time(author.get('date',''))}\n\n"
            f"── Message ─────────────────────\n"
            f"{commit.get('message','')}\n\n"
            f"── Files changed ───────────────\n"
        )
        files = c.get("files", [])
        if files:
            for f in files:
                self.commit_detail.insert(
                    tk.END,
                    f"  {f.get('status','?')[0].upper()}  {f.get('filename','')}\n")
        else:
            self.commit_detail.insert(tk.END, "  (load commit URL for file details)\n")
        self.commit_detail.config(state=tk.DISABLED)
        self.commit_open_btn.config(command=lambda u=url: webbrowser.open(u))
        self.commit_copy_sha.config(command=lambda s=sha: (
            self.root.clipboard_clear(),
            self.root.clipboard_append(s),
            self._set_status(f"Copied SHA: {s[:12]}", "ok")))

    def _on_commit_open(self, _=None):
        sel = self.commits_tree.selection()
        if not sel:
            return
        c   = self._commits_data.get(sel[0], {})
        url = c.get("html_url", "")
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
                    self.root.after(0, lambda: self._set_status(
                        f"Preview: {name}", "ok"))
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
        win.geometry("1060x740")
        win.configure(bg=C["bg"])
        self._preview_windows.append(win)
        win.protocol("WM_DELETE_WINDOW",
                     lambda: (self._preview_windows.remove(win)
                              if win in self._preview_windows else None,
                              win.destroy()))

        tk.Frame(win, bg=C["accent"], height=2).pack(fill=tk.X)

        hdr = tk.Frame(win, bg=C["surface"], height=46)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        hdr_inner = tk.Frame(hdr, bg=C["surface"])
        hdr_inner.pack(fill=tk.BOTH, expand=True, padx=14)

        tk.Label(hdr_inner, text=f"{file_icon(name)}  {name}",
                 bg=C["surface"], fg=C["fg"],
                 font=(FONT_TITLE, 11, "bold")).pack(side=tk.LEFT, pady=8)
        tk.Label(hdr_inner,
                 text=f"  ·  {size}  ·  {lang.capitalize()}  ·  {self.current_repo}",
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

        txt = tk.Text(code_f, wrap=tk.NONE,
                      bg=C["surface"], fg=C["fg"],
                      font=(FONT_MONO, 10), relief=tk.FLAT,
                      highlightthickness=0, insertbackground=C["fg"],
                      selectbackground=C["tree_select"],
                      padx=12, pady=8)
        vsb = ttk.Scrollbar(code_f, orient=tk.VERTICAL,   command=txt.yview)
        hsb = ttk.Scrollbar(win,    orient=tk.HORIZONTAL,  command=txt.xview)

        def sync_scroll(*args):
            txt.yview(*args)
            ln.yview(*args)

        vsb.config(command=sync_scroll)
        txt.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        ln.configure(yscrollcommand=vsb.set)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        txt.insert("1.0", text)
        txt.config(state=tk.DISABLED)
        SyntaxHighlighter.apply(txt, lang, C)

    # ══════════════════════════════════════════════════════════════════
    #   DOWNLOAD
    # ══════════════════════════════════════════════════════════════════
    def _download_selected(self):
        if not self.current_repo:
            messagebox.showwarning("GitView", "Please select a repository first.")
            return
        sel   = self.tree.selection()
        items = []
        for iid in sel:
            vals = self.tree.item(iid, "values")
            name = self.tree.item(iid, "text").strip()
            if vals and vals[1] == "File":
                path = f"{self.current_path}/{name}" if self.current_path else name
                items.append((name, path))
        if not items:
            messagebox.showinfo("GitView", "Select one or more files to download.")
            return
        dest = filedialog.askdirectory(title="Choose Download Destination")
        if not dest:
            return
        self._start_download(items, dest)

    def _download_single_file(self, name: str):
        path = f"{self.current_path}/{name}" if self.current_path else name
        dest = filedialog.askdirectory(title="Choose Download Destination")
        if not dest:
            return
        self._start_download([(name, path)], dest)

    def _start_download(self, items: List[Tuple[str, str]], dest: str):
        self._set_status(f"Downloading {len(items)} file(s)…")
        self.progress_bar.start()
        total  = len(items)
        branch = self.branch_var.get()

        def _work():
            done   = 0
            errors = []
            for name, path in items:
                try:
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
                "Read Only Mode",
                "You are browsing a public profile — uploading is not available.\n\n"
                "To upload or edit:\n"
                "  1. Switch to 'Token Mode'\n"
                "  2. Connect with a GitHub Personal Access Token\n"
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
            "Commit Message",
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
                self.root.after(0, self.progress_bar.stop)
                if r.status_code in (200, 201):
                    self.root.after(0, lambda: self._set_status(
                        f"Uploaded {name}", "ok"))
                    self.root.after(0, lambda: self._load_dir(self.current_path))
                    self.root.after(0, lambda: self._log_operation(
                        f"Uploaded {name}"))
                else:
                    err = r.json().get("message", "Upload failed")
                    self.root.after(0, lambda: self._set_status(err, "err"))
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
        for root_dir, _, fnames in os.walk(folder):
            for fn in fnames:
                fp  = os.path.join(root_dir, fn)
                rel = os.path.relpath(fp, folder).replace("\\", "/")
                files.append((fp, rel))
        if not files:
            messagebox.showinfo("GitView", "No files found in that folder.")
            return
        commit_msg = simpledialog.askstring(
            "Commit Message",
            f"Commit message for uploading {len(files)} file(s):",
            initialvalue=f"Upload folder {os.path.basename(folder)} via GitView",
            parent=self.root)
        if not commit_msg:
            return
        self._set_status(f"Uploading {len(files)} file(s)…")
        self.progress_bar.start()
        total = len(files)

        def _work():
            done   = 0
            errors = []
            branch = self.branch_var.get()
            for fp, rel in files:
                try:
                    with open(fp, "rb") as fh:
                        content = base64.b64encode(fh.read()).decode()
                    api_path = (f"{self.current_path}/{rel}"
                                if self.current_path else rel)
                    payload  = {"message": commit_msg, "content": content,
                                "branch": branch}
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
                        self.root.after(0, lambda d=done, t=total:
                                        self.progress_var.set(
                                            f"Uploaded {d}/{t}…"))
                    else:
                        errors.append(rel)
                except Exception as e:
                    errors.append(f"{rel}: {e}")
            self.root.after(0, self.progress_bar.stop)
            if done == total:
                self.root.after(0, lambda: self._set_status(
                    f"Uploaded {done}/{total} files", "ok"))
                self.root.after(0, lambda: self._load_dir(self.current_path))
            else:
                msg = f"Uploaded {done}/{total}.  Errors: {', '.join(errors[:5])}"
                self.root.after(0, lambda: messagebox.showwarning("GitView", msg))
            self.root.after(0, lambda: self._log_operation(
                f"Folder upload: {done}/{total}"))

        threading.Thread(target=_work, daemon=True).start()

    def _create_file_dialog(self):
        if not self._check_write_access():
            return
        if not self.current_repo:
            messagebox.showwarning("GitView", "Please select a repository first.")
            return
        fname = simpledialog.askstring(
            "New File",
            "Enter new file name (include extension):",
            parent=self.root)
        if not fname:
            return
        content_str = simpledialog.askstring(
            "File Content",
            f"Initial content for '{fname}' (can be empty):",
            parent=self.root) or ""
        commit_msg = simpledialog.askstring(
            "Commit Message",
            f"Commit message for creating '{fname}':",
            initialvalue=f"Create {fname} via GitView",
            parent=self.root)
        if not commit_msg:
            return
        api_path = f"{self.current_path}/{fname}" if self.current_path else fname
        branch   = self.branch_var.get()
        payload  = {
            "message": commit_msg,
            "content": base64.b64encode(content_str.encode()).decode(),
            "branch":  branch,
        }
        self._set_status(f"Creating {fname}…")
        self.progress_bar.start()

        def _work():
            try:
                r = self.session.put(
                    f"{self.api_base}/repos/{self.username}/"
                    f"{self.current_repo}/contents/{api_path}",
                    json=payload, timeout=20)
                self._parse_rate_limit(r)
                self.root.after(0, self.progress_bar.stop)
                if r.status_code in (200, 201):
                    self.root.after(0, lambda: self._set_status(
                        f"Created {fname}", "ok"))
                    self.root.after(0, lambda: self._load_dir(self.current_path))
                    self.root.after(0, lambda: self._log_operation(
                        f"Created {fname}"))
                else:
                    err = r.json().get("message", "Create failed")
                    self.root.after(0, lambda: self._set_status(err, "err"))
            except Exception as e:
                self.root.after(0, self.progress_bar.stop)
                self.root.after(0, lambda: self._set_status(str(e), "err"))

        threading.Thread(target=_work, daemon=True).start()

    def _create_folder_dialog(self):
        if not self._check_write_access():
            return
        if not self.current_repo:
            messagebox.showwarning("GitView", "Please select a repository first.")
            return
        fname = simpledialog.askstring(
            "New Folder",
            "Enter folder name:\n(A .gitkeep file will be created inside it)",
            parent=self.root)
        if not fname:
            return
        api_path = (f"{self.current_path}/{fname}/.gitkeep"
                    if self.current_path else f"{fname}/.gitkeep")
        branch  = self.branch_var.get()
        payload = {
            "message": f"Create folder {fname} via GitView",
            "content": base64.b64encode(b"").decode(),
            "branch":  branch,
        }
        def _work():
            try:
                r = self.session.put(
                    f"{self.api_base}/repos/{self.username}/"
                    f"{self.current_repo}/contents/{api_path}",
                    json=payload, timeout=20)
                self._parse_rate_limit(r)
                if r.status_code in (200, 201):
                    self.root.after(0, lambda: self._set_status(
                        f"Created folder {fname}", "ok"))
                    self.root.after(0, lambda: self._load_dir(self.current_path))
                else:
                    err = r.json().get("message", "Failed to create folder")
                    self.root.after(0, lambda: self._set_status(err, "err"))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(str(e), "err"))
        threading.Thread(target=_work, daemon=True).start()

    def _delete_selected(self):
        if not self._check_write_access():
            return
        sel = self.tree.selection()
        if not sel:
            return
        names = [self.tree.item(i, "text").strip() for i in sel]
        if not messagebox.askyesno(
                "Confirm Delete",
                f"Delete {len(names)} item(s)?\n  " +
                "\n  ".join(names[:5]) +
                ("\n  …" if len(names) > 5 else "") +
                "\n\nThis cannot be undone."):
            return
        branch = self.branch_var.get()

        def _work():
            for iid in sel:
                name = self.tree.item(iid, "text").strip()
                path = f"{self.current_path}/{name}" if self.current_path else name
                try:
                    r_get = self.session.get(
                        f"{self.api_base}/repos/{self.username}/"
                        f"{self.current_repo}/contents/{path}",
                        params={"ref": branch}, timeout=10)
                    if r_get.status_code == 200:
                        sha = r_get.json().get("sha", "")
                        r_del = self.session.delete(
                            f"{self.api_base}/repos/{self.username}/"
                            f"{self.current_repo}/contents/{path}",
                            json={"message": f"Delete {name} via GitView",
                                  "sha": sha, "branch": branch},
                            timeout=20)
                        self._parse_rate_limit(r_del)
                        if r_del.status_code in (200, 204):
                            self.root.after(0, lambda n=name:
                                            self._set_status(f"Deleted {n}", "ok"))
                            self.root.after(0, lambda n=name:
                                            self._log_operation(f"Deleted {n}"))
                except Exception as e:
                    self.root.after(0, lambda err=e:
                                    self._set_status(str(err), "err"))
            self.root.after(0, lambda: self._load_dir(self.current_path))

        threading.Thread(target=_work, daemon=True).start()

    def _rename_selected(self):
        messagebox.showinfo(
            "GitView — Rename",
            "GitHub API does not support direct rename.\n\n"
            "To rename:\n"
            "  1. Download the file\n"
            "  2. Delete the original\n"
            "  3. Upload with the new name")

    def _copy_path(self):
        sel = self.tree.selection()
        if not sel:
            return
        name = self.tree.item(sel[0], "text").strip()
        path = f"{self.current_path}/{name}" if self.current_path else name
        self.root.clipboard_clear()
        self.root.clipboard_append(path)
        self._set_status(f"Copied path: {path}", "ok")

    def _open_in_browser(self):
        if not self.current_repo or not self.username:
            return
        url = f"https://github.com/{self.username}/{self.current_repo}"
        if self.current_path:
            branch = self.branch_var.get()
            url += f"/tree/{branch}/{self.current_path}"
        webbrowser.open(url)

    # ══════════════════════════════════════════════════════════════════
    #   CREATE REPO
    # ══════════════════════════════════════════════════════════════════
    def _create_repo_dialog(self):
        if not self._check_write_access():
            return
        name = simpledialog.askstring(
            "New Repository",
            "Repository name (no spaces — use hyphens):",
            parent=self.root)
        if not name:
            return
        desc = simpledialog.askstring(
            "Description (optional)",
            "Short description of your repository:",
            parent=self.root) or ""
        is_private = messagebox.askyesno(
            "Visibility",
            "Make this repository private?\n\n"
            "  Yes = private (only you can see)\n"
            "  No  = public  (anyone can see)")
        payload = {
            "name":        name,
            "description": desc,
            "private":     is_private,
            "auto_init":   True,
        }

        def _work():
            try:
                r = self.session.post(
                    f"{self.api_base}/user/repos",
                    json=payload, timeout=20)
                self._parse_rate_limit(r)
                if r.status_code == 201:
                    self.root.after(0, lambda: self._set_status(
                        f"Created repo: {name}", "ok"))
                    self.root.after(0, self._load_repos)
                    self.root.after(0, lambda: self._log_operation(
                        f"Created repo: {name}"))
                else:
                    err = r.json().get("message", "Create failed")
                    self.root.after(0, lambda: messagebox.showerror(
                        "Create Failed", err))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(str(e), "err"))

        threading.Thread(target=_work, daemon=True).start()

    # ══════════════════════════════════════════════════════════════════
    #   CONFIG PERSISTENCE
    # ══════════════════════════════════════════════════════════════════
    def _save_config(self):
        try:
            cfg = {
                "auth_mode":   self.auth_mode,
                "username":    self.username or "",
                "theme":       self.current_theme,
                "pinned":      self.pinned_repos,
                "history":     list(self._search_history),
            }
            with open(CONFIG_FILE, "w") as fh:
                json.dump(cfg, fh, indent=2)
        except Exception:
            pass

    def _load_saved_config(self):
        try:
            if not CONFIG_FILE.exists():
                return
            with open(CONFIG_FILE) as fh:
                cfg = json.load(fh)
            self.pinned_repos    = cfg.get("pinned", [])
            history              = cfg.get("history", [])
            self._search_history = deque(history, maxlen=30)
            theme = cfg.get("theme", "dark")
            if theme != self.current_theme:
                self._toggle_theme()
                return
            mode = cfg.get("auth_mode", "token")
            user = cfg.get("username", "")
            if mode == "token":
                self._switch_to_token()
            elif mode == "public" and user:
                self._switch_to_public()
                self.public_var.set(user)
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════════════
    #   RATE LIMIT PARSER
    # ══════════════════════════════════════════════════════════════════
    def _parse_rate_limit(self, r: requests.Response):
        try:
            self.rate_remaining = int(r.headers.get("X-RateLimit-Remaining", self.rate_remaining))
            self.rate_limit     = int(r.headers.get("X-RateLimit-Limit",     self.rate_limit))
            self.rate_reset_ts  = float(r.headers.get("X-RateLimit-Reset",   self.rate_reset_ts))
            self.root.after(0, self._update_rate_display)
        except Exception:
            pass

    def _update_rate_display(self):
        try:
            rem    = self.rate_remaining
            lim    = self.rate_limit
            pct    = (rem / lim * 100) if lim else 100
            C      = self.C
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
            self.progress_var.set(msg if level in ("ok","err") else msg)
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════════════
    #   HELP WINDOW
    # ══════════════════════════════════════════════════════════════════
    def _show_help(self):
        C = self.C
        win = tk.Toplevel(self.root)
        win.title("GitView v4 — Help & Quick Start")
        win.geometry("760x680")
        win.configure(bg=C["bg"])

        tk.Frame(win, bg=C["accent"], height=2).pack(fill=tk.X)
        hdr = tk.Frame(win, bg=C["surface"], height=46)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="❓  GitView v4 — Help & Quick Start",
                 bg=C["surface"], fg=C["fg"],
                 font=(FONT_TITLE, 12, "bold")).pack(side=tk.LEFT, padx=16, pady=12)

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
{'─'*66}

👋  GETTING STARTED
   Two ways to connect:

   ① 🔑  TOKEN MODE  (full access, 5000 req/hr)
      • github.com → Settings → Developer settings
        → Personal access tokens → Generate new token (Classic)
      • Tick 'repo' scope, generate, copy, paste here → Connect
      • Unlock: content search, file search, commit search, upload

   ② 👤  BROWSE PUBLIC  (no account needed, 60 req/hr)
      • Type any GitHub username (e.g. torvalds) → Browse
      • All public repos instantly accessible
      • Repo search and topics filter still work

📁  EXPLORER TAB
   • Pick a repo from REPOSITORY dropdown
   • Pick a branch in BRANCH
   • Double-click 📁 folder to enter it
   • Double-click 📄 file to preview with syntax highlighting
   • Type in 🔍 filter box to instantly find files  [Ctrl+F]
   • Click column headers to sort  ·  right-click for context menu
   • Home = root  ·  Backspace = go up

🔍  SEARCH TAB  (NEW v4 — SCOPED TO LOADED USER)
   ★ Ctrl+K anywhere to focus search

   📦 REPOS    — Search repository names, descriptions, topics
   📄 CONTENT  — ★ NEW: Find keywords INSIDE file contents
                  Works best with Token mode
                  Shows matched code fragments with highlighting
   🗂 FILES    — Search file names across all repos  (needs token)
   🕐 COMMITS  — Search commit messages  (needs token or local scan)
   🏷 TOPICS   — Filter repos by programming language or topic tag

   • Results appear as rich cards with context snippets
   • Click any card to see full details in the side panel
   • Pagination: 20 results per page, navigate with Prev/Next
   • Sort by: Relevance, Name, or Date
   • Press ↓ in the search box or click 🕐 History to see recent searches

📥  DOWNLOADING
   • Select files → right-click → Download
   • Ctrl+D for selected files
   • Operations tab → Download Entire Repo (opens GitHub .zip download)

📤  UPLOADING  (token mode only)
   • Ctrl+U = upload file  ·  Ctrl+N = create new file
   • Operations tab for folder upload

⌨️  KEYBOARD SHORTCUTS
   Ctrl+K   Focus search box         F5      Refresh repos
   Ctrl+F   Focus file filter        F2      Rename
   Ctrl+D   Download selection       Del     Delete selected
   Ctrl+U   Upload file              Space   Preview file
   Ctrl+N   New file                 Home    Go to root
                                     Backspace  Go up

🎨  TIPS
   • 🌙/☀️  Theme button — toggle dark/light mode
   • API badge (top right) shows remaining API calls
   • Green ≥40% · Yellow 15-40% · Red <15%

{'─'*66}
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
        make_btn(bot, "🔗  LinkedIn",
                 lambda: webbrowser.open(AUTHOR_LI_URL),
                 style="accent", C=C).pack(side=tk.LEFT, padx=12, pady=6)
        make_btn(bot, "⭐  Star on GitHub",
                 lambda: webbrowser.open(GITHUB_URL),
                 style="ghost", C=C).pack(side=tk.LEFT, padx=(0, 8), pady=6)
        make_btn(bot, "🔑  Get Token",
                 lambda: webbrowser.open("https://github.com/settings/tokens/new"),
                 style="ghost", C=C).pack(side=tk.LEFT, padx=(0, 8), pady=6)


# ══════════════════════════════════════════════════════════════════════════
#   ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    try:
        root.iconbitmap(default="gitview.ico")
    except Exception:
        pass

    app = GitView(root)  # noqa: F841

    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth()  - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()