#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  GitView v5.0 — Enterprise GitHub Intelligence Platform     ║
║  Author : Ali Essam  ·  Egypt 🇪🇬                          ║
║  GitHub : github.com/dragonked2/gitview  ·  MIT License    ║
╚══════════════════════════════════════════════════════════════╝
"""
import warnings, os, re, json, base64, threading, time, webbrowser
from pathlib import Path
from datetime import datetime, timezone
from collections import deque
from typing import Dict, List, Any, Optional, Tuple, Callable
warnings.filterwarnings("ignore")

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import requests
try:
    import urllib3; urllib3.disable_warnings()
except Exception:
    pass

# ── Design System ──────────────────────────────────────────────────────────
DARK: Dict[str, str] = {
    "bg":"#070b10","surface":"#0d1117","surface2":"#161b22","surface3":"#1c2431",
    "card":"#111820","border":"#21262d","border_bright":"#30363d",
    "fg":"#e6edf3","fg_muted":"#8b949e","fg_subtle":"#484f58",
    "accent":"#1f6feb","accent_hover":"#388bfd","accent_subtle":"#0c2d6b","accent_glow":"#163359",
    "success":"#3fb950","success_subtle":"#0a2213",
    "warning":"#e3b341","warning_subtle":"#272115",
    "danger":"#f85149","danger_subtle":"#300a0a",
    "purple":"#bc8cff","purple_subtle":"#1e1340",
    "cyan":"#39d0d8","cyan_subtle":"#0c2e31",
    "orange":"#f0883e","pink":"#ff7b72",
    "tree_select":"#0d2645","entry_bg":"#010409","entry_border":"#30363d",
    "tag_dir":"#58a6ff","tag_file":"#e6edf3",
    "title_bar":"#040811","status_bar":"#040811",
    "scrollbar":"#21262d","scrollbar_hover":"#30363d",
    "rate_ok":"#3fb950","rate_warn":"#e3b341","rate_low":"#f85149",
    "badge_token":"#1a7f37","badge_public":"#9a3412",
    "hl_bg":"#2d3b1a","hl_fg":"#7ee787",
    "diff_add":"#0a2213","diff_add_fg":"#3fb950",
    "diff_del":"#300a0a","diff_del_fg":"#f85149",
    "diff_hunk":"#0c2d6b","diff_hunk_fg":"#388bfd",
    "syn_kw":"#ff7b72","syn_str":"#a5d6ff","syn_cmt":"#6e7681",
    "syn_num":"#79c0ff","syn_func":"#d2a8ff","syn_deco":"#ffa657","syn_builtin":"#79c0ff",
}
LIGHT: Dict[str, str] = {
    "bg":"#f0f2f5","surface":"#ffffff","surface2":"#f6f8fa","surface3":"#eaeef2",
    "card":"#fafbfc","border":"#d0d7de","border_bright":"#b0bac4",
    "fg":"#1f2328","fg_muted":"#57606a","fg_subtle":"#9ea8b3",
    "accent":"#0969da","accent_hover":"#0550ae","accent_subtle":"#dbeafe","accent_glow":"#cce5ff",
    "success":"#1a7f37","success_subtle":"#d1f8dc",
    "warning":"#9a6700","warning_subtle":"#fff8c5",
    "danger":"#cf222e","danger_subtle":"#ffebe9",
    "purple":"#8250df","purple_subtle":"#f3f0ff",
    "cyan":"#0969da","cyan_subtle":"#ddf4ff",
    "orange":"#bc4c00","pink":"#a40e26",
    "tree_select":"#dbeafe","entry_bg":"#ffffff","entry_border":"#d0d7de",
    "tag_dir":"#0969da","tag_file":"#1f2328",
    "title_bar":"#ffffff","status_bar":"#f6f8fa",
    "scrollbar":"#d0d7de","scrollbar_hover":"#b0bac4",
    "rate_ok":"#1a7f37","rate_warn":"#9a6700","rate_low":"#cf222e",
    "badge_token":"#1a7f37","badge_public":"#9a3412",
    "hl_bg":"#fff8c5","hl_fg":"#9a6700",
    "diff_add":"#d1f8dc","diff_add_fg":"#1a7f37",
    "diff_del":"#ffebe9","diff_del_fg":"#cf222e",
    "diff_hunk":"#dbeafe","diff_hunk_fg":"#0550ae",
    "syn_kw":"#cf222e","syn_str":"#0550ae","syn_cmt":"#6e7781",
    "syn_num":"#0550ae","syn_func":"#8250df","syn_deco":"#bc4c00","syn_builtin":"#0969da",
}

FUI   = "Segoe UI"
FMONO = "Cascadia Code" if os.name == "nt" else "Menlo"
FTIT  = "Segoe UI Semibold"
VER   = "5.0.0"
CFG   = Path.home() / ".gitview_config.json"
RPP   = 20   # results per page

# ── Utilities ──────────────────────────────────────────────────────────────
def fmt_size(b: int) -> str:
    if b < 1024:          return f"{b} B"
    if b < 1_048_576:     return f"{b/1024:.1f} KB"
    if b < 1_073_741_824: return f"{b/1_048_576:.1f} MB"
    return f"{b/1_073_741_824:.1f} GB"

def rel_time(iso: str) -> str:
    if not iso: return ""
    try:
        dt = datetime.fromisoformat(iso.replace("Z","+00:00"))
        s  = int((datetime.now(timezone.utc) - dt).total_seconds())
        if s < 60:       return "just now"
        if s < 3600:     return f"{s//60}m ago"
        if s < 86400:    return f"{s//3600}h ago"
        if s < 604800:   return f"{s//86400}d ago"
        if s < 2592000:  return f"{s//604800}w ago"
        if s < 31536000: return f"{s//2592000}mo ago"
        return f"{s//31536000}y ago"
    except Exception:
        return iso[:10] if len(iso) >= 10 else iso

def recency_score(iso: str) -> float:
    if not iso: return 0.0
    try:
        dt = datetime.fromisoformat(iso.replace("Z","+00:00"))
        days = (datetime.now(timezone.utc) - dt).days
        return max(0.0, 1.0 - days / 730.0)
    except Exception:
        return 0.0

def parse_github_input(text: str) -> Optional[str]:
    text = re.sub(r"^https?://", "", text.strip().rstrip("/"))
    text = re.sub(r"^(www\.)?github\.com/?", "", text)
    parts = [p for p in text.split("/") if p]
    if not parts: return None
    u = parts[0]
    return u if re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,37}[a-zA-Z0-9])?$", u) else None

_ICONS = {
    "py":"🐍","js":"🟨","ts":"🔷","jsx":"⚛️","tsx":"⚛️","html":"🌐","css":"🎨",
    "scss":"🎨","sass":"🎨","json":"📋","yaml":"📋","yml":"📋","toml":"📋","ini":"📋",
    "md":"📝","txt":"📄","rst":"📝","log":"📄","sh":"⚙️","bash":"⚙️","zsh":"⚙️",
    "bat":"⚙️","ps1":"⚙️","c":"🔵","cpp":"🔵","h":"🔵","hpp":"🔵","go":"🐹",
    "rs":"🦀","rb":"💎","php":"🐘","java":"☕","kt":"🎯","swift":"🍎","cs":"🔷",
    "sql":"🗄️","db":"🗄️","png":"🖼️","jpg":"🖼️","jpeg":"🖼️","gif":"🖼️","svg":"🖼️",
    "ico":"🖼️","webp":"🖼️","pdf":"📕","zip":"📦","tar":"📦","gz":"📦","rar":"📦",
    "mp4":"🎬","mp3":"🎵","lock":"🔒","env":"🔑","pem":"🔑","key":"🔑",
    "dockerfile":"🐳","gitignore":"🚫","makefile":"🔨","gradle":"🐘",
}
_LANG_MAP = {
    "py":"python","pyw":"python","js":"javascript","jsx":"javascript","mjs":"javascript",
    "ts":"javascript","tsx":"javascript","json":"json","html":"html","htm":"html",
    "css":"css","scss":"css","sh":"bash","bash":"bash","zsh":"bash","rb":"ruby",
    "go":"go","rs":"rust","java":"java","c":"c","h":"c","cpp":"c","hpp":"c",
    "cs":"csharp","php":"php","swift":"swift","kt":"kotlin","sql":"sql",
    "md":"markdown","yaml":"yaml","yml":"yaml","toml":"toml",
}

def file_icon(name: str) -> str:
    n = name.lower()
    for s in ("dockerfile",".gitignore",".env","makefile","readme","license"):
        if s in n: return _ICONS.get(s.lstrip("."), "📄")
    ext = n.rsplit(".",1)[-1] if "." in n else ""
    return _ICONS.get(ext, "📄")

def lang_from_name(name: str) -> str:
    ext = name.lower().rsplit(".",1)[-1] if "." in name else ""
    return _LANG_MAP.get(ext, "text")


# ── Search Engine ──────────────────────────────────────────────────────────
class SearchEngine:
    @staticmethod
    def score(query: str, text: str) -> int:
        q, t = query.lower(), text.lower()
        if not q or not t: return 0
        if t == q:               return 100
        if t.startswith(q):      return 85
        if q in t.split():       return 75
        if t.endswith(q):        return 65
        if q in t:               return 55
        parts = q.split()
        if len(parts) > 1 and all(p in t for p in parts): return 45
        chars = sum(1 for c in q if c in t)
        return int(chars / max(len(q),1) * 30)

    @staticmethod
    def fuzzy(query: str, text: str, threshold: int = 60) -> bool:
        return SearchEngine.score(query, text) >= threshold

    @classmethod
    def rank_repo(cls, query: str, rd: Dict) -> int:
        q   = query.lower()
        sc  = 0
        sc += cls.score(q, rd.get("name","")) * 4
        sc += cls.score(q, rd.get("description") or "") * 1
        sc += sum(50 if q in t.lower() else 0 for t in rd.get("topics",[]))
        lang = (rd.get("language") or "").lower()
        if q == lang: sc += 30
        elif q in lang: sc += 15
        sc += int(recency_score(rd.get("updated_at","")) * 40)
        sc += int(recency_score(rd.get("pushed_at","")) * 20)
        stars = rd.get("stargazers_count", 0)
        sc += min(30, int(stars**0.4))
        return sc

    @classmethod
    def rank_commit(cls, query: str, commit: Dict) -> int:
        msg = (commit.get("commit",{}).get("message","") or "").lower()
        sc  = cls.score(query.lower(), msg) * 3
        sc += int(recency_score(
            (commit.get("commit",{}).get("author") or {}).get("date","")) * 30)
        return sc


# ── Diff Parser ────────────────────────────────────────────────────────────
class DiffParser:
    @staticmethod
    def parse(raw: str) -> List[Dict]:
        files: List[Dict] = []
        cur: Optional[Dict] = None
        hunk: Optional[Dict] = None
        for line in raw.splitlines():
            if line.startswith("diff --git"):
                if cur: files.append(cur)
                cur = {"header": line, "path": "", "hunks": []}
            elif line.startswith("--- ") and cur:
                cur["old"] = line[4:]
            elif line.startswith("+++ ") and cur:
                p = line[4:]
                cur["path"] = p[2:] if p.startswith("b/") else p
                cur["new"]  = p
            elif line.startswith("@@") and cur is not None:
                hunk = {"header": line, "lines": []}
                cur["hunks"].append(hunk)
            elif hunk is not None:
                if line.startswith("+"):
                    hunk["lines"].append(("add", line[1:]))
                elif line.startswith("-"):
                    hunk["lines"].append(("del", line[1:]))
                else:
                    hunk["lines"].append(("ctx", line[1:] if line.startswith(" ") else line))
        if cur: files.append(cur)
        return files

    @staticmethod
    def stats(files: List[Dict]) -> Tuple[int, int]:
        adds = dels = 0
        for f in files:
            for h in f.get("hunks", []):
                for kind, _ in h["lines"]:
                    if kind == "add": adds += 1
                    elif kind == "del": dels += 1
        return adds, dels


# ── Syntax Highlighter ─────────────────────────────────────────────────────
class SyntaxHL:
    _PY_KW  = (r'\b(False|None|True|and|as|assert|async|await|break|class|continue|'
               r'def|del|elif|else|except|finally|for|from|global|if|import|in|is|'
               r'lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b')
    _PY_BLT = (r'\b(abs|all|any|bin|bool|bytes|callable|chr|dict|dir|enumerate|eval|'
               r'filter|float|format|frozenset|getattr|globals|hasattr|hash|hex|id|'
               r'input|int|isinstance|issubclass|iter|len|list|locals|map|max|min|'
               r'next|object|open|ord|pow|print|property|range|repr|reversed|round|'
               r'set|setattr|sorted|staticmethod|str|sum|super|tuple|type|vars|zip)\b')
    _JS_KW  = (r'\b(async|await|break|case|catch|class|const|continue|debugger|default|'
               r'delete|do|else|export|extends|finally|for|from|function|if|import|in|'
               r'instanceof|let|new|null|of|return|static|super|switch|this|throw|try|'
               r'typeof|undefined|var|void|while|with|yield|true|false)\b')
    _SQL_KW = (r'\b(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|OUTER|'
               r'ON|AS|AND|OR|NOT|IN|EXISTS|LIKE|BETWEEN|ORDER|BY|GROUP|HAVING|LIMIT|'
               r'OFFSET|UNION|ALL|DISTINCT|CREATE|TABLE|DROP|ALTER|INDEX|VIEW|PRIMARY|'
               r'KEY|FOREIGN|REFERENCES|UNIQUE|NULL|DEFAULT|BEGIN|COMMIT|ROLLBACK)\b')
    PAT: Dict[str, List[Tuple[str,str]]] = {
        "python": [
            ("syn_cmt",     r'#[^\n]*'),
            ("syn_str",     r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"[^"\n]*"|\'[^\'\n]*\')'),
            ("syn_deco",    r'@\w+'),
            ("syn_kw",      _PY_KW),
            ("syn_builtin", _PY_BLT),
            ("syn_num",     r'\b\d+(\.\d+)?\b'),
            ("syn_func",    r'\bdef\s+(\w+)'),
        ],
        "javascript": [
            ("syn_cmt",  r'//[^\n]*|/\*[\s\S]*?\*/'),
            ("syn_str",  r'(`[^`]*`|"[^"\n]*"|\'[^\'\n]*\')'),
            ("syn_kw",   _JS_KW),
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
                         r'function|return|echo|exit|export|source|local)\b'),
            ("syn_num",  r'\$[\w@#?$!*-]|\$\{[\w@#?$!*-]+\}'),
        ],
        "sql": [
            ("syn_cmt",  r'--[^\n]*|/\*[\s\S]*?\*/'),
            ("syn_str",  r"'[^']*'"),
            ("syn_kw",   _SQL_KW),
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
    for _l in ("c","csharp","java","go","rust","ruby","swift","kotlin","php"):
        PAT[_l] = PAT["javascript"]

    @classmethod
    def apply(cls, widget: tk.Text, lang: str, C: Dict) -> None:
        pats = cls.PAT.get(lang, [])
        if not pats: return
        for tag, col_key in [
            ("syn_kw","syn_kw"),("syn_str","syn_str"),("syn_cmt","syn_cmt"),
            ("syn_num","syn_num"),("syn_func","syn_func"),
            ("syn_deco","syn_deco"),("syn_builtin","syn_builtin"),
        ]:
            widget.tag_configure(tag, foreground=C.get(col_key,"#ccc"))
        content = widget.get("1.0", tk.END)
        for tag, pat in pats:
            try:
                for m in re.finditer(pat, content, re.MULTILINE):
                    widget.tag_add(tag, f"1.0+{m.start()}c", f"1.0+{m.end()}c")
            except (re.error, tk.TclError):
                pass


# ── Widget Helpers ─────────────────────────────────────────────────────────
class Tooltip:
    DELAY = 500
    def __init__(self, w: tk.Widget, text: str, C: Dict):
        self.w, self.text, self.C = w, text, C
        self.tip = self._aid = None
        w.bind("<Enter>",   lambda _: self._sched(), add="+")
        w.bind("<Leave>",   self._cancel, add="+")
        w.bind("<Destroy>", self._cancel, add="+")
    def _sched(self):
        self._cancel()
        self._aid = self.w.after(self.DELAY, self._show)
    def _show(self):
        if not self.w.winfo_exists(): return
        x = self.w.winfo_rootx() + 16
        y = self.w.winfo_rooty() + self.w.winfo_height() + 4
        self.tip = tk.Toplevel(self.w)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        self.tip.wm_attributes("-topmost", True)
        C = self.C
        f = tk.Frame(self.tip, bg=C["border_bright"], padx=1, pady=1)
        f.pack()
        tk.Label(f, text=self.text, bg=C["surface3"], fg=C["fg"],
                 font=(FUI, 8), padx=10, pady=5).pack()
    def _cancel(self, _=None):
        if self._aid:
            try: self.w.after_cancel(self._aid)
            except Exception: pass
            self._aid = None
        if self.tip:
            try: self.tip.destroy()
            except Exception: pass
            self.tip = None

def btn(parent, text, cmd, style="default", C=None, **kw) -> tk.Button:
    C = C or DARK
    S = {
        "default": (C["surface2"],  C["fg"],       C["border_bright"], C["fg"]),
        "accent":  (C["accent"],    "#ffffff",      C["accent_hover"],  "#ffffff"),
        "danger":  (C["danger"],    "#ffffff",      "#ff6961",          "#ffffff"),
        "success": (C["success"],   "#ffffff",      "#56d364",          "#ffffff"),
        "ghost":   (C["surface"],   C["fg_muted"],  C["surface2"],      C["fg"]),
        "ghost2":  (C["surface2"],  C["fg_muted"],  C["surface3"],      C["fg"]),
        "warning": (C["warning"],   "#000",         "#f0c040",          "#000"),
        "purple":  (C["purple"],    "#fff",         "#d2a8ff",          "#000"),
    }
    bg, fg, abg, afg = S.get(style, S["default"])
    font = kw.pop("font", (FUI, 9))
    padx = kw.pop("padx", 12)
    pady = kw.pop("pady", 5)
    b = tk.Button(parent, text=text, command=cmd, font=font, relief=tk.FLAT,
                  cursor="hand2", padx=padx, pady=pady, bd=0,
                  highlightthickness=0, bg=bg, fg=fg,
                  activebackground=abg, activeforeground=afg, **kw)
    b.bind("<Enter>", lambda _: b.config(bg=abg, fg=afg))
    b.bind("<Leave>", lambda _: b.config(bg=bg,  fg=fg))
    return b

def hdiv(parent, C, h=1, pady=0):
    tk.Frame(parent, bg=C["border"], height=h).pack(fill=tk.X, pady=pady)

def slbl(parent, text, C):
    return tk.Label(parent, text=text, bg=C["surface"], fg=C["fg_subtle"],
                    font=(FUI, 7, "bold"))

def entry(parent, var, C, width=20, mono=False, show=None) -> tk.Entry:
    kw = dict(textvariable=var, relief=tk.FLAT, bg=C["entry_bg"], fg=C["fg"],
              insertbackground=C["fg"], width=width, highlightthickness=1,
              highlightbackground=C["entry_border"], highlightcolor=C["accent"])
    if mono: kw["font"] = (FMONO, 10)
    else:    kw["font"] = (FUI, 10)
    if show: kw["show"] = show
    return tk.Entry(parent, **kw)

def scrolled_text(parent, C, mono=False, height=None, **kw) -> tk.Text:
    font = (FMONO, 9) if mono else (FUI, 9)
    defaults = dict(wrap=tk.WORD, bg=C["surface"], fg=C["fg"], font=font,
                    relief=tk.FLAT, highlightthickness=0, state=tk.DISABLED,
                    padx=12, pady=10, selectbackground=C["tree_select"])
    defaults.update(kw)
    if height: defaults["height"] = height
    return tk.Text(parent, **defaults)


# ── Network ────────────────────────────────────────────────────────────────
def rget(session: requests.Session, url: str, params=None, headers=None,
         timeout=15, retries=3) -> requests.Response:
    exc = None
    for i in range(retries):
        try:
            r = session.get(url, params=params, headers=dict(headers or {}),
                            timeout=timeout)
            if r.status_code in (429,500,502,503,504) and i < retries-1:
                time.sleep(2**i); continue
            return r
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            exc = e
            if i < retries-1: time.sleep(2**i)
    raise exc or RuntimeError("Request failed")


# ── Main Application ───────────────────────────────────────────────────────
class GitView:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title(f"GitView v{VER} — Enterprise GitHub Explorer")
        root.geometry("1600x920")
        root.minsize(1100, 660)

        self.session = requests.Session()
        self.session.headers.update({
            "Accept":     "application/vnd.github.v3+json",
            "User-Agent": f"GitView/{VER}",
        })
        self.api_base          = "https://api.github.com"
        self.token: Optional[str]  = None
        self.username: Optional[str] = None
        self.auth_mode         = "token"
        self.current_repo: Optional[str] = None
        self.current_repo_full: Optional[str] = None
        self.current_path      = ""
        self.repo_data: Dict[str, Any] = {}
        self.all_items: Dict[str, List] = {"dirs": [], "files": []}
        self.current_theme     = "dark"
        self.C                 = DARK
        self.pinned_repos: List[str] = []
        self.sort_col          = "name"
        self.sort_rev          = False
        self.rate_remaining    = 60
        self.rate_limit        = 60
        self.rate_reset_ts     = 0.0
        self.op_log: List[str] = []
        self.search_cancel     = threading.Event()
        self.search_history: deque = deque(maxlen=30)
        self.saved_searches: List[str] = []
        self._results: List[Dict] = []
        self._result_page      = 1
        self._search_scope     = "Repos"
        self._preview_wins: List[tk.Toplevel] = []
        self._commits_cache: Dict[str, Any] = {}
        self._diff_cache: Dict[str, str] = {}
        self._debounce_id: Optional[str] = None
        self.show_tok          = False
        self._cp_win: Optional[tk.Toplevel] = None

        self._apply_styles()
        self._build_ui()
        self._shortcuts()
        self._load_cfg()

    # ── Styles ─────────────────────────────────────────────────────────────
    def _apply_styles(self):
        C = self.C
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Treeview", background=C["surface"], foreground=C["fg"],
                    fieldbackground=C["surface"], rowheight=34,
                    font=(FUI, 10), borderwidth=0, relief="flat")
        s.configure("Treeview.Heading", background=C["surface2"],
                    foreground=C["fg_muted"], font=(FUI, 8, "bold"),
                    relief="flat", padding=(10, 8))
        s.map("Treeview",
              background=[("selected", C["tree_select"])],
              foreground=[("selected", C["accent_hover"])])
        s.map("Treeview.Heading", background=[("active", C["surface3"])])
        s.configure("TNotebook", background=C["bg"], borderwidth=0, tabmargins=[0,0,0,0])
        s.configure("TNotebook.Tab", background=C["surface2"], foreground=C["fg_muted"],
                    padding=[20, 9], font=(FUI, 9, "bold"), borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", C["bg"])],
              foreground=[("selected", C["fg"])],
              expand=[("selected", [0,0,0,0])])
        s.configure("TCombobox", fieldbackground=C["surface2"], background=C["surface2"],
                    foreground=C["fg"], arrowcolor=C["fg_muted"],
                    selectbackground=C["tree_select"], selectforeground=C["fg"],
                    borderwidth=0, relief="flat", padding=(8, 6))
        s.map("TCombobox",
              fieldbackground=[("readonly", C["surface2"])],
              foreground=[("readonly", C["fg"])],
              arrowcolor=[("disabled", C["fg_subtle"])])
        s.configure("TScrollbar", background=C["scrollbar"], troughcolor=C["surface"],
                    arrowcolor=C["fg_subtle"], relief="flat", borderwidth=0, width=8)
        s.map("TScrollbar",
              background=[("active", C["scrollbar_hover"]), ("pressed", C["accent"])])
        s.configure("Horizontal.TProgressbar", troughcolor=C["surface2"],
                    background=C["accent"], borderwidth=0, thickness=3)
        s.configure("TPanedwindow", background=C["bg"])
        self.root.configure(bg=C["bg"])
        self.root.option_add("*TCombobox*Listbox.background", C["surface2"])
        self.root.option_add("*TCombobox*Listbox.foreground", C["fg"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", C["tree_select"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", C["accent_hover"])
        self.root.option_add("*TCombobox*Listbox.font", (FUI, 10))

    # ── UI Build ───────────────────────────────────────────────────────────
    def _build_ui(self):
        C = self.C
        wrap = tk.Frame(self.root, bg=C["bg"])
        wrap.pack(fill=tk.BOTH, expand=True)
        self._wrap = wrap
        self._build_titlebar(wrap)
        self._build_authbar(wrap)
        body = tk.Frame(wrap, bg=C["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0,8))
        self.nb = ttk.Notebook(body)
        self.nb.pack(fill=tk.BOTH, expand=True)
        for name, tab_key in [
            ("  📁  Explorer  ","_tab_explorer"),
            ("  🔍  Search  ","_tab_search"),
            ("  🕐  Commits  ","_tab_commits"),
            ("  ⚡  Operations  ","_tab_ops"),
            ("  ℹ️  About  ","_tab_about"),
        ]:
            f = tk.Frame(self.nb, bg=C["bg"])
            self.nb.add(f, text=name)
            setattr(self, tab_key, f)
        self._build_explorer()
        self._build_search()
        self._build_commits()
        self._build_ops()
        self._build_about()
        self._build_statusbar(wrap)
        self._build_ctxmenu()

    # ── Title Bar ──────────────────────────────────────────────────────────
    def _build_titlebar(self, parent):
        C = self.C
        tk.Frame(parent, bg=C["accent"], height=2).pack(fill=tk.X)
        bar = tk.Frame(parent, bg=C["title_bar"], height=56)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)
        inner = tk.Frame(bar, bg=C["title_bar"])
        inner.pack(fill=tk.BOTH, expand=True, padx=18)

        lf = tk.Frame(inner, bg=C["title_bar"])
        lf.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(lf, text="⬡", bg=C["title_bar"], fg=C["accent"],
                 font=(FUI, 22)).pack(side=tk.LEFT, padx=(0,8), pady=8)
        bf = tk.Frame(lf, bg=C["title_bar"])
        bf.pack(side=tk.LEFT, fill=tk.Y, pady=10)
        tk.Label(bf, text="GitView", bg=C["title_bar"], fg=C["fg"],
                 font=(FTIT, 15, "bold")).pack(anchor=tk.W)
        tk.Label(bf, text=f"v{VER}  ·  Enterprise GitHub Intelligence",
                 bg=C["title_bar"], fg=C["fg_muted"], font=(FUI, 8)).pack(anchor=tk.W)

        rlf = tk.Frame(inner, bg=C["title_bar"])
        rlf.pack(side=tk.RIGHT, fill=tk.Y, padx=(8,0), pady=10)
        self.api_reset_lbl = tk.Label(rlf, text="", bg=C["title_bar"],
                                      fg=C["fg_subtle"], font=(FUI, 7))
        self.api_reset_lbl.pack(anchor=tk.E)
        self.rate_lbl = tk.Label(rlf, text="API  ●  —/—", bg=C["title_bar"],
                                 fg=C["fg_subtle"], font=(FMONO, 8))
        self.rate_lbl.pack(anchor=tk.E)

        right = tk.Frame(inner, bg=C["title_bar"])
        right.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0,8))
        for label, cmd in [("❓  Help", self._show_help),
                            ("⌘  Palette", self._open_palette),
                            ("🌐  GitHub", lambda: webbrowser.open("https://github.com/dragonked2/gitview"))]:
            btn(right, label, cmd, style="ghost", C=C, font=(FUI,9), padx=10, pady=4
                ).pack(side=tk.RIGHT, padx=2)
        self.theme_btn = btn(right,
            "🌙  Dark" if self.current_theme == "dark" else "☀️  Light",
            self._toggle_theme, style="ghost", C=C, font=(FUI,9), padx=10, pady=4)
        self.theme_btn.pack(side=tk.RIGHT, padx=2)

    # ── Auth Bar ───────────────────────────────────────────────────────────
    def _build_authbar(self, parent):
        C = self.C
        bar = tk.Frame(parent, bg=C["surface"],
                       highlightbackground=C["border"], highlightthickness=1)
        bar.pack(fill=tk.X, padx=12, pady=(4,0))
        inner = tk.Frame(bar, bg=C["surface"])
        inner.pack(fill=tk.BOTH, expand=True, padx=14, pady=8)

        left = tk.Frame(inner, bg=C["surface"])
        left.pack(side=tk.LEFT, fill=tk.Y)
        mr = tk.Frame(left, bg=C["surface"])
        mr.pack(anchor=tk.W)
        self._tab_tok_btn = btn(mr, "🔑  Token Mode", self._sw_token,
                                style="accent" if self.auth_mode=="token" else "ghost2",
                                C=C, font=(FUI,8,"bold"), padx=12, pady=4)
        self._tab_tok_btn.pack(side=tk.LEFT)
        self._tab_pub_btn = btn(mr, "👤  Browse Public", self._sw_public,
                                style="accent" if self.auth_mode=="public" else "ghost2",
                                C=C, font=(FUI,8,"bold"), padx=12, pady=4)
        self._tab_pub_btn.pack(side=tk.LEFT, padx=(4,0))

        self._tok_frame = tk.Frame(left, bg=C["surface"])
        slbl(self._tok_frame, "PERSONAL ACCESS TOKEN", C).pack(anchor=tk.W, pady=(4,2))
        tokrow = tk.Frame(self._tok_frame, bg=C["surface"])
        tokrow.pack(fill=tk.X)
        self.tok_var = tk.StringVar()
        self.tok_entry = entry(tokrow, self.tok_var, C, width=44, mono=True, show="•")
        self.tok_entry.pack(side=tk.LEFT, ipady=6, padx=(0,4))
        self.tok_entry.bind("<Return>", lambda _: self._connect_token())
        self.eye_btn = btn(tokrow, "👁", self._toggle_tok_vis, style="ghost2",
                           C=C, font=(FUI,11), padx=6, pady=4)
        self.eye_btn.pack(side=tk.LEFT, padx=(0,4))
        self.connect_btn = btn(tokrow, "  ⚡  Connect  ", self._connect_token,
                               style="accent", C=C, font=(FUI,9,"bold"), padx=14, pady=6)
        self.connect_btn.pack(side=tk.LEFT)
        self.disconnect_btn = btn(tokrow, "✕  Disconnect", self._disconnect,
                                  style="danger", C=C, font=(FUI,9), pady=6)
        self.disconnect_btn.pack(side=tk.LEFT, padx=(4,0))
        self.disconnect_btn.pack_forget()
        lnk = tk.Label(self._tok_frame,
                       text="🆘  No token? Click to generate one →",
                       bg=C["surface"], fg=C["accent"], font=(FUI,8), cursor="hand2")
        lnk.pack(anchor=tk.W, pady=(3,0))
        lnk.bind("<Button-1>", lambda _: webbrowser.open(
            "https://github.com/settings/tokens/new?description=GitView&scopes=repo"))

        self._pub_frame = tk.Frame(left, bg=C["surface"])
        slbl(self._pub_frame, "USERNAME or github.com/username", C).pack(
            anchor=tk.W, pady=(4,2))
        pubrow = tk.Frame(self._pub_frame, bg=C["surface"])
        pubrow.pack(fill=tk.X)
        self.pub_var = tk.StringVar()
        self.pub_entry = entry(pubrow, self.pub_var, C, width=36, mono=True)
        self.pub_entry.pack(side=tk.LEFT, ipady=6, padx=(0,6))
        self.pub_entry.bind("<Return>", lambda _: self._connect_public())
        for lbl, val in [("torvalds","torvalds"),("microsoft","microsoft"),("google","google")]:
            btn(pubrow, lbl,
                lambda v=val: (self.pub_var.set(v), self._connect_public()),
                style="ghost2", C=C, font=(FUI,8), padx=7, pady=6).pack(side=tk.LEFT, padx=2)
        btn(pubrow, "  🚀  Browse  ", self._connect_public,
            style="success", C=C, font=(FUI,9,"bold"), padx=14, pady=6
            ).pack(side=tk.LEFT, padx=(6,0))
        tk.Label(self._pub_frame, text="📌  Public repos only  ·  60 req/hr",
                 bg=C["surface"], fg=C["warning"], font=(FUI,7)).pack(anchor=tk.W, pady=(3,0))

        if self.auth_mode == "token":
            self._tok_frame.pack(fill=tk.X, pady=(6,0))
        else:
            self._pub_frame.pack(fill=tk.X, pady=(6,0))

        tk.Frame(inner, bg=C["border"], width=1).pack(side=tk.RIGHT, fill=tk.Y, padx=12)
        ra = tk.Frame(inner, bg=C["surface"])
        ra.pack(side=tk.RIGHT, fill=tk.Y, padx=(0,8))
        self.avatar_lbl = tk.Label(ra, text="○", bg=C["surface"], fg=C["fg_subtle"],
                                   font=(FUI, 32))
        self.avatar_lbl.pack(side=tk.LEFT, padx=(0,12))
        uc = tk.Frame(ra, bg=C["surface"])
        uc.pack(side=tk.LEFT, fill=tk.Y, pady=4)
        self.uname_lbl = tk.Label(uc, text="Not Connected", bg=C["surface"],
                                  fg=C["fg_muted"], font=(FTIT,12,"bold"))
        self.uname_lbl.pack(anchor=tk.W)
        self.umeta_lbl = tk.Label(uc, text="Choose Token or Public mode above",
                                  bg=C["surface"], fg=C["fg_subtle"], font=(FUI,8))
        self.umeta_lbl.pack(anchor=tk.W)
        self.ubio_lbl  = tk.Label(uc, text="", bg=C["surface"], fg=C["fg_subtle"],
                                  font=(FUI,8))
        self.ubio_lbl.pack(anchor=tk.W)
        self.ubadge_lbl = tk.Label(uc, text="", bg=C["surface"], fg=C["fg_subtle"],
                                   font=(FUI,7,"bold"))
        self.ubadge_lbl.pack(anchor=tk.W, pady=(2,0))

        ma = tk.Frame(inner, bg=C["surface"])
        ma.pack(side=tk.RIGHT, fill=tk.Y, padx=12)
        self.repo_meta_lbl = tk.Label(ma, text="", bg=C["surface"], fg=C["fg_muted"],
                                      font=(FUI,8), justify=tk.RIGHT)
        self.repo_meta_lbl.pack(anchor=tk.E)
        self.repo_desc_lbl = tk.Label(ma, text="", bg=C["surface"], fg=C["fg_subtle"],
                                      font=(FUI,8), justify=tk.RIGHT, wraplength=280)
        self.repo_desc_lbl.pack(anchor=tk.E)

    def _sw_token(self):
        self.auth_mode = "token"
        C = self.C
        self._tab_tok_btn.config(bg=C["accent"], fg="#fff", activebackground=C["accent_hover"])
        self._tab_pub_btn.config(bg=C["surface2"], fg=C["fg_muted"], activebackground=C["surface3"])
        self._pub_frame.pack_forget()
        self._tok_frame.pack(fill=tk.X, pady=(6,0))

    def _sw_public(self):
        self.auth_mode = "public"
        C = self.C
        self._tab_pub_btn.config(bg=C["accent"], fg="#fff", activebackground=C["accent_hover"])
        self._tab_tok_btn.config(bg=C["surface2"], fg=C["fg_muted"], activebackground=C["surface3"])
        self._tok_frame.pack_forget()
        self._pub_frame.pack(fill=tk.X, pady=(6,0))

    # ── Explorer Tab ───────────────────────────────────────────────────────
    def _build_explorer(self):
        C = self.C
        f = self._tab_explorer
        ctrl = tk.Frame(f, bg=C["surface"], highlightbackground=C["border"], highlightthickness=1)
        ctrl.pack(fill=tk.X, pady=(10,6))
        inner = tk.Frame(ctrl, bg=C["surface"])
        inner.pack(fill=tk.X, padx=12, pady=8)

        rl = tk.Frame(inner, bg=C["surface"])
        rl.pack(side=tk.LEFT, fill=tk.Y)
        slbl(rl, "REPOSITORY", C).pack(anchor=tk.W, pady=(0,2))
        self.repo_var = tk.StringVar()
        self.repo_cb  = ttk.Combobox(rl, textvariable=self.repo_var, state="readonly",
                                     font=(FUI,10), width=34)
        self.repo_cb.pack(side=tk.LEFT, ipady=4)
        self.repo_cb.bind("<<ComboboxSelected>>", self._on_repo_sel)

        bl = tk.Frame(inner, bg=C["surface"])
        bl.pack(side=tk.LEFT, padx=(16,0), fill=tk.Y)
        slbl(bl, "BRANCH", C).pack(anchor=tk.W, pady=(0,2))
        self.branch_var = tk.StringVar()
        self.branch_cb  = ttk.Combobox(bl, textvariable=self.branch_var, state="readonly",
                                       font=(FUI,10), width=20)
        self.branch_cb.pack(side=tk.LEFT, ipady=4)
        self.branch_cb.bind("<<ComboboxSelected>>", self._on_branch_sel)

        navf = tk.Frame(inner, bg=C["surface"])
        navf.pack(side=tk.LEFT, padx=(16,0), fill=tk.Y, pady=3)
        for lbl, cmd, tip in [("⌂", self._go_home,"Home"),("↑", self._go_up,"Up"),
                               ("↻", self._refresh_dir,"Refresh"),("📌", self._pin_repo,"Pin")]:
            b = btn(navf, lbl, cmd, style="ghost2", C=C, font=(FUI,10), padx=8, pady=3)
            b.pack(side=tk.LEFT, padx=2)
            Tooltip(b, tip, C)

        ff = tk.Frame(inner, bg=C["surface"])
        ff.pack(side=tk.LEFT, padx=(16,0), fill=tk.Y)
        slbl(ff, "QUICK FILTER", C).pack(anchor=tk.W, pady=(0,2))
        self.filter_var = tk.StringVar()
        fe = entry(ff, self.filter_var, C, width=18)
        fe.pack(side=tk.LEFT, ipady=5)
        self.filter_var.trace_add("write", lambda *_: self._apply_filter())
        Tooltip(fe, "Filter files  [Ctrl+F]", C)

        self.file_count_lbl = tk.Label(inner, text="", bg=C["surface"], fg=C["fg_muted"],
                                       font=(FUI,8))
        self.file_count_lbl.pack(side=tk.RIGHT, padx=8)

        content = tk.Frame(f, bg=C["bg"])
        content.pack(fill=tk.BOTH, expand=True)
        tree_panel = tk.Frame(content, bg=C["surface"],
                              highlightbackground=C["border"], highlightthickness=1)
        tree_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        path_bar = tk.Frame(tree_panel, bg=C["surface2"], height=30)
        path_bar.pack(fill=tk.X)
        path_bar.pack_propagate(False)
        self.path_lbl = tk.Label(path_bar, text="/", bg=C["surface2"], fg=C["fg_muted"],
                                 font=(FMONO, 9))
        self.path_lbl.pack(side=tk.LEFT, padx=12, pady=5)

        tree_wrap = tk.Frame(tree_panel, bg=C["surface"])
        tree_wrap.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(tree_wrap, columns=("icon","kind","size"),
                                  show="tree headings", selectmode="extended")
        self.tree.heading("#0",    text="  Name",  anchor=tk.W,
                          command=lambda: self._sort_by("name"))
        self.tree.heading("icon",  text="",         anchor=tk.CENTER)
        self.tree.heading("kind",  text="Type",     anchor=tk.W,
                          command=lambda: self._sort_by("kind"))
        self.tree.heading("size",  text="Size",     anchor=tk.W,
                          command=lambda: self._sort_by("size"))
        self.tree.column("#0",   width=380, minwidth=160, stretch=True)
        self.tree.column("icon", width=32,  minwidth=32,  stretch=False)
        self.tree.column("kind", width=70,  minwidth=50,  stretch=False)
        self.tree.column("size", width=80,  minwidth=60,  stretch=False)
        tvsb = ttk.Scrollbar(tree_wrap, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tvsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tvsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.info_frame = tk.Frame(tree_panel, bg=C["surface"])
        self.info_icon  = tk.Label(self.info_frame, text="📁", bg=C["surface"],
                                   fg=C["fg_subtle"], font=(FUI,36))
        self.info_icon.pack()
        self.info_main  = tk.Label(self.info_frame, text="Select a repository",
                                   bg=C["surface"], fg=C["fg_muted"],
                                   font=(FTIT,13,"bold"))
        self.info_main.pack(pady=(8,0))
        self.info_extra = tk.Label(self.info_frame, text="",
                                   bg=C["surface"], fg=C["fg_subtle"], font=(FUI,9))
        self.info_extra.pack(pady=(4,0))
        self.info_frame.place(relx=0.5, rely=0.5, anchor="center")

        preview_panel = tk.Frame(content, bg=C["surface"],
                                 highlightbackground=C["border"], highlightthickness=1,
                                 width=340)
        preview_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(8,0))
        preview_panel.pack_propagate(False)
        phdr = tk.Frame(preview_panel, bg=C["surface2"], height=34)
        phdr.pack(fill=tk.X)
        phdr.pack_propagate(False)
        tk.Label(phdr, text="PREVIEW", bg=C["surface2"], fg=C["fg_muted"],
                 font=(FUI,7,"bold")).pack(side=tk.LEFT, padx=12, pady=8)
        self.prev_open_btn = btn(phdr, "⤢ Expand", self._preview_selected,
                                  style="ghost", C=C, font=(FUI,8), padx=8, pady=2)
        self.prev_open_btn.pack(side=tk.RIGHT, padx=8, pady=5)

        self.preview_text = scrolled_text(preview_panel, C, mono=True)
        pvsb = ttk.Scrollbar(preview_panel, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=pvsb.set)
        pvsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>",          self._on_tree_dbl)
        self.tree.bind("<<TreeviewSelect>>",  self._on_tree_sel)
        self.tree.bind("<Return>",            self._on_tree_dbl)
        self.tree.bind("<space>",             lambda _: self._preview_selected())
        self.tree.bind("<Home>",              lambda _: self._go_home())
        self.tree.bind("<BackSpace>",         lambda _: self._go_up())

    # ── Search Tab ─────────────────────────────────────────────────────────
    def _build_search(self):
        C = self.C
        f = self._tab_search

        # Banner
        self.search_banner = tk.Frame(f, bg=C["warning_subtle"],
                                      highlightbackground=C["warning"], highlightthickness=1)
        self.search_banner.pack(fill=tk.X, pady=(10,0))
        self._banner_lbl = tk.Label(self.search_banner,
                                    text="ℹ️  Connect to a GitHub user first, then search.",
                                    bg=C["warning_subtle"], fg=C["warning"],
                                    font=(FUI,9), padx=12, pady=7)
        self._banner_lbl.pack(anchor=tk.W)

        # Search bar
        sbar = tk.Frame(f, bg=C["surface"],
                        highlightbackground=C["border"], highlightthickness=1)
        sbar.pack(fill=tk.X, pady=(6,0))
        si = tk.Frame(sbar, bg=C["surface"])
        si.pack(fill=tk.X, padx=12, pady=8)

        self.usearch_var = tk.StringVar()
        se = entry(si, self.usearch_var, C, width=48, mono=True)
        se.pack(side=tk.LEFT, ipady=7, padx=(0,6))
        self.search_entry = se
        se.bind("<Return>", lambda _: self._do_search())
        se.bind("<Down>",   lambda _: self._show_history())
        self.usearch_var.trace_add("write", self._debounce_search)

        btn(si, "🕐", self._show_history, style="ghost2", C=C,
            font=(FUI,11), padx=8, pady=6).pack(side=tk.LEFT)
        self.search_go_btn = btn(si, "  🔍  Search  ", self._do_search,
                                 style="accent", C=C, font=(FUI,9,"bold"), padx=14, pady=6)
        self.search_go_btn.pack(side=tk.LEFT, padx=(4,0))
        self.search_cancel_btn = btn(si, "✕", self._cancel_search,
                                     style="danger", C=C, font=(FUI,9), padx=8, pady=6)
        self.search_cancel_btn.pack(side=tk.LEFT, padx=(4,0))
        self.search_cancel_btn.config(state=tk.DISABLED)
        self.search_prog_lbl = tk.Label(si, text="", bg=C["surface"],
                                        fg=C["fg_muted"], font=(FUI,8))
        self.search_prog_lbl.pack(side=tk.LEFT, padx=8)
        btn(si, "⭐  Saved", self._show_saved_searches, style="ghost2", C=C,
            font=(FUI,8), padx=8, pady=6).pack(side=tk.RIGHT, padx=4)
        btn(si, "➕  Save", self._save_current_search, style="ghost2", C=C,
            font=(FUI,8), padx=8, pady=6).pack(side=tk.RIGHT)

        # Scope + Filters row
        sf = tk.Frame(sbar, bg=C["surface"])
        sf.pack(fill=tk.X, padx=12, pady=(0,8))
        self.scope_var = tk.StringVar(value="Repos")
        self._scope_btns: Dict[str, tk.Button] = {}
        for scope in ("Repos","Content","Files","Commits","Topics"):
            b = btn(sf, scope,
                    lambda s=scope: self._select_scope(s),
                    style="accent" if scope == "Repos" else "ghost2",
                    C=C, font=(FUI,8,"bold"), padx=10, pady=3)
            b.pack(side=tk.LEFT, padx=(0,3))
            self._scope_btns[scope] = b

        self.filter_lang_var = tk.StringVar()
        self.filter_ext_var  = tk.StringVar()
        for var, lbl, w in [
            (self.filter_lang_var, "Lang:", 12),
            (self.filter_ext_var,  "Ext:",  10),
        ]:
            tk.Label(sf, text=lbl, bg=C["surface"], fg=C["fg_subtle"],
                     font=(FUI,8)).pack(side=tk.LEFT, padx=(12,2))
            e = entry(sf, var, C, width=w)
            e.pack(side=tk.LEFT, ipady=3)

        # Results area (split)
        outer = tk.Frame(f, bg=C["bg"])
        outer.pack(fill=tk.BOTH, expand=True, pady=(6,0))

        left_panel = tk.Frame(outer, bg=C["bg"])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        res_hdr = tk.Frame(left_panel, bg=C["surface"],
                           highlightbackground=C["border"], highlightthickness=1, height=34)
        res_hdr.pack(fill=tk.X)
        res_hdr.pack_propagate(False)
        self.search_count_lbl = tk.Label(res_hdr, text="", bg=C["surface"],
                                         fg=C["fg_muted"], font=(FUI,8,"bold"))
        self.search_count_lbl.pack(side=tk.LEFT, padx=12, pady=8)
        sort_row = tk.Frame(res_hdr, bg=C["surface"])
        sort_row.pack(side=tk.RIGHT, padx=8, pady=4)
        tk.Label(sort_row, text="Sort:", bg=C["surface"], fg=C["fg_subtle"],
                 font=(FUI,7)).pack(side=tk.LEFT)
        self.sort_var = tk.StringVar(value="relevance")
        for sv, sl in [("relevance","Relevance"),("name","Name"),("date","Date"),("activity","Activity")]:
            tk.Radiobutton(sort_row, text=sl, variable=self.sort_var, value=sv,
                           bg=C["surface"], fg=C["fg_muted"], selectcolor=C["surface3"],
                           activebackground=C["surface"], font=(FUI,8), cursor="hand2",
                           command=self._resort).pack(side=tk.LEFT, padx=2)

        # Scrollable results
        res_scrl = tk.Frame(left_panel, bg=C["bg"])
        res_scrl.pack(fill=tk.BOTH, expand=True)
        self.res_canvas = tk.Canvas(res_scrl, bg=C["bg"], highlightthickness=0)
        res_vsb = ttk.Scrollbar(res_scrl, orient=tk.VERTICAL, command=self.res_canvas.yview)
        self.res_canvas.configure(yscrollcommand=res_vsb.set)
        res_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.res_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.res_inner = tk.Frame(self.res_canvas, bg=C["bg"])
        self._res_win  = self.res_canvas.create_window((0,0), window=self.res_inner, anchor="nw")
        self.res_inner.bind("<Configure>",
                            lambda _: self.res_canvas.configure(
                                scrollregion=self.res_canvas.bbox("all")))
        self.res_canvas.bind("<Configure>",
                             lambda e: self.res_canvas.itemconfig(self._res_win, width=e.width))
        for ev, delta in [("<MouseWheel>", None), ("<Button-4>", -1), ("<Button-5>", 1)]:
            if ev == "<MouseWheel>":
                self.res_canvas.bind(ev, lambda e: self.res_canvas.yview_scroll(
                    int(-1*(e.delta/120)), "units"))
            else:
                self.res_canvas.bind(ev, lambda e, d=delta: self.res_canvas.yview_scroll(d, "units"))

        # Pager
        self.pager_frame = tk.Frame(left_panel, bg=C["surface"],
                                    highlightbackground=C["border"], highlightthickness=1,
                                    height=38)
        self.pager_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.pager_frame.pack_propagate(False)
        self._build_pager()

        # Detail panel
        det = tk.Frame(outer, bg=C["surface"],
                       highlightbackground=C["border"], highlightthickness=1, width=360)
        det.pack(side=tk.RIGHT, fill=tk.Y, padx=(8,0))
        det.pack_propagate(False)
        dhdr = tk.Frame(det, bg=C["surface2"], height=34)
        dhdr.pack(fill=tk.X)
        dhdr.pack_propagate(False)
        tk.Label(dhdr, text="DETAILS", bg=C["surface2"], fg=C["fg_muted"],
                 font=(FUI,7,"bold")).pack(side=tk.LEFT, padx=12, pady=8)
        self.det_text = scrolled_text(det, C)
        dvsb = ttk.Scrollbar(det, command=self.det_text.yview)
        self.det_text.configure(yscrollcommand=dvsb.set)
        dvsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.det_text.pack(fill=tk.BOTH, expand=True)
        det_btns = tk.Frame(det, bg=C["surface"])
        det_btns.pack(fill=tk.X, padx=12, pady=(0,12))
        self.det_open_btn = btn(det_btns, "🌐  Open on GitHub",
                                lambda: None, style="accent", C=C, font=(FUI,9), pady=5)
        self.det_open_btn.pack(fill=tk.X)
        self.det_nav_btn = btn(det_btns, "📁  Navigate in Explorer",
                               lambda: None, style="ghost2", C=C, font=(FUI,9), pady=5)
        self.det_nav_btn.pack(fill=tk.X, pady=(4,0))

        self._show_search_empty()

    def _build_pager(self):
        C = self.C
        for w in self.pager_frame.winfo_children(): w.destroy()
        pi = tk.Frame(self.pager_frame, bg=C["surface"])
        pi.pack(side=tk.LEFT, padx=12, pady=5)
        self.pager_prev = btn(pi, "← Prev", lambda: self._go_page(-1),
                              style="ghost2", C=C, font=(FUI,8), padx=8, pady=3)
        self.pager_prev.pack(side=tk.LEFT)
        self.pager_lbl = tk.Label(pi, text="Page 0 / 0", bg=C["surface"],
                                  fg=C["fg_muted"], font=(FUI,8))
        self.pager_lbl.pack(side=tk.LEFT, padx=8)
        self.pager_next = btn(pi, "Next →", lambda: self._go_page(1),
                              style="ghost2", C=C, font=(FUI,8), padx=8, pady=3)
        self.pager_next.pack(side=tk.LEFT)

    # ── Commits Tab ────────────────────────────────────────────────────────
    def _build_commits(self):
        C = self.C
        f = self._tab_commits

        ctrl = tk.Frame(f, bg=C["surface"],
                        highlightbackground=C["border"], highlightthickness=1)
        ctrl.pack(fill=tk.X, pady=(10,6))
        ci = tk.Frame(ctrl, bg=C["surface"])
        ci.pack(fill=tk.X, padx=12, pady=8)

        for attr, lbl in [("commit_author_var","AUTHOR"), ("commit_path_var","PATH"),
                           ("commit_msg_var","MESSAGE CONTAINS")]:
            g = tk.Frame(ci, bg=C["surface"])
            g.pack(side=tk.LEFT, padx=(0,12))
            tk.Label(g, text=lbl, bg=C["surface"], fg=C["fg_subtle"],
                     font=(FUI,7,"bold")).pack(anchor=tk.W, pady=(0,2))
            var = tk.StringVar()
            setattr(self, attr, var)
            e = entry(g, var, C, width=16)
            e.pack(ipady=5)

        self.commit_load_btn = btn(ci, "  🕐  Load Commits  ",
                                   self._load_commits, style="accent", C=C,
                                   font=(FUI,9,"bold"), pady=5)
        self.commit_load_btn.pack(side=tk.LEFT)
        self.commit_count_lbl = tk.Label(ci, text="", bg=C["surface"],
                                         fg=C["fg_muted"], font=(FUI,9))
        self.commit_count_lbl.pack(side=tk.RIGHT, padx=8)

        # Split: commit list + diff viewer
        splitter = tk.PanedWindow(f, orient=tk.HORIZONTAL, bg=C["bg"],
                                  sashwidth=6, sashrelief=tk.FLAT)
        splitter.pack(fill=tk.BOTH, expand=True)

        # Left: commit list
        com_panel = tk.Frame(splitter, bg=C["surface"],
                             highlightbackground=C["border"], highlightthickness=1)
        splitter.add(com_panel, minsize=260)
        chdr = tk.Frame(com_panel, bg=C["surface2"], height=34)
        chdr.pack(fill=tk.X)
        chdr.pack_propagate(False)
        tk.Label(chdr, text="COMMIT HISTORY", bg=C["surface2"], fg=C["fg_muted"],
                 font=(FUI,7,"bold")).pack(side=tk.LEFT, padx=12, pady=8)
        self.commit_inf_btn = btn(chdr, "⬇ Load More", self._load_more_commits,
                                  style="ghost2", C=C, font=(FUI,8), padx=8, pady=2)
        self.commit_inf_btn.pack(side=tk.RIGHT, padx=8, pady=5)

        cwrap = tk.Frame(com_panel, bg=C["surface"])
        cwrap.pack(fill=tk.BOTH, expand=True)
        self.commit_tree = ttk.Treeview(cwrap, columns=("sha","author","date"),
                                         show="tree headings", selectmode="browse")
        self.commit_tree.heading("#0",     text="  Message",  anchor=tk.W)
        self.commit_tree.heading("sha",    text="SHA",        anchor=tk.W)
        self.commit_tree.heading("author", text="Author",     anchor=tk.W)
        self.commit_tree.heading("date",   text="Date",       anchor=tk.W)
        self.commit_tree.column("#0",     width=360, minwidth=180, stretch=True)
        self.commit_tree.column("sha",    width=80,  minwidth=60,  stretch=False)
        self.commit_tree.column("author", width=130, minwidth=70,  stretch=False)
        self.commit_tree.column("date",   width=100, minwidth=70,  stretch=False)
        cvsb = ttk.Scrollbar(cwrap, orient=tk.VERTICAL, command=self.commit_tree.yview)
        self.commit_tree.configure(yscrollcommand=cvsb.set)
        self.commit_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cvsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.commit_tree.bind("<<TreeviewSelect>>", self._on_commit_sel)
        self.commit_tree.bind("<Double-1>", self._on_commit_open)
        self._commit_page = 1

        # Right: diff viewer (tabbed: metadata + diff)
        diff_panel = tk.Frame(splitter, bg=C["surface"],
                              highlightbackground=C["border"], highlightthickness=1)
        splitter.add(diff_panel, minsize=400)

        diff_tabs = ttk.Notebook(diff_panel)
        diff_tabs.pack(fill=tk.BOTH, expand=True)
        self._diff_tabs = diff_tabs

        self._diff_meta_frame = tk.Frame(diff_tabs, bg=C["surface"])
        diff_tabs.add(self._diff_meta_frame, text="  📋  Details  ")

        self._diff_view_frame = tk.Frame(diff_tabs, bg=C["surface"])
        diff_tabs.add(self._diff_view_frame, text="  Δ  Diff  ")

        # Meta pane
        self.commit_meta_text = scrolled_text(self._diff_meta_frame, C, mono=False)
        mvsb = ttk.Scrollbar(self._diff_meta_frame, command=self.commit_meta_text.yview)
        self.commit_meta_text.configure(yscrollcommand=mvsb.set)
        mvsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.commit_meta_text.pack(fill=tk.BOTH, expand=True)
        mbf = tk.Frame(self._diff_meta_frame, bg=C["surface"])
        mbf.pack(fill=tk.X, padx=12, pady=(0,12))
        self.commit_open_btn = btn(mbf, "🌐  View on GitHub", lambda: None,
                                   style="accent", C=C, font=(FUI,9), pady=5)
        self.commit_open_btn.pack(fill=tk.X)
        self.commit_copy_btn = btn(mbf, "📋  Copy SHA", lambda: None,
                                   style="ghost2", C=C, font=(FUI,9), pady=5)
        self.commit_copy_btn.pack(fill=tk.X, pady=(4,0))

        # Diff pane — file list + unified diff
        diff_splitter = tk.PanedWindow(self._diff_view_frame, orient=tk.HORIZONTAL,
                                       bg=C["bg"], sashwidth=4, sashrelief=tk.FLAT)
        diff_splitter.pack(fill=tk.BOTH, expand=True)

        file_list_panel = tk.Frame(diff_splitter, bg=C["surface"],
                                   highlightbackground=C["border"], highlightthickness=1)
        diff_splitter.add(file_list_panel, minsize=180)
        flhdr = tk.Frame(file_list_panel, bg=C["surface2"], height=28)
        flhdr.pack(fill=tk.X)
        flhdr.pack_propagate(False)
        tk.Label(flhdr, text="FILES CHANGED", bg=C["surface2"], fg=C["fg_muted"],
                 font=(FUI,7,"bold")).pack(side=tk.LEFT, padx=8, pady=5)
        self.diff_stats_lbl = tk.Label(flhdr, text="", bg=C["surface2"],
                                       fg=C["fg_muted"], font=(FUI,7))
        self.diff_stats_lbl.pack(side=tk.RIGHT, padx=8)
        self.diff_file_tree = ttk.Treeview(file_list_panel, show="tree",
                                            selectmode="browse")
        self.diff_file_tree.column("#0", width=200, stretch=True)
        dfvsb = ttk.Scrollbar(file_list_panel, orient=tk.VERTICAL,
                               command=self.diff_file_tree.yview)
        self.diff_file_tree.configure(yscrollcommand=dfvsb.set)
        self.diff_file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dfvsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.diff_file_tree.bind("<<TreeviewSelect>>", self._on_diff_file_sel)
        self._diff_files: List[Dict] = []

        diff_content_panel = tk.Frame(diff_splitter, bg=C["surface"])
        diff_splitter.add(diff_content_panel, minsize=300)

        diff_toolbar = tk.Frame(diff_content_panel, bg=C["surface2"], height=28)
        diff_toolbar.pack(fill=tk.X)
        diff_toolbar.pack_propagate(False)
        self.diff_mode_var = tk.StringVar(value="unified")
        for mode, label in [("unified","Unified"),("split","Side-by-Side")]:
            tk.Radiobutton(diff_toolbar, text=label, variable=self.diff_mode_var,
                           value=mode, bg=C["surface2"], fg=C["fg_muted"],
                           selectcolor=C["surface3"], activebackground=C["surface2"],
                           font=(FUI,8), cursor="hand2",
                           command=self._redraw_diff).pack(side=tk.LEFT, padx=(8,0), pady=4)
        self.diff_loading_lbl = tk.Label(diff_toolbar, text="",
                                         bg=C["surface2"], fg=C["fg_muted"], font=(FUI,8))
        self.diff_loading_lbl.pack(side=tk.RIGHT, padx=8)

        self.diff_text = tk.Text(diff_content_panel, wrap=tk.NONE,
                                  bg=C["surface"], fg=C["fg"], font=(FMONO, 9),
                                  relief=tk.FLAT, highlightthickness=0,
                                  insertbackground=C["fg"],
                                  selectbackground=C["tree_select"],
                                  padx=8, pady=6, state=tk.DISABLED)
        diff_vscroll = ttk.Scrollbar(diff_content_panel, orient=tk.VERTICAL,
                                      command=self.diff_text.yview)
        diff_hscroll = ttk.Scrollbar(diff_content_panel, orient=tk.HORIZONTAL,
                                      command=self.diff_text.xview)
        self.diff_text.configure(yscrollcommand=diff_vscroll.set,
                                  xscrollcommand=diff_hscroll.set)
        diff_hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        diff_vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.diff_text.pack(fill=tk.BOTH, expand=True)
        self._current_diff_raw = ""

    # ── Operations Tab ─────────────────────────────────────────────────────
    def _build_ops(self):
        C = self.C
        f = self._tab_ops
        outer = tk.Frame(f, bg=C["bg"])
        outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left = tk.Frame(outer, bg=C["bg"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,8))
        self._ops_card(left, "📦  Bulk Download", [
            ("📦  Download Entire Repository", self._dl_entire,    "accent"),
            ("📁  Download Current Folder",    self._dl_folder,    "default"),
            ("📄  Download Selected Files",    self._dl_selected,  "default"),
        ])
        self._ops_card(left, "📤  Upload & Create", [
            ("📤  Upload File",          self._upload_file,   "default"),
            ("📁  Upload Entire Folder", self._upload_folder, "default"),
            ("✏️   Create New File",      self._create_file,   "default"),
            ("📂  Create New Folder",    self._create_folder, "default"),
        ])

        right = tk.Frame(outer, bg=C["bg"], width=340)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)
        self._ops_card(right, "🔧  Repository", [
            ("➕  Create New Repository", self._create_repo,    "accent"),
            ("🔄  Refresh Repositories",  self._load_repos,     "default"),
            ("🌐  Open in Browser",       self._open_browser,   "default"),
            ("🕐  Load Commit History",   self._load_commits,   "default"),
        ])

        prog_card = tk.Frame(right, bg=C["surface"],
                             highlightbackground=C["border"], highlightthickness=1)
        prog_card.pack(fill=tk.X, pady=(0,10))
        ph = tk.Frame(prog_card, bg=C["surface2"], height=34)
        ph.pack(fill=tk.X)
        ph.pack_propagate(False)
        tk.Label(ph, text="⚡  PROGRESS", bg=C["surface2"], fg=C["fg_muted"],
                 font=(FUI,7,"bold")).pack(side=tk.LEFT, padx=12, pady=8)
        pb_wrap = tk.Frame(prog_card, bg=C["surface"])
        pb_wrap.pack(fill=tk.X, padx=12, pady=(6,4))
        self.progress_bar = ttk.Progressbar(pb_wrap, mode="indeterminate",
                                             style="Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X)
        self.progress_var = tk.StringVar(value="No active operations")
        tk.Label(prog_card, textvariable=self.progress_var,
                 bg=C["surface"], fg=C["fg_muted"], font=(FUI,8),
                 wraplength=300, justify=tk.LEFT).pack(padx=12, pady=(0,8), anchor=tk.W)

        log_card = tk.Frame(right, bg=C["surface"],
                            highlightbackground=C["border"], highlightthickness=1)
        log_card.pack(fill=tk.BOTH, expand=True)
        lh = tk.Frame(log_card, bg=C["surface2"], height=34)
        lh.pack(fill=tk.X)
        lh.pack_propagate(False)
        tk.Label(lh, text="📋  OPERATION LOG", bg=C["surface2"], fg=C["fg_muted"],
                 font=(FUI,7,"bold")).pack(side=tk.LEFT, padx=12, pady=8)
        btn(lh, "Clear", self._clear_log, style="ghost", C=C,
            font=(FUI,7), padx=8, pady=3).pack(side=tk.RIGHT, padx=8, pady=5)
        self.log_text = scrolled_text(log_card, C, mono=True)
        lvsb = ttk.Scrollbar(log_card, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=lvsb.set)
        lvsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _ops_card(self, parent, title: str, actions: List[Tuple]):
        C = self.C
        card = tk.Frame(parent, bg=C["surface"],
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill=tk.X, pady=(0,10))
        hdr = tk.Frame(card, bg=C["surface2"], height=34)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text=title, bg=C["surface2"], fg=C["fg_muted"],
                 font=(FUI,7,"bold")).pack(side=tk.LEFT, padx=12, pady=8)
        bi = tk.Frame(card, bg=C["surface"])
        bi.pack(fill=tk.X, padx=12, pady=8)
        for label, cmd, style in actions:
            btn(bi, label, cmd, style=style, C=C, font=(FUI,9), pady=6
                ).pack(fill=tk.X, pady=(0,4))

    # ── About Tab ──────────────────────────────────────────────────────────
    def _build_about(self):
        C = self.C
        f = self._tab_about
        wrapper = tk.Frame(f, bg=C["bg"])
        wrapper.pack(fill=tk.BOTH, expand=True, padx=60, pady=40)
        tk.Label(wrapper, text="⬡", bg=C["bg"], fg=C["accent"],
                 font=(FUI,52)).pack()
        tk.Label(wrapper, text=f"GitView v{VER}", bg=C["bg"], fg=C["fg"],
                 font=(FTIT,24,"bold")).pack(pady=(8,0))
        tk.Label(wrapper, text="Enterprise GitHub Intelligence Platform",
                 bg=C["bg"], fg=C["fg_muted"], font=(FUI,12)).pack(pady=(4,20))
        for line in [
            "Author: Ali Essam  ·  Egypt 🇪🇬",
            "Superior hybrid search engine with recency & activity scoring",
            "Full commit diff viewer with syntax highlighting",
            "Command palette  ·  Saved searches  ·  Live search",
        ]:
            tk.Label(wrapper, text=line, bg=C["bg"], fg=C["fg_muted"],
                     font=(FUI,10)).pack(pady=2)
        btn_row = tk.Frame(wrapper, bg=C["bg"])
        btn_row.pack(pady=24)
        for label, url, style in [
            ("🔗  LinkedIn",      "https://www.linkedin.com/in/dragonked2",   "accent"),
            ("⭐  Star on GitHub","https://github.com/dragonked2/gitview",     "ghost2"),
            ("🔑  Get Token",     "https://github.com/settings/tokens/new",   "ghost2"),
        ]:
            btn(btn_row, label, lambda u=url: webbrowser.open(u),
                style=style, C=C, font=(FUI,10), padx=16, pady=8
                ).pack(side=tk.LEFT, padx=6)

    # ── Status Bar ─────────────────────────────────────────────────────────
    def _build_statusbar(self, parent):
        C = self.C
        sb = tk.Frame(parent, bg=C["status_bar"],
                      highlightbackground=C["border"], highlightthickness=1, height=28)
        sb.pack(fill=tk.X, side=tk.BOTTOM, padx=12, pady=(0,4))
        sb.pack_propagate(False)
        self.status_lbl = tk.Label(sb, text="  Ready", bg=C["status_bar"],
                                   fg=C["fg_muted"], font=(FUI,8))
        self.status_lbl.pack(side=tk.LEFT, padx=4)

    # ── Context Menu ───────────────────────────────────────────────────────
    def _build_ctxmenu(self):
        C = self.C
        self._ctx = tk.Menu(self.root, tearoff=0, bg=C["surface2"], fg=C["fg"],
                            activebackground=C["tree_select"],
                            activeforeground=C["accent_hover"],
                            font=(FUI,9), relief=tk.FLAT, bd=0)
        self._ctx.add_command(label="  📂  Open / Preview",  command=self._on_tree_dbl)
        self._ctx.add_command(label="  📥  Download",        command=self._dl_selected)
        self._ctx.add_command(label="  🌐  Open on GitHub",  command=self._open_selected_browser)
        self._ctx.add_separator()
        self._ctx.add_command(label="  ✏️   Rename",          command=self._rename_selected)
        self._ctx.add_command(label="  🗑  Delete",          command=self._delete_selected)
        self.tree.bind("<Button-3>", self._show_ctx)
        self.tree.bind("<Button-2>", self._show_ctx)

    def _show_ctx(self, e):
        iid = self.tree.identify_row(e.y)
        if iid: self.tree.selection_set(iid)
        self._ctx.post(e.x_root, e.y_root)

    # ── Keyboard Shortcuts ─────────────────────────────────────────────────
    def _shortcuts(self):
        for key, fn in [
            ("<Control-k>",      self._open_palette),
            ("<Control-K>",      self._open_palette),
            ("<Control-f>",      lambda e: (self.nb.select(0), self.filter_var.set(""), self.tree.focus_set())),
            ("<Control-d>",      lambda e: self._dl_selected()),
            ("<Control-u>",      lambda e: self._upload_file()),
            ("<Control-n>",      lambda e: self._create_file()),
            ("<F5>",             lambda e: self._load_repos()),
            ("<F2>",             lambda e: self._rename_selected()),
            ("<Delete>",         lambda e: self._delete_selected()),
            ("<Escape>",         lambda e: self._cancel_search()),
        ]:
            self.root.bind(key, fn)

    # ── Command Palette ────────────────────────────────────────────────────
    def _open_palette(self, _=None):
        if self._cp_win and self._cp_win.winfo_exists():
            self._cp_win.focus_set(); return
        C = self.C
        self._cp_win = win = tk.Toplevel(self.root)
        win.wm_overrideredirect(True)
        win.wm_attributes("-topmost", True)
        win.configure(bg=C["border_bright"])
        x = self.root.winfo_x() + (self.root.winfo_width() - 620) // 2
        y = self.root.winfo_y() + 80
        win.wm_geometry(f"620x420+{x}+{y}")
        outer = tk.Frame(win, bg=C["surface"], padx=1, pady=1)
        outer.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        search_row = tk.Frame(outer, bg=C["surface"])
        search_row.pack(fill=tk.X)
        tk.Label(search_row, text="⌘", bg=C["surface"], fg=C["accent"],
                 font=(FUI,14)).pack(side=tk.LEFT, padx=12, pady=10)
        pvar = tk.StringVar()
        pe = tk.Entry(search_row, textvariable=pvar, relief=tk.FLAT,
                      bg=C["surface"], fg=C["fg"], insertbackground=C["fg"],
                      font=(FUI,14), highlightthickness=0, bd=0)
        pe.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)
        pe.focus_set()
        tk.Label(search_row, text="esc", bg=C["surface"], fg=C["fg_subtle"],
                 font=(FUI,9), padx=8).pack(side=tk.RIGHT)
        hdiv(outer, C)

        listbox = tk.Listbox(outer, bg=C["surface"], fg=C["fg"], font=(FUI,10),
                              relief=tk.FLAT, highlightthickness=0, bd=0,
                              selectbackground=C["tree_select"],
                              selectforeground=C["accent_hover"],
                              activestyle="none", height=15)
        listbox.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        CMDS = [
            ("📁  Explorer",                 lambda: self.nb.select(0)),
            ("🔍  Search",                   lambda: self.nb.select(1)),
            ("🕐  Commits",                  lambda: (self.nb.select(2), self._load_commits())),
            ("⚡  Operations",               lambda: self.nb.select(3)),
            ("🌙/☀️  Toggle Theme",           self._toggle_theme),
            ("🔄  Refresh Repositories",     self._load_repos),
            ("📦  Download Entire Repo",     self._dl_entire),
            ("📤  Upload File",              self._upload_file),
            ("✏️   Create New File",          self._create_file),
            ("📂  Create New Folder",        self._create_folder),
            ("➕  Create Repository",        self._create_repo),
            ("⌂  Go to Root",               self._go_home),
            ("🌐  Open in Browser",          self._open_browser),
            ("❓  Help",                     self._show_help),
        ]

        def _refresh(q=""):
            listbox.delete(0, tk.END)
            for label, _ in CMDS:
                if not q or q.lower() in label.lower():
                    listbox.insert(tk.END, f"  {label}")
            if listbox.size(): listbox.selection_set(0)

        def _run():
            sel = listbox.curselection()
            if not sel: return
            idx = sel[0]; q = pvar.get().lower()
            matches = [c for label,c in CMDS if not q or q.lower() in label.lower()]
            if idx < len(matches):
                win.destroy()
                matches[idx]()

        pvar.trace_add("write", lambda *_: _refresh(pvar.get()))
        listbox.bind("<Return>",       lambda _: _run())
        listbox.bind("<Double-1>",     lambda _: _run())
        pe.bind("<Return>",            lambda _: _run())
        pe.bind("<Down>",              lambda _: (listbox.focus_set(),
                                                  listbox.selection_set(0)) if listbox.size() else None)
        win.bind("<Escape>",           lambda _: win.destroy())
        win.bind("<FocusOut>",         lambda _: win.destroy())
        _refresh()

    # ── Auth ───────────────────────────────────────────────────────────────
    def _toggle_tok_vis(self):
        self.show_tok = not self.show_tok
        self.tok_entry.config(show="" if self.show_tok else "•")

    def _connect_token(self):
        tok = self.tok_var.get().strip()
        if not tok:
            messagebox.showwarning("GitView", "Please enter a Personal Access Token.")
            return
        self.token = tok
        self.session.headers.update({"Authorization": f"token {tok}"})
        self._set_status("Connecting with token…")
        self.progress_bar.start()
        self.connect_btn.config(state=tk.DISABLED, text="Connecting…")

        def _work():
            try:
                r = rget(self.session, f"{self.api_base}/user", timeout=15)
                self._parse_rl(r)
                if r.status_code == 200:
                    data = r.json()
                    self.username = data.get("login","")
                    self.root.after(0, lambda: self._on_connected(data, "token"))
                elif r.status_code == 401:
                    self.root.after(0, lambda: self._set_status("Invalid token", "err"))
                    self.root.after(0, lambda: messagebox.showerror(
                        "GitView", "Token invalid or expired."))
                else:
                    self.root.after(0, lambda: self._set_status(f"Auth error: {r.status_code}", "err"))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(f"Connection error: {e}", "err"))
            finally:
                self.root.after(0, self.progress_bar.stop)
                self.root.after(0, lambda: self.connect_btn.config(
                    state=tk.NORMAL, text="  ⚡  Connect  "))

        threading.Thread(target=_work, daemon=True).start()

    def _connect_public(self):
        raw = self.pub_var.get().strip()
        user = parse_github_input(raw)
        if not user:
            messagebox.showwarning("GitView", "Invalid username or GitHub URL.")
            return
        self.token = None
        self.session.headers.pop("Authorization", None)
        self._set_status(f"Connecting to @{user}…")
        self.progress_bar.start()

        def _work():
            try:
                r = rget(self.session, f"{self.api_base}/users/{user}", timeout=15)
                self._parse_rl(r)
                if r.status_code == 200:
                    data = r.json()
                    self.username = data.get("login","")
                    self.root.after(0, lambda: self._on_connected(data, "public"))
                elif r.status_code == 404:
                    self.root.after(0, lambda: messagebox.showerror(
                        "GitView", f"User '{user}' not found."))
                else:
                    self.root.after(0, lambda: self._set_status(f"Error: {r.status_code}", "err"))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(str(e), "err"))
            finally:
                self.root.after(0, self.progress_bar.stop)

        threading.Thread(target=_work, daemon=True).start()

    def _on_connected(self, data: Dict, mode: str):
        C = self.C
        login = data.get("login","")
        name  = data.get("name") or login
        repos = data.get("public_repos",0)
        fol   = data.get("followers",0)
        bio   = (data.get("bio") or "")[:60]
        self.uname_lbl.config(text=name, fg=C["fg"])
        self.umeta_lbl.config(text=f"@{login}  ·  {repos} repos  ·  {fol:,} followers",
                               fg=C["fg_muted"])
        self.ubio_lbl.config(text=bio, fg=C["fg_subtle"])
        badge = "🔑  TOKEN MODE" if mode=="token" else "👤  PUBLIC MODE"
        bcol  = C["badge_token"] if mode=="token" else C["badge_public"]
        self.ubadge_lbl.config(text=badge, fg=bcol)
        self.avatar_lbl.config(text="●", fg=C["success"])
        self.disconnect_btn.pack(side=tk.LEFT, padx=(4,0))
        self.connect_btn.config(text="  ✓  Connected  ")
        self._update_search_banner()
        self._update_rl_display()
        self._set_status(f"Connected as @{login}", "ok")
        self._log(f"Connected: @{login} [{mode}]")
        self._save_cfg()
        self._load_repos()

    def _disconnect(self):
        self.token = self.username = None
        self.session.headers.pop("Authorization", None)
        self.current_repo = self.current_repo_full = None
        self.current_path = ""
        self.repo_data.clear()
        self.repo_cb["values"] = []
        self.branch_cb["values"] = []
        self.tree.delete(*self.tree.get_children())
        C = self.C
        self.uname_lbl.config(text="Not Connected", fg=C["fg_muted"])
        self.umeta_lbl.config(text="Choose Token or Public mode above", fg=C["fg_subtle"])
        self.ubio_lbl.config(text="", fg=C["fg_subtle"])
        self.ubadge_lbl.config(text="")
        self.avatar_lbl.config(text="○", fg=C["fg_subtle"])
        self.disconnect_btn.pack_forget()
        self.connect_btn.config(text="  ⚡  Connect  ")
        self.rate_remaining = 60; self.rate_limit = 60
        self._update_rl_display()
        self._update_search_banner()
        self._set_status("Disconnected")
        self._log("Disconnected")

    def _update_search_banner(self):
        try:
            C = self.C
            if self.username:
                mode = "🔑 Token (5000/hr)" if self.auth_mode=="token" else "👤 Public (60/hr)"
                self._banner_lbl.config(
                    text=f"✅  Searching @{self.username}  ·  Mode: {mode}  ·  Ctrl+K palette",
                    bg=C["success_subtle"], fg=C["success"])
                self.search_banner.config(bg=C["success_subtle"])
            else:
                self._banner_lbl.config(
                    text="ℹ️   Connect a GitHub account first, then search across repositories.",
                    bg=C["warning_subtle"], fg=C["warning"])
                self.search_banner.config(bg=C["warning_subtle"])
        except Exception: pass

    # ── Repos & Branches ───────────────────────────────────────────────────
    def _load_repos(self):
        if not self.username: return
        self._set_status(f"Loading repositories for @{self.username}…")
        self.progress_bar.start()

        def _work():
            try:
                repos, page = [], 1
                while True:
                    url = (f"{self.api_base}/user/repos" if self.auth_mode=="token"
                           else f"{self.api_base}/users/{self.username}/repos")
                    r = rget(self.session, url, params={
                        "per_page":100,"page":page,"sort":"updated","type":"all"}, timeout=20)
                    self._parse_rl(r)
                    if r.status_code != 200: break
                    batch = r.json()
                    if not batch: break
                    repos.extend(batch)
                    if len(batch) < 100: break
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
            key = rd.get("full_name", rd.get("name",""))
            self.repo_data[key] = rd
        names = self._repo_names()
        self.repo_cb["values"] = names
        if names:
            prev = self.current_repo_full
            self.repo_cb.set(prev if prev and prev in names else names[0])
            self._on_repo_sel()
        self._set_status(f"Loaded {len(repos)} repositories", "ok")
        self._log(f"Loaded {len(repos)} repos for @{self.username}")
        self._show_info("📦", f"{len(repos)} repositories loaded",
                        f"@{self.username}  ·  Select a repository above to explore")

    def _repo_names(self) -> List[str]:
        pinned   = [k for k in self.pinned_repos if k in self.repo_data]
        unpinned = [k for k in self.repo_data   if k not in pinned]
        return pinned + unpinned

    def _on_repo_sel(self, _=None):
        key = self.repo_var.get()
        if not key or key not in self.repo_data: return
        rd = self.repo_data[key]
        self.current_repo      = rd.get("name", key.split("/")[-1])
        self.current_repo_full = key
        self.current_path      = ""
        self._update_repo_meta()
        self._load_branches()
        self._log(f"Selected repo: {key}")

    def _update_repo_meta(self):
        key = self.repo_var.get()
        if key not in self.repo_data: return
        rd   = self.repo_data[key]
        lang = rd.get("language") or "—"
        self.repo_meta_lbl.config(
            text=f"★ {rd.get('stargazers_count',0):,}  🍴 {rd.get('forks_count',0):,}"
                 f"  {lang}  ·  {rel_time(rd.get('updated_at',''))}")
        self.repo_desc_lbl.config(text=(rd.get("description") or "No description")[:120])

    def _load_branches(self):
        if not self.current_repo: return
        def _work():
            try:
                r = rget(self.session,
                         f"{self.api_base}/repos/{self.username}/{self.current_repo}/branches",
                         params={"per_page":100}, timeout=15)
                self._parse_rl(r)
                if r.status_code == 200:
                    branches = [b["name"] for b in r.json()]
                    self.root.after(0, lambda: self._on_branches_loaded(branches))
            except Exception: pass
        threading.Thread(target=_work, daemon=True).start()

    def _on_branches_loaded(self, branches: List[str]):
        self.branch_cb["values"] = branches
        rd = self.repo_data.get(self.current_repo_full or "", {})
        default = rd.get("default_branch","main")
        self.branch_var.set(default if default in branches else (branches[0] if branches else ""))
        self._load_dir("")

    def _on_branch_sel(self, _=None):
        self.current_path = ""
        self._load_dir("")

    def _pin_repo(self):
        key = self.repo_var.get()
        if not key: return
        if key in self.pinned_repos:
            self.pinned_repos.remove(key)
            self._set_status(f"Unpinned: {key}", "ok")
        else:
            self.pinned_repos.append(key)
            self._set_status(f"Pinned: {key}", "ok")
        self.repo_cb["values"] = self._repo_names()
        self._save_cfg()

    # ── Directory Navigation ───────────────────────────────────────────────
    def _load_dir(self, path: str):
        if not self.current_repo: return
        self.current_path = path
        branch = self.branch_var.get()
        self.path_lbl.config(text=f"/{path}" if path else "/")
        self._show_info("⏳","Loading…","Fetching from GitHub")
        self.tree.delete(*self.tree.get_children())
        self.filter_var.set("")
        self._clear_preview()

        def _work():
            try:
                r = rget(self.session,
                         f"{self.api_base}/repos/{self.username}/{self.current_repo}/contents/{path}",
                         params={"ref":branch} if branch else {}, timeout=20)
                self._parse_rl(r)
                if r.status_code == 200:
                    items = r.json()
                    if not isinstance(items, list): items = [items]
                    self.root.after(0, lambda: self._populate_tree(items))
                elif r.status_code == 404:
                    self.root.after(0, lambda: self._show_info(
                        "⚠️","Path not found", f"'{path}' doesn't exist on '{branch}'"))
                else:
                    msg = r.json().get("message","Error")
                    self.root.after(0, lambda: self._set_status(msg, "err"))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(str(e), "err"))

        threading.Thread(target=_work, daemon=True).start()

    def _populate_tree(self, items: List[Dict]):
        self.all_items = {"dirs":[], "files":[]}
        for item in items:
            (self.all_items["dirs"] if item.get("type")=="dir"
             else self.all_items["files"]).append(item)
        self._render_tree(self.all_items["dirs"] + self.all_items["files"])
        d = len(self.all_items["dirs"]); fi = len(self.all_items["files"])
        self.file_count_lbl.config(text=f"{d} folders  ·  {fi} files")
        self._set_status(
            f"Loaded {d+fi} items  ·  {self.current_repo}/{self.current_path or ''}","ok")
        self.info_frame.place_forget()

    def _render_tree(self, items: List[Dict]):
        self.tree.delete(*self.tree.get_children())
        C = self.C
        for item in items:
            is_dir = item.get("type") == "dir"
            name   = item.get("name","")
            size   = item.get("size",0)
            self.tree.insert("", "end",
                             text=f"  {name}",
                             values=(file_icon(name), "Folder" if is_dir else "File",
                                     "—" if is_dir else fmt_size(size)),
                             tags=("dir" if is_dir else "file",))
        self.tree.tag_configure("dir",  foreground=C["tag_dir"])
        self.tree.tag_configure("file", foreground=C["tag_file"])

    def _show_info(self, icon: str, main: str, extra: str):
        self.tree.delete(*self.tree.get_children())
        self.info_icon.config(text=icon)
        self.info_main.config(text=main)
        self.info_extra.config(text=extra)
        self.info_frame.place(relx=0.5, rely=0.5, anchor="center")

    def _on_tree_dbl(self, _=None):
        sel = self.tree.selection()
        if not sel: return
        item = sel[0]
        vals = self.tree.item(item, "values")
        name = self.tree.item(item, "text").strip()
        if vals and vals[1] == "Folder":
            self._load_dir(f"{self.current_path}/{name}" if self.current_path else name)
        else:
            self._open_file_preview(name)

    def _on_tree_sel(self, _=None):
        sel = self.tree.selection()
        if not sel: return
        item = sel[0]
        vals = self.tree.item(item, "values")
        name = self.tree.item(item, "text").strip()
        if vals and vals[1] == "File":
            self._quick_preview(name)

    def _go_home(self):
        if self.current_repo: self._load_dir("")

    def _go_up(self):
        if not self.current_path: return
        parent = "/".join(self.current_path.rsplit("/",1)[:-1])
        self._load_dir(parent)

    def _refresh_dir(self):
        self._load_dir(self.current_path)

    def _apply_filter(self):
        q = self.filter_var.get().lower()
        if not q:
            self._render_tree(self.all_items["dirs"] + self.all_items["files"])
            self.file_count_lbl.config(text="")
            return
        filtered = ([i for i in self.all_items["dirs"]  if q in i["name"].lower()] +
                    [i for i in self.all_items["files"] if q in i["name"].lower()])
        self._render_tree(filtered)
        self.file_count_lbl.config(text=f"Filter: {len(filtered)} match{'es' if len(filtered)!=1 else ''}")

    def _sort_by(self, col: str):
        if self.sort_col == col:
            self.sort_rev = not self.sort_rev
        else:
            self.sort_col = col; self.sort_rev = False
        key_fns = {"name": lambda i: i.get("name","").lower(),
                   "kind": lambda i: i.get("type",""),
                   "size": lambda i: i.get("size",0)}
        kf = key_fns.get(col, lambda i: "")
        dirs  = sorted(self.all_items["dirs"],  key=kf, reverse=self.sort_rev)
        files = sorted(self.all_items["files"], key=kf, reverse=self.sort_rev)
        self._render_tree(dirs + files)

    # ── File Preview ───────────────────────────────────────────────────────
    def _clear_preview(self):
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.config(state=tk.DISABLED)

    def _quick_preview(self, name: str):
        if not self.current_repo: return
        path   = f"{self.current_path}/{name}" if self.current_path else name
        branch = self.branch_var.get()
        ext    = name.lower().rsplit(".",1)[-1] if "." in name else ""
        if ext in ("png","jpg","jpeg","gif","svg","ico","webp","bmp","pdf","zip","tar","gz","rar"):
            return
        self._set_preview_text(f"Loading {name}…")

        def _work():
            try:
                r = rget(self.session,
                         f"{self.api_base}/repos/{self.username}/{self.current_repo}/contents/{path}",
                         params={"ref":branch} if branch else {}, timeout=15)
                self._parse_rl(r)
                if r.status_code == 200:
                    content = r.json().get("content","")
                    try:
                        text = base64.b64decode(content).decode("utf-8", errors="replace")
                    except Exception:
                        text = "[Binary file — cannot preview]"
                    lang = lang_from_name(name)
                    self.root.after(0, lambda: self._set_preview_text(text, lang))
            except Exception as e:
                self.root.after(0, lambda: self._set_preview_text(f"Error: {e}"))

        threading.Thread(target=_work, daemon=True).start()

    def _set_preview_text(self, text: str, lang: str = "text"):
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", text[:50000])
        if lang != "text":
            SyntaxHL.apply(self.preview_text, lang, self.C)
        self.preview_text.config(state=tk.DISABLED)

    def _preview_selected(self):
        sel = self.tree.selection()
        if not sel: return
        item = sel[0]
        vals = self.tree.item(item, "values")
        name = self.tree.item(item, "text").strip()
        if not (vals and vals[1] == "File"): return
        path   = f"{self.current_path}/{name}" if self.current_path else name
        branch = self.branch_var.get()
        self._set_status(f"Loading {name}…")

        def _work():
            try:
                r = rget(self.session,
                         f"{self.api_base}/repos/{self.username}/{self.current_repo}/contents/{path}",
                         params={"ref":branch} if branch else {}, timeout=15)
                self._parse_rl(r)
                if r.status_code == 200:
                    content = r.json().get("content","")
                    size    = r.json().get("size", 0)
                    try:
                        text = base64.b64decode(content).decode("utf-8", errors="replace")
                    except Exception:
                        text = "[Binary file]"
                    self.root.after(0, lambda: self._open_preview_win(
                        name, text, fmt_size(size), lang_from_name(name)))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(str(e), "err"))

        threading.Thread(target=_work, daemon=True).start()

    def _open_preview_win(self, name: str, text: str, size: str, lang: str):
        C = self.C
        win = tk.Toplevel(self.root)
        win.title(f"{name}  —  GitView")
        win.geometry("1060x720")
        win.configure(bg=C["bg"])
        self._preview_wins.append(win)
        win.protocol("WM_DELETE_WINDOW",
                     lambda: (self._preview_wins.remove(win) if win in self._preview_wins else None,
                              win.destroy()))
        tk.Frame(win, bg=C["accent"], height=2).pack(fill=tk.X)
        hdr = tk.Frame(win, bg=C["surface"], height=46)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        hi = tk.Frame(hdr, bg=C["surface"])
        hi.pack(fill=tk.BOTH, expand=True, padx=14)
        tk.Label(hi, text=f"{file_icon(name)}  {name}", bg=C["surface"], fg=C["fg"],
                 font=(FTIT,11,"bold")).pack(side=tk.LEFT, pady=8)
        tk.Label(hi, text=f"  ·  {size}  ·  {lang.capitalize()}  ·  {self.current_repo}",
                 bg=C["surface"], fg=C["fg_muted"], font=(FUI,9)).pack(side=tk.LEFT)
        for txt, cmd, sty in [
            ("✕  Close",    win.destroy,                                         "ghost"),
            ("📥  Download", lambda: self._dl_single(name),                     "accent"),
            ("📋  Copy",     lambda: (win.clipboard_clear(), win.clipboard_append(text),
                                     self._set_status("Copied","ok")),           "ghost"),
        ]:
            btn(hi, txt, cmd, style=sty, C=C, font=(FUI,9), pady=4
                ).pack(side=tk.RIGHT, padx=3, pady=8)
        code_f = tk.Frame(win, bg=C["surface"])
        code_f.pack(fill=tk.BOTH, expand=True)
        line_count = text.count("\n") + 1
        ln = tk.Text(code_f, width=5, wrap=tk.NONE, bg=C["surface2"], fg=C["fg_subtle"],
                     font=(FMONO,10), relief=tk.FLAT, highlightthickness=0,
                     state=tk.NORMAL, selectbackground=C["surface2"])
        ln.insert("1.0", "\n".join(str(i) for i in range(1, line_count+1)))
        ln.config(state=tk.DISABLED)
        ln.pack(side=tk.LEFT, fill=tk.Y)
        txt_w = tk.Text(code_f, wrap=tk.NONE, bg=C["surface"], fg=C["fg"],
                        font=(FMONO,10), relief=tk.FLAT, highlightthickness=0,
                        insertbackground=C["fg"], selectbackground=C["tree_select"],
                        padx=12, pady=8)
        vsb = ttk.Scrollbar(code_f, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(win,    orient=tk.HORIZONTAL, command=txt_w.xview)
        def sync(*a):
            txt_w.yview(*a); ln.yview(*a)
        vsb.config(command=sync)
        txt_w.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        ln.configure(yscrollcommand=vsb.set)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        txt_w.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        txt_w.insert("1.0", text)
        txt_w.config(state=tk.DISABLED)
        SyntaxHL.apply(txt_w, lang, C)

    # ── Search: Core ───────────────────────────────────────────────────────
    def _debounce_search(self, *_):
        if self._debounce_id:
            try: self.root.after_cancel(self._debounce_id)
            except Exception: pass
        q = self.usearch_var.get().strip()
        if len(q) >= 3:
            self._debounce_id = self.root.after(600, self._do_search)

    def _do_search(self, _=None):
        if not self.username:
            messagebox.showwarning("GitView", "Connect a GitHub account first.")
            return
        q = self.usearch_var.get().strip()
        if not q:
            self._set_status("Enter a search term","warn"); return
        if len(q) < 2:
            self._set_status("Term too short","warn"); return

        if q not in self.search_history:
            self.search_history.appendleft(q)
        else:
            self.search_history.remove(q); self.search_history.appendleft(q)

        scope = self.scope_var.get()
        self._result_page = 1
        self._results = []
        for w in self.res_inner.winfo_children(): w.destroy()
        tk.Label(self.res_inner, text="🔄  Searching…", bg=self.C["bg"],
                 fg=self.C["fg_muted"], font=(FUI,11)).pack(pady=40)
        self.search_count_lbl.config(text="Searching…")
        self.search_prog_lbl.config(text=f"● {scope}…")
        self.search_cancel_btn.config(state=tk.NORMAL)
        self.search_go_btn.config(state=tk.DISABLED)
        self.search_cancel.clear()
        try: self.nb.select(1)
        except Exception: pass

        def _work():
            try:
                dispatch = {
                    "Repos":   self._search_repos,
                    "Content": self._search_content,
                    "Files":   self._search_files,
                    "Commits": self._search_commits,
                    "Topics":  self._search_topics,
                }
                results = dispatch.get(scope, self._search_repos)(q)
                if not self.search_cancel.is_set():
                    self.root.after(0, lambda: self._display_results(results, scope, q))
            except Exception as e:
                if not self.search_cancel.is_set():
                    self.root.after(0, lambda: self._set_status(f"Search error: {e}", "err"))
                    self.root.after(0, lambda: self.search_prog_lbl.config(text=""))
            finally:
                self.root.after(0, lambda: self.search_cancel_btn.config(state=tk.DISABLED))
                self.root.after(0, lambda: self.search_go_btn.config(state=tk.NORMAL))

        threading.Thread(target=_work, daemon=True).start()

    def _select_scope(self, scope: str):
        self.scope_var.set(scope)
        C = self.C
        for s, b in self._scope_btns.items():
            b.config(bg=C["accent"] if s==scope else C["surface2"],
                     fg="#fff" if s==scope else C["fg_muted"],
                     activebackground=C["accent_hover"] if s==scope else C["surface3"])

    def _cancel_search(self):
        self.search_cancel.set()
        self.search_cancel_btn.config(state=tk.DISABLED)
        self.search_go_btn.config(state=tk.NORMAL)
        self.search_prog_lbl.config(text="")
        self._set_status("Search cancelled")

    # ── Search Backends ────────────────────────────────────────────────────
    def _search_repos(self, q: str) -> List[Dict]:
        results = []
        lq = q.lower(); lang_f = self.filter_lang_var.get().strip().lower()
        for key, rd in self.repo_data.items():
            lang = (rd.get("language") or "").lower()
            if lang_f and lang_f not in lang: continue
            sc = SearchEngine.rank_repo(lq, rd)
            if sc > 0:
                results.append({"type":"repo","key":key,"data":rd,"_score":sc})
        results.sort(key=lambda x: x["_score"], reverse=True)
        return results

    def _search_topics(self, q: str) -> List[Dict]:
        ql = q.lower(); results = []
        for key, rd in self.repo_data.items():
            lang   = (rd.get("language") or "").lower()
            topics = [t.lower() for t in rd.get("topics",[])]
            sc = 0
            if ql == lang:                       sc += 100
            elif ql in lang:                     sc += 60
            if ql in topics:                     sc += 90
            if any(ql in t for t in topics):     sc += 40
            if sc > 0:
                results.append({"type":"repo","key":key,"data":rd,"_score":sc})
        results.sort(key=lambda x: x["_score"], reverse=True)
        return results

    def _search_content(self, q: str) -> List[Dict]:
        results = []
        lang_f = self.filter_lang_var.get().strip()
        ext_f  = self.filter_ext_var.get().strip()
        query  = f"{q} user:{self.username}"
        if lang_f: query += f" language:{lang_f}"
        if ext_f:  query += f" extension:{ext_f.lstrip('.')}"
        hdrs = {"Accept":"application/vnd.github.text-match+json"}
        if self.auth_mode=="token" and self.token:
            hdrs["Authorization"] = f"token {self.token}"
        page = 1
        while page <= 3:
            if self.search_cancel.is_set(): break
            try:
                r = rget(self.session, f"{self.api_base}/search/code",
                         params={"q":query,"per_page":30,"page":page},
                         headers=hdrs, timeout=25)
                self._parse_rl(r)
                if r.status_code == 200:
                    items = r.json().get("items",[])
                    for item in items:
                        results.append({"type":"content","key":str(id(item))+str(page),
                                        "data":item,"_score":100})
                    if len(items) < 30: break
                    page += 1; time.sleep(0.5)
                elif r.status_code == 403:
                    results.append({"type":"error","key":"err403","data":{
                        "message":"⚠️  Content search requires token auth.\nSwitch to Token mode."}})
                    break
                elif r.status_code == 422:
                    results.append({"type":"error","key":"err422","data":{
                        "message":"⚠️  Search term invalid. Use 3+ characters or exact phrases."}})
                    break
                elif r.status_code == 429:
                    time.sleep(10); continue
                else:
                    msg = r.json().get("message",f"HTTP {r.status_code}")
                    results.append({"type":"error","key":"errmsg","data":{"message":f"API: {msg}"}})
                    break
            except Exception as e:
                results.append({"type":"error","key":"errnet","data":{"message":f"Network: {e}"}})
                break
        return results

    def _search_files(self, q: str) -> List[Dict]:
        results = []
        lang_f = self.filter_lang_var.get().strip()
        ext_f  = self.filter_ext_var.get().strip()
        query  = f"filename:{q} user:{self.username}"
        if lang_f: query += f" language:{lang_f}"
        if ext_f:  query += f" extension:{ext_f.lstrip('.')}"
        hdrs = {"Accept":"application/vnd.github.text-match+json"}
        if self.auth_mode=="token" and self.token:
            hdrs["Authorization"] = f"token {self.token}"
        try:
            r = rget(self.session, f"{self.api_base}/search/code",
                     params={"q":query,"per_page":50}, headers=hdrs, timeout=25)
            self._parse_rl(r)
            if r.status_code == 200:
                for item in r.json().get("items",[]):
                    sc = SearchEngine.score(q.lower(), item.get("name",""))
                    sc += int(recency_score(
                        self.repo_data.get(item.get("repository",{}).get("full_name",""),{})
                        .get("updated_at","")) * 20)
                    results.append({"type":"file","key":str(id(item)),"data":item,"_score":sc})
                results.sort(key=lambda x: x["_score"], reverse=True)
            elif r.status_code == 403:
                results.append({"type":"error","key":"err403","data":{
                    "message":"⚠️  File search requires token authentication."}})
            elif r.status_code == 422:
                results.append({"type":"error","key":"err422","data":{
                    "message":"⚠️  Filename too short. Use 3+ characters."}})
        except Exception as e:
            results.append({"type":"error","key":"errnet","data":{"message":f"Network: {e}"}})
        return results

    def _search_commits(self, q: str) -> List[Dict]:
        results = []
        hdrs = {"Accept":"application/vnd.github.cloak-preview+json"}
        if self.auth_mode=="token" and self.token:
            hdrs["Authorization"] = f"token {self.token}"
        try:
            r = rget(self.session, f"{self.api_base}/search/commits",
                     params={"q":f"{q} author:{self.username}","per_page":50},
                     headers=hdrs, timeout=25)
            self._parse_rl(r)
            if r.status_code == 200:
                for item in r.json().get("items",[]):
                    sc = SearchEngine.rank_commit(q, item)
                    results.append({"type":"commit","key":str(id(item)),"data":item,"_score":sc})
                results.sort(key=lambda x: x["_score"], reverse=True)
            elif r.status_code == 403:
                results.append({"type":"error","key":"err403","data":{
                    "message":"⚠️  Commit search requires token authentication."}})
            elif r.status_code == 422:
                results = self._search_commits_local(q)
        except Exception as e:
            results.append({"type":"error","key":"errnet","data":{"message":f"Network: {e}"}})
        return results

    def _search_commits_local(self, q: str) -> List[Dict]:
        results = []; ql = q.lower()
        for key, rd in list(self.repo_data.items())[:8]:
            if self.search_cancel.is_set(): break
            try:
                r = rget(self.session,
                         f"{self.api_base}/repos/{self.username}/{rd.get('name','')}/commits",
                         params={"per_page":30}, timeout=12)
                if r.status_code == 200:
                    for cd in r.json():
                        msg = (cd.get("commit",{}).get("message","") or "").lower()
                        if ql in msg:
                            cd["repository"] = {"full_name": key}
                            sc = SearchEngine.rank_commit(q, cd)
                            results.append({"type":"commit","key":str(id(cd)),"data":cd,"_score":sc})
            except Exception: pass
        results.sort(key=lambda x: x["_score"], reverse=True)
        return results

    # ── Search Result Display ──────────────────────────────────────────────
    def _display_results(self, results: List[Dict], scope: str, q: str):
        self._results = results
        self._result_page = 1
        errors = [r for r in results if r.get("type")=="error"]
        good   = [r for r in results if r.get("type")!="error"]
        count  = len(good)
        self.search_prog_lbl.config(text="")
        self.search_count_lbl.config(text=f"{'No' if count==0 else count} result{'s' if count!=1 else ''}")
        self._set_status(f"Found {count} result{'s' if count!=1 else ''} for '{q}'  [{scope}]",
                         "ok" if count > 0 else "warn")
        self._log(f"Search [{scope}] '{q}' → {count} results")
        if errors:
            self._show_error_card(errors[0]["data"].get("message","Error")); return
        self._sort_results()
        self._render_page()

    def _sort_results(self):
        pref = self.sort_var.get()
        if pref == "name":
            def key(r):
                d = r.get("data",{})
                if r["type"]=="repo":   return d.get("name","").lower()
                if r["type"]=="commit": return (d.get("commit",{}).get("message","") or "").lower()
                return d.get("name","").lower()
            self._results.sort(key=key)
        elif pref == "date":
            def key(r):
                d = r.get("data",{})
                if r["type"]=="repo":   return d.get("updated_at","") or ""
                if r["type"]=="commit":
                    return (d.get("commit",{}).get("author") or {}).get("date","") or ""
                return ""
            self._results.sort(key=key, reverse=True)
        elif pref == "activity":
            def key(r):
                d = r.get("data",{})
                if r["type"]=="repo":
                    return (d.get("stargazers_count",0) +
                            int(recency_score(d.get("pushed_at","")) * 200))
                return r.get("_score",0)
            self._results.sort(key=key, reverse=True)

    def _resort(self):
        if not self._results: return
        self._sort_results()
        self._result_page = 1
        self._render_page()

    def _go_page(self, delta: int):
        good  = [r for r in self._results if r.get("type")!="error"]
        total = len(good)
        max_p = max(1, (total + RPP - 1) // RPP)
        new   = max(1, min(max_p, self._result_page + delta))
        if new != self._result_page:
            self._result_page = new
            self._render_page()

    def _render_page(self):
        C    = self.C
        q    = self.usearch_var.get().strip()
        data = [r for r in self._results if r.get("type")!="error"]
        total = len(data)
        max_p = max(1, (total + RPP - 1) // RPP)
        page  = min(self._result_page, max_p)
        self._result_page = page
        start = (page-1) * RPP
        items = data[start:start+RPP]
        self.pager_lbl.config(text=f"Page {page} / {max_p}")
        self.pager_prev.config(state=tk.NORMAL if page > 1       else tk.DISABLED)
        self.pager_next.config(state=tk.NORMAL if page < max_p   else tk.DISABLED)
        for w in self.res_inner.winfo_children(): w.destroy()
        if not items:
            f = tk.Frame(self.res_inner, bg=C["bg"]); f.pack(pady=50)
            tk.Label(f, text="🔎  No results found", bg=C["bg"], fg=C["fg_muted"],
                     font=(FTIT,13,"bold")).pack()
            tk.Label(f, text="Try a different keyword or scope", bg=C["bg"],
                     fg=C["fg_subtle"], font=(FUI,9)).pack(pady=(4,0))
            return
        for entry in items:
            self._render_card(entry, q)
        self.res_canvas.yview_moveto(0)

    def _render_card(self, entry: Dict, q: str):
        C     = self.C
        etype = entry.get("type","")
        data  = entry.get("data",{})
        TYPE_CONF = {
            "repo":    ("📦","REPO",    C["accent_subtle"],  C["accent"]),
            "content": ("📄","CONTENT", C["purple_subtle"],  C["purple"]),
            "file":    ("🗂","FILE",    C["purple_subtle"],  C["purple"]),
            "commit":  ("🕐","COMMIT",  C["cyan_subtle"],    C["cyan"]),
        }
        icon_txt, badge_txt, badge_bg, badge_fg = TYPE_CONF.get(
            etype, ("📄", etype.upper(), C["surface2"], C["fg_muted"]))
        if etype in ("content","file"):
            icon_txt = file_icon(data.get("name",""))

        card = tk.Frame(self.res_inner, bg=C["card"],
                        highlightbackground=C["border"], highlightthickness=1,
                        cursor="hand2")
        card.pack(fill=tk.X, padx=8, pady=3)
        inner = tk.Frame(card, bg=C["card"])
        inner.pack(fill=tk.X, padx=12, pady=10)

        ic = tk.Frame(inner, bg=C["card"])
        ic.pack(side=tk.LEFT, padx=(0,10))
        tk.Label(ic, text=icon_txt,   bg=C["card"], fg=C["fg"], font=(FUI,18)).pack(pady=2)
        tk.Label(ic, text=badge_txt,  bg=badge_bg,  fg=badge_fg,
                 font=(FUI,6,"bold"), padx=4, pady=1).pack()

        cc = tk.Frame(inner, bg=C["card"])
        cc.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hr = tk.Frame(cc, bg=C["card"])
        hr.pack(fill=tk.X)

        if etype == "repo":
            name   = data.get("name","")
            stars  = data.get("stargazers_count",0)
            lang   = data.get("language") or ""
            upd    = rel_time(data.get("updated_at",""))
            pushed = rel_time(data.get("pushed_at",""))
            desc   = (data.get("description") or "No description")[:120]
            topics = data.get("topics",[])[:5]
            is_priv= data.get("private",False)
            sc     = entry.get("_score",0)
            nl = tk.Label(hr, text=name, bg=C["card"], fg=C["accent_hover"],
                          font=(FTIT,11,"bold"), cursor="hand2")
            nl.pack(side=tk.LEFT)
            if is_priv:
                tk.Label(hr, text="🔒", bg=C["card"], fg=C["fg_subtle"],
                         font=(FUI,9)).pack(side=tk.LEFT, padx=4)
            meta = f"  ★{stars:,}"
            if lang: meta += f"  ·  {lang}"
            meta += f"  ·  updated {upd}"
            if pushed != upd: meta += f"  ·  pushed {pushed}"
            meta += f"  ·  score {sc}"
            tk.Label(hr, text=meta, bg=C["card"], fg=C["fg_muted"],
                     font=(FUI,8)).pack(side=tk.LEFT, padx=6)
            tk.Label(cc, text=desc, bg=C["card"], fg=C["fg_muted"],
                     font=(FUI,9), anchor=tk.W).pack(fill=tk.X, pady=(2,0))
            if topics:
                tr = tk.Frame(cc, bg=C["card"])
                tr.pack(fill=tk.X, pady=(4,0))
                for t in topics:
                    tk.Label(tr, text=t, bg=C["accent_subtle"], fg=C["accent"],
                             font=(FUI,7), padx=5, pady=1).pack(side=tk.LEFT, padx=(0,3))

        elif etype in ("content","file"):
            name = data.get("name","")
            path = data.get("path","")
            repo = data.get("repository",{}).get("full_name","")
            nl = tk.Label(hr, text=name, bg=C["card"], fg=C["accent_hover"],
                          font=(FTIT,11,"bold"), cursor="hand2")
            nl.pack(side=tk.LEFT)
            tk.Label(hr, text=f"  in  {repo}", bg=C["card"], fg=C["fg_subtle"],
                     font=(FUI,8)).pack(side=tk.LEFT)
            if path != name:
                tk.Label(cc, text=f"📂  {path}", bg=C["card"], fg=C["fg_subtle"],
                         font=(FMONO,8)).pack(anchor=tk.W, pady=(2,0))
            frags = data.get("text_matches",[])
            if frags:
                ff = tk.Frame(cc, bg=C["surface2"],
                              highlightbackground=C["border"], highlightthickness=1)
                ff.pack(fill=tk.X, pady=(6,0))
                for frag in frags[:2]:
                    ft = frag.get("fragment","").strip()
                    if ft: self._render_fragment(ff, ft, q)

        elif etype == "commit":
            commit  = data.get("commit",{})
            msg     = (commit.get("message","") or "").split("\n")[0][:100]
            sha     = data.get("sha","")[:10]
            repo    = data.get("repository",{}).get("full_name","")
            author  = (commit.get("author") or {}).get("name","")
            dstr    = rel_time((commit.get("author") or {}).get("date",""))
            tk.Label(hr, text=msg, bg=C["card"], fg=C["fg"],
                     font=(FUI,10,"bold")).pack(side=tk.LEFT)
            meta = f"  {sha}  ·  {author}  ·  {dstr}"
            if repo: meta += f"  ·  {repo}"
            tk.Label(cc, text=meta, bg=C["card"], fg=C["fg_muted"],
                     font=(FMONO,8)).pack(anchor=tk.W, pady=(2,0))

        def click(e=None, ent=entry): self._on_card_click(ent)
        def enter(e=None): card.config(highlightbackground=C["accent"])
        def leave(e=None): card.config(highlightbackground=C["border"])
        for w in [card, inner, cc, hr]:
            w.bind("<Button-1>", click)
            w.bind("<Enter>",    enter)
            w.bind("<Leave>",    leave)

    def _render_fragment(self, parent, fragment: str, q: str):
        C = self.C
        ft = tk.Text(parent, wrap=tk.WORD, bg=C["surface2"], fg=C["fg_muted"],
                     font=(FMONO,8), relief=tk.FLAT, highlightthickness=0,
                     height=3, padx=8, pady=4)
        ft.pack(fill=tk.X)
        ft.insert("1.0", fragment)
        ft.tag_configure("hl", background=C["hl_bg"], foreground=C["hl_fg"],
                         font=(FMONO,8,"bold"))
        ql = q.lower(); cl = fragment.lower()
        start = 0
        while True:
            i = cl.find(ql, start)
            if i == -1: break
            ft.tag_add("hl", f"1.0+{i}c", f"1.0+{i+len(ql)}c")
            start = i + 1
        ft.config(state=tk.DISABLED)

    def _show_search_empty(self):
        C = self.C
        for w in self.res_inner.winfo_children(): w.destroy()
        f = tk.Frame(self.res_inner, bg=C["bg"]); f.pack(pady=60)
        tk.Label(f, text="🔍", bg=C["bg"], fg=C["fg_subtle"], font=(FUI,36)).pack()
        tk.Label(f, text="Search within loaded user", bg=C["bg"], fg=C["fg_muted"],
                 font=(FTIT,13,"bold")).pack(pady=(8,0))
        tk.Label(f, text="Connect a GitHub account, then search\nrepos · content · files · commits · topics",
                 bg=C["bg"], fg=C["fg_subtle"], font=(FUI,9), justify=tk.CENTER).pack(pady=(6,0))

    def _show_error_card(self, msg: str):
        C = self.C
        for w in self.res_inner.winfo_children(): w.destroy()
        f = tk.Frame(self.res_inner, bg=C["danger_subtle"],
                     highlightbackground=C["danger"], highlightthickness=1)
        f.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(f, text="⚠️  Search Note", bg=C["danger_subtle"], fg=C["danger"],
                 font=(FUI,10,"bold"), padx=12, pady=8).pack(anchor=tk.W)
        tk.Label(f, text=msg, bg=C["danger_subtle"], fg=C["fg"],
                 font=(FUI,9), padx=12, pady=(0,10), justify=tk.LEFT,
                 wraplength=600).pack(anchor=tk.W)
        self.search_count_lbl.config(text="")
        self.pager_lbl.config(text="Page 0 / 0")

    def _on_card_click(self, entry: Dict):
        C     = self.C
        etype = entry.get("type","")
        data  = entry.get("data",{})
        self.det_text.config(state=tk.NORMAL)
        self.det_text.delete("1.0", tk.END)
        for tag, kw in [
            ("h",  {"font":(FTIT,11,"bold"), "foreground":C["accent_hover"]}),
            ("k",  {"font":(FUI,8,"bold"),   "foreground":C["fg_subtle"]}),
            ("v",  {"font":(FUI,9),          "foreground":C["fg_muted"]}),
            ("vv", {"font":(FMONO,8),        "foreground":C["purple"]}),
        ]:
            self.det_text.tag_configure(tag, **kw)

        def ins(text: str, tag: str = "v"):
            self.det_text.insert(tk.END, text, tag)

        url = ""
        if etype == "repo":
            url = data.get("html_url","")
            ins(data.get("full_name",""), "h"); ins("\n")
            for k, v in [
                ("Language",   data.get("language") or "—"),
                ("Stars",      f"{data.get('stargazers_count',0):,}"),
                ("Forks",      f"{data.get('forks_count',0):,}"),
                ("Watchers",   f"{data.get('watchers_count',0):,}"),
                ("Updated",    rel_time(data.get("updated_at",""))),
                ("Pushed",     rel_time(data.get("pushed_at",""))),
                ("Default",    data.get("default_branch","—")),
                ("License",    (data.get("license") or {}).get("name","—")),
                ("Private",    str(data.get("private",False))),
                ("Fork",       str(data.get("fork",False))),
            ]:
                ins(f"\n{k}  ", "k"); ins(str(v))
            desc = data.get("description") or ""
            if desc:
                ins("\n\nDescription\n", "k"); ins(desc)
            topics = data.get("topics",[])
            if topics:
                ins("\n\nTopics  ", "k"); ins("  ".join(topics),"vv")
            key = data.get("full_name","")
            repo_name = data.get("name","")
            self.det_open_btn.config(command=lambda u=url: webbrowser.open(u))
            self.det_nav_btn.config(command=lambda k=key, rn=repo_name: self._nav_to_repo(k, rn))

        elif etype in ("content","file"):
            url = data.get("html_url","")
            ins(data.get("name",""), "h"); ins("\n")
            ins("\nPath  ", "k"); ins(data.get("path",""))
            repo = data.get("repository",{}).get("full_name","")
            ins("\nRepo  ", "k"); ins(repo)
            ins("\nURL  ",  "k"); ins(url,"vv")
            self.det_open_btn.config(command=lambda u=url: webbrowser.open(u))
            self.det_nav_btn.config(command=lambda: None)

        elif etype == "commit":
            sha  = data.get("sha","")
            url  = data.get("html_url","") or (
                f"https://github.com/{data.get('repository',{}).get('full_name','')}/commit/{sha}")
            commit = data.get("commit",{})
            ins(sha[:10], "h"); ins("\n")
            ins("\nMessage  ", "k"); ins(commit.get("message","")[:300])
            author = commit.get("author") or {}
            ins("\n\nAuthor  ", "k"); ins(author.get("name",""))
            ins("\nEmail  ",   "k"); ins(author.get("email",""))
            ins("\nDate  ",    "k"); ins(rel_time(author.get("date","")))
            repo = data.get("repository",{}).get("full_name","")
            ins("\nRepo  ",    "k"); ins(repo)
            self.det_open_btn.config(command=lambda u=url: webbrowser.open(u))
            self.det_nav_btn.config(command=lambda s=sha: self._show_commit_diff_from_search(data))

        self.det_text.config(state=tk.DISABLED)

    def _nav_to_repo(self, full_name: str, repo_name: str):
        if full_name in self.repo_data:
            self.repo_var.set(full_name)
            self.current_repo = repo_name
            self.current_repo_full = full_name
            self.nb.select(0)
            self._on_repo_sel()

    # ── Search History & Saved Searches ───────────────────────────────────
    def _show_history(self, _=None):
        if not self.search_history: return
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
        for q in list(self.search_history)[:15]:
            lbl = tk.Label(inner, text=f"🕐  {q}", bg=C["surface2"], fg=C["fg"],
                           font=(FUI,9), anchor=tk.W, padx=12, pady=5, cursor="hand2",
                           width=44)
            lbl.pack(fill=tk.X)
            def _pick(query=q, p=popup):
                self.usearch_var.set(query); p.destroy(); self._do_search()
            lbl.bind("<Button-1>", lambda _, fn=_pick: fn())
            lbl.bind("<Enter>",    lambda e, w=lbl: w.config(bg=C["tree_select"]))
            lbl.bind("<Leave>",    lambda e, w=lbl: w.config(bg=C["surface2"]))
        popup.bind("<FocusOut>", lambda _: popup.destroy())
        popup.focus_set()

    def _save_current_search(self):
        q = self.usearch_var.get().strip()
        if not q: return
        if q not in self.saved_searches:
            self.saved_searches.append(q)
            self._save_cfg()
            self._set_status(f"Saved search: {q}","ok")

    def _show_saved_searches(self):
        if not self.saved_searches:
            messagebox.showinfo("GitView","No saved searches yet.\nSearch something and press '➕ Save'.")
            return
        C = self.C
        popup = tk.Toplevel(self.root)
        popup.title("Saved Searches")
        popup.geometry("340x380")
        popup.configure(bg=C["bg"])
        tk.Frame(popup, bg=C["accent"], height=2).pack(fill=tk.X)
        hdr = tk.Frame(popup, bg=C["surface"], height=40)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⭐  Saved Searches", bg=C["surface"], fg=C["fg"],
                 font=(FTIT,11,"bold")).pack(side=tk.LEFT, padx=12, pady=10)
        lb = tk.Listbox(popup, bg=C["surface"], fg=C["fg"], font=(FUI,10),
                        relief=tk.FLAT, highlightthickness=0,
                        selectbackground=C["tree_select"],
                        selectforeground=C["accent_hover"],
                        activestyle="none")
        lb.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        for s in self.saved_searches: lb.insert(tk.END, f"  {s}")
        def _run():
            sel = lb.curselection()
            if sel:
                q = self.saved_searches[sel[0]]
                self.usearch_var.set(q); popup.destroy(); self._do_search()
        def _del():
            sel = lb.curselection()
            if sel:
                self.saved_searches.pop(sel[0])
                lb.delete(sel[0]); self._save_cfg()
        bf = tk.Frame(popup, bg=C["surface"])
        bf.pack(fill=tk.X, padx=10, pady=(0,10))
        btn(bf,"▶  Run",    _run,  style="accent",  C=C, font=(FUI,9)).pack(side=tk.LEFT, padx=(0,4))
        btn(bf,"🗑  Delete", _del, style="danger",  C=C, font=(FUI,9)).pack(side=tk.LEFT)
        btn(bf,"✕  Close",  popup.destroy, style="ghost", C=C, font=(FUI,9)).pack(side=tk.RIGHT)
        lb.bind("<Double-1>", lambda _: _run())

    # ── Commits ────────────────────────────────────────────────────────────
    def _load_commits(self, _=None):
        if not self.current_repo:
            messagebox.showwarning("GitView","Select a repository first."); return
        self._commit_page = 1
        self._commits_cache = {}
        self.commit_tree.delete(*self.commit_tree.get_children())
        self.commit_count_lbl.config(text="Loading…")
        self.progress_bar.start()
        self._fetch_commits(page=1)

    def _load_more_commits(self):
        self._commit_page += 1
        self._fetch_commits(page=self._commit_page)

    def _fetch_commits(self, page: int = 1):
        repo   = self.current_repo
        author = self.commit_author_var.get().strip()
        path   = self.commit_path_var.get().strip()
        msg    = self.commit_msg_var.get().strip()
        branch = self.branch_var.get()

        def _work():
            try:
                params: Dict[str,Any] = {"per_page":50,"page":page}
                if branch: params["sha"]    = branch
                if author: params["author"] = author
                if path:   params["path"]   = path
                r = rget(self.session,
                         f"{self.api_base}/repos/{self.username}/{repo}/commits",
                         params=params, timeout=20)
                self._parse_rl(r)
                if r.status_code == 200:
                    commits = r.json()
                    if msg:
                        ml = msg.lower()
                        commits = [c for c in commits if ml in (c.get("commit",{}).get("message","") or "").lower()]
                    self.root.after(0, lambda cs=commits: self._on_commits_loaded(cs, page))
                else:
                    err = r.json().get("message","Error")
                    self.root.after(0, lambda: self._set_status(f"Commits error: {err}","err"))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(str(e),"err"))
            finally:
                self.root.after(0, self.progress_bar.stop)

        threading.Thread(target=_work, daemon=True).start()

    def _on_commits_loaded(self, commits: List[Dict], page: int):
        if page == 1:
            self.commit_tree.delete(*self.commit_tree.get_children())
        for cd in commits:
            commit = cd.get("commit",{})
            sha    = cd.get("sha","")[:8]
            msg    = (commit.get("message","") or "").split("\n")[0][:90]
            author = (commit.get("author") or {}).get("name","")
            date   = rel_time((commit.get("author") or {}).get("date",""))
            iid    = self.commit_tree.insert("","end",text=f"  {msg}",
                                              values=(sha,author,date))
            self._commits_cache[iid] = cd
        total = len(self.commit_tree.get_children())
        self.commit_count_lbl.config(text=f"{total} commits")
        self._set_status(f"Loaded {len(commits)} commits (page {page})","ok")
        self._log(f"Commits loaded: {len(commits)} for {self.current_repo}")

    def _on_commit_sel(self, _=None):
        sel = self.commit_tree.selection()
        if not sel: return
        cd = self._commits_cache.get(sel[0],{})
        if not cd: return
        self._show_commit_meta(cd)
        self._diff_tabs.select(0)
        sha = cd.get("sha","")
        if sha: self._load_commit_diff(sha)

    def _on_commit_open(self, _=None):
        sel = self.commit_tree.selection()
        if not sel: return
        cd  = self._commits_cache.get(sel[0],{})
        url = cd.get("html_url","")
        if url: webbrowser.open(url)

    def _show_commit_meta(self, cd: Dict):
        C  = self.C
        t  = self.commit_meta_text
        t.config(state=tk.NORMAL)
        t.delete("1.0", tk.END)
        for tag, kw in [
            ("h",  {"font":(FTIT,12,"bold"), "foreground":C["accent_hover"]}),
            ("k",  {"font":(FUI,8,"bold"),   "foreground":C["fg_subtle"]}),
            ("v",  {"font":(FUI,9),          "foreground":C["fg_muted"]}),
            ("m",  {"font":(FMONO,9),        "foreground":C["fg"]}),
            ("sha",{"font":(FMONO,10,"bold"),"foreground":C["purple"]}),
        ]:
            t.tag_configure(tag, **kw)

        sha    = cd.get("sha","")
        commit = cd.get("commit",{})
        msg    = commit.get("message","")
        author = commit.get("author") or {}
        cmtr   = commit.get("committer") or {}
        stats  = cd.get("stats",{})
        files  = cd.get("files",[])

        t.insert(tk.END, sha[:16], "sha"); t.insert(tk.END, "\n")
        t.insert(tk.END, "\nMessage\n", "k"); t.insert(tk.END, msg, "m")
        t.insert(tk.END, "\n\nAuthor  ",   "k"); t.insert(tk.END, author.get("name",""),  "v")
        t.insert(tk.END, "\nEmail   ",     "k"); t.insert(tk.END, author.get("email",""), "v")
        t.insert(tk.END, "\nDate    ",     "k"); t.insert(tk.END, rel_time(author.get("date","")), "v")
        if cmtr.get("name","") != author.get("name",""):
            t.insert(tk.END, "\nCommitter  ","k"); t.insert(tk.END, cmtr.get("name",""),"v")
        parents = cd.get("parents",[])
        if parents:
            t.insert(tk.END, "\n\nParents  ", "k")
            for p in parents:
                t.insert(tk.END, p.get("sha","")[:10]+" ", "sha")
        if stats:
            t.insert(tk.END, "\n\nStats  ", "k")
            t.insert(tk.END, f"+{stats.get('additions',0)}  -{stats.get('deletions',0)}  ~{stats.get('total',0)} lines", "v")
        if files:
            t.insert(tk.END, f"\n\nFiles changed  ({len(files)})\n", "k")
            for fi in files:
                status = fi.get("status","")
                fn     = fi.get("filename","")
                adds   = fi.get("additions",0)
                dels   = fi.get("deletions",0)
                t.insert(tk.END, f"  [{status[:1].upper()}] {fn}  +{adds} -{dels}\n","v")
        t.config(state=tk.DISABLED)

        sha_full = sha
        url = cd.get("html_url","")
        self.commit_open_btn.config(command=lambda u=url: webbrowser.open(u))
        self.commit_copy_btn.config(command=lambda s=sha_full: (
            self.root.clipboard_clear(), self.root.clipboard_append(s),
            self._set_status("SHA copied","ok")))

    def _load_commit_diff(self, sha: str):
        if sha in self._diff_cache:
            self._render_diff(self._diff_cache[sha]); return
        self.diff_loading_lbl.config(text="Loading diff…")
        self.diff_text.config(state=tk.NORMAL)
        self.diff_text.delete("1.0", tk.END)
        self.diff_text.config(state=tk.DISABLED)

        def _work():
            try:
                r = rget(self.session,
                         f"{self.api_base}/repos/{self.username}/{self.current_repo}/commits/{sha}",
                         headers={"Accept":"application/vnd.github.diff"}, timeout=20)
                self._parse_rl(r)
                if r.status_code == 200:
                    raw = r.text
                    self._diff_cache[sha] = raw
                    if len(self._diff_cache) > 50:
                        oldest = next(iter(self._diff_cache))
                        del self._diff_cache[oldest]
                    self.root.after(0, lambda: self._render_diff(raw))
                else:
                    self.root.after(0, lambda: self.diff_loading_lbl.config(
                        text=f"Diff unavailable ({r.status_code})"))
            except Exception as e:
                self.root.after(0, lambda: self.diff_loading_lbl.config(text=f"Error: {e}"))

        threading.Thread(target=_work, daemon=True).start()

    def _render_diff(self, raw: str):
        self.diff_loading_lbl.config(text="")
        self._current_diff_raw = raw
        files = DiffParser.parse(raw)
        self._diff_files = files
        adds, dels = DiffParser.stats(files)
        self.diff_stats_lbl.config(text=f"+{adds}  -{dels}")

        self.diff_file_tree.delete(*self.diff_file_tree.get_children())
        for fi in files:
            path = fi.get("path","")
            ico  = file_icon(path) if path else "📄"
            self.diff_file_tree.insert("","end", text=f"{ico}  {path}")

        if files:
            children = self.diff_file_tree.get_children()
            if children:
                self.diff_file_tree.selection_set(children[0])
                self._render_diff_file(files[0])

    def _on_diff_file_sel(self, _=None):
        sel = self.diff_file_tree.selection()
        if not sel: return
        idx = self.diff_file_tree.index(sel[0])
        if idx < len(self._diff_files):
            self._render_diff_file(self._diff_files[idx])

    def _redraw_diff(self):
        sel = self.diff_file_tree.selection()
        if not sel or not self._diff_files: return
        idx = self.diff_file_tree.index(sel[0])
        if idx < len(self._diff_files):
            self._render_diff_file(self._diff_files[idx])

    def _render_diff_file(self, fi: Dict):
        C    = self.C
        t    = self.diff_text
        mode = self.diff_mode_var.get()
        t.config(state=tk.NORMAL)
        t.delete("1.0", tk.END)
        for tag, bg, fg in [
            ("add",  C["diff_add"],  C["diff_add_fg"]),
            ("del",  C["diff_del"],  C["diff_del_fg"]),
            ("hunk", C["diff_hunk"], C["diff_hunk_fg"]),
            ("ctx",  C["surface"],   C["fg_muted"]),
        ]:
            t.tag_configure(tag, background=bg, foreground=fg, font=(FMONO,9))

        path = fi.get("path","")
        t.insert(tk.END, f"{'─'*60}\n  {path}\n{'─'*60}\n", "hunk")

        for hunk in fi.get("hunks",[]):
            t.insert(tk.END, f"\n{hunk.get('header','')}\n", "hunk")
            if mode == "unified":
                for kind, line in hunk.get("lines",[]):
                    prefix = {"add":"+", "del":"-", "ctx":" "}.get(kind," ")
                    t.insert(tk.END, f"{prefix} {line}\n", kind)
            else:
                left_lines  = [(k,l) for k,l in hunk.get("lines",[]) if k in ("del","ctx")]
                right_lines = [(k,l) for k,l in hunk.get("lines",[]) if k in ("add","ctx")]
                width = 55
                for i in range(max(len(left_lines), len(right_lines))):
                    lk, ll = left_lines[i]  if i < len(left_lines)  else ("ctx","")
                    rk, rl = right_lines[i] if i < len(right_lines) else ("ctx","")
                    left_s  = f"{'─' if lk=='del' else ' '} {ll:<{width}}"
                    right_s = f"{'+'  if rk=='add' else ' '} {rl}"
                    t.insert(tk.END, left_s,  lk)
                    t.insert(tk.END, " │ ", "ctx")
                    t.insert(tk.END, right_s + "\n", rk)

        t.config(state=tk.DISABLED)

    def _show_commit_diff_from_search(self, cd: Dict):
        sha  = cd.get("sha","")
        repo = cd.get("repository",{}).get("full_name","")
        if not sha: return
        repo_name = repo.split("/")[-1] if "/" in repo else repo
        prev_repo = self.current_repo
        if repo_name and repo_name != self.current_repo:
            self.current_repo = repo_name
        self.nb.select(2)
        self._show_commit_meta(cd)
        self._diff_tabs.select(0)
        if sha: self._load_commit_diff(sha)
        if prev_repo and repo_name != prev_repo:
            self.current_repo = prev_repo

    # ── Download ───────────────────────────────────────────────────────────
    def _dl_selected(self):
        if not self.current_repo:
            messagebox.showwarning("GitView","Select a repository first."); return
        sel = self.tree.selection()
        items = []
        for iid in sel:
            vals = self.tree.item(iid,"values")
            name = self.tree.item(iid,"text").strip()
            if vals and vals[1]=="File":
                path = f"{self.current_path}/{name}" if self.current_path else name
                items.append((name, path))
        if not items:
            messagebox.showinfo("GitView","Select one or more files."); return
        dest = filedialog.askdirectory(title="Choose Download Destination")
        if dest: self._start_dl(items, dest)

    def _dl_single(self, name: str):
        path = f"{self.current_path}/{name}" if self.current_path else name
        dest = filedialog.askdirectory(title="Choose Download Destination")
        if dest: self._start_dl([(name, path)], dest)

    def _start_dl(self, items: List[Tuple[str,str]], dest: str):
        self._set_status(f"Downloading {len(items)} file(s)…")
        self.progress_bar.start()
        branch = self.branch_var.get()
        total  = len(items)

        def _work():
            done, errs = 0, []
            for name, path in items:
                try:
                    r = rget(self.session,
                             f"{self.api_base}/repos/{self.username}/{self.current_repo}/contents/{path}",
                             params={"ref":branch} if branch else {}, timeout=20)
                    self._parse_rl(r)
                    if r.status_code == 200:
                        data = r.json().get("content","")
                        with open(os.path.join(dest, name), "wb") as fh:
                            fh.write(base64.b64decode(data))
                        done += 1
                        self.root.after(0, lambda d=done: self.progress_var.set(f"Downloaded {d}/{total}…"))
                    else:
                        errs.append(name)
                except Exception as e:
                    errs.append(f"{name}: {e}")
            self.root.after(0, self.progress_bar.stop)
            msg = f"Downloaded {done}/{total} file(s) to {dest}"
            if errs: self.root.after(0, lambda: messagebox.showwarning("GitView",
                                     msg + "\n\nErrors:\n" + "\n".join(errs[:5])))
            else:    self.root.after(0, lambda: self._set_status(msg,"ok"))
            self.root.after(0, lambda: self.progress_var.set("No active operations"))
            self.root.after(0, lambda: self._log(f"Downloaded {done}/{total}"))

        threading.Thread(target=_work, daemon=True).start()

    def _dl_entire(self):
        if not self.current_repo:
            messagebox.showwarning("GitView","Select a repository first."); return
        dest = filedialog.askdirectory(title="Choose Download Destination")
        if not dest: return
        branch = self.branch_var.get()
        webbrowser.open(f"https://github.com/{self.username}/{self.current_repo}"
                        f"/archive/refs/heads/{branch}.zip")
        self._set_status(f"Opening download for {self.current_repo}…","ok")
        self._log(f"Download repo: {self.current_repo} ({branch})")

    def _dl_folder(self):
        if not self.current_repo: return
        dest = filedialog.askdirectory(title="Choose Download Destination")
        if not dest: return
        items = [(f["name"], f.get("path","")) for f in self.all_items["files"]]
        if items: self._start_dl(items, dest)
        else: self._set_status("No files in current folder","warn")

    # ── Upload & Create ────────────────────────────────────────────────────
    def _check_write(self) -> bool:
        if self.auth_mode=="public" or not self.token:
            messagebox.showwarning("Read Only",
                "Uploading requires Token mode.\n"
                "Switch to Token mode and connect with a Personal Access Token.")
            return False
        if not self.current_repo:
            messagebox.showwarning("GitView","Select a repository first."); return False
        return True

    def _upload_file(self):
        if not self._check_write(): return
        path = filedialog.askopenfilename(title="Choose File to Upload")
        if not path: return
        name = os.path.basename(path)
        dest = simpledialog.askstring("Upload Path",
            f"Upload path in repository\n(leave blank for root):", parent=self.root)
        if dest is None: return
        dest_path = f"{dest}/{name}" if dest.strip() else name
        self._set_status(f"Uploading {name}…")
        self.progress_bar.start()
        branch = self.branch_var.get()

        def _work():
            try:
                with open(path,"rb") as fh:
                    content = base64.b64encode(fh.read()).decode()
                r = rget(self.session,
                         f"{self.api_base}/repos/{self.username}/{self.current_repo}/contents/{dest_path}",
                         timeout=10)
                sha = r.json().get("sha","") if r.status_code==200 else ""
                payload: Dict[str,Any] = {
                    "message": f"Upload {name} via GitView",
                    "content": content,
                    "branch":  branch,
                }
                if sha: payload["sha"] = sha
                r2 = self.session.put(
                    f"{self.api_base}/repos/{self.username}/{self.current_repo}/contents/{dest_path}",
                    json=payload, timeout=20)
                self._parse_rl(r2)
                if r2.status_code in (200,201):
                    self.root.after(0, lambda: self._set_status(f"Uploaded {name}","ok"))
                    self.root.after(0, self._refresh_dir)
                else:
                    msg = r2.json().get("message","Upload failed")
                    self.root.after(0, lambda: self._set_status(msg,"err"))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(str(e),"err"))
            finally:
                self.root.after(0, self.progress_bar.stop)
                self.root.after(0, lambda: self._log(f"Upload: {name} → {dest_path}"))

        threading.Thread(target=_work, daemon=True).start()

    def _upload_folder(self):
        if not self._check_write(): return
        folder = filedialog.askdirectory(title="Choose Folder to Upload")
        if not folder: return
        dest = simpledialog.askstring("Upload Destination",
            "Destination path in repository (blank for root):", parent=self.root)
        if dest is None: return
        files = [(str(p), os.path.relpath(str(p), folder))
                 for p in Path(folder).rglob("*") if os.path.isfile(str(p))]
        if not files: return
        self._set_status(f"Uploading {len(files)} files…")
        self.progress_bar.start()
        branch = self.branch_var.get()
        total  = len(files)

        def _work():
            done, errs = 0, []
            for local_path, rel in files:
                repo_path = f"{dest}/{rel}".replace("\\","/").lstrip("/") if dest.strip() else rel.replace("\\","/")
                try:
                    with open(local_path,"rb") as fh:
                        content = base64.b64encode(fh.read()).decode()
                    r = rget(self.session,
                             f"{self.api_base}/repos/{self.username}/{self.current_repo}/contents/{repo_path}",
                             timeout=10)
                    sha = r.json().get("sha","") if r.status_code==200 else ""
                    payload: Dict[str,Any] = {
                        "message": f"Upload {rel} via GitView",
                        "content": content, "branch": branch,
                    }
                    if sha: payload["sha"] = sha
                    r2 = self.session.put(
                        f"{self.api_base}/repos/{self.username}/{self.current_repo}/contents/{repo_path}",
                        json=payload, timeout=20)
                    if r2.status_code in (200,201): done += 1
                    else: errs.append(rel)
                except Exception as e:
                    errs.append(f"{rel}: {e}")
                self.root.after(0, lambda d=done: self.progress_var.set(f"Uploaded {d}/{total}…"))
            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, lambda: self._set_status(f"Uploaded {done}/{total} files","ok"))
            self.root.after(0, lambda: self._log(f"Folder upload: {done}/{total}"))
            if errs:
                self.root.after(0, lambda: messagebox.showwarning("GitView",
                    f"Errors:\n" + "\n".join(errs[:10])))

        threading.Thread(target=_work, daemon=True).start()

    def _create_file(self):
        if not self._check_write(): return
        name = simpledialog.askstring("Create File","Filename:", parent=self.root)
        if not name: return
        content = simpledialog.askstring("File Content",
            "Initial content (leave blank for empty):", parent=self.root) or ""
        path   = f"{self.current_path}/{name}" if self.current_path else name
        branch = self.branch_var.get()
        self.progress_bar.start()

        def _work():
            try:
                r = self.session.put(
                    f"{self.api_base}/repos/{self.username}/{self.current_repo}/contents/{path}",
                    json={"message":f"Create {name} via GitView",
                          "content":base64.b64encode(content.encode()).decode(),
                          "branch":branch}, timeout=20)
                self._parse_rl(r)
                if r.status_code in (200,201):
                    self.root.after(0, lambda: self._set_status(f"Created {name}","ok"))
                    self.root.after(0, self._refresh_dir)
                else:
                    msg = r.json().get("message","Failed")
                    self.root.after(0, lambda: self._set_status(msg,"err"))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(str(e),"err"))
            finally:
                self.root.after(0, self.progress_bar.stop)

        threading.Thread(target=_work, daemon=True).start()

    def _create_folder(self):
        if not self._check_write(): return
        name = simpledialog.askstring("Create Folder","Folder name:", parent=self.root)
        if not name: return
        path   = f"{self.current_path}/{name}/.gitkeep" if self.current_path else f"{name}/.gitkeep"
        branch = self.branch_var.get()
        self.progress_bar.start()

        def _work():
            try:
                r = self.session.put(
                    f"{self.api_base}/repos/{self.username}/{self.current_repo}/contents/{path}",
                    json={"message":f"Create folder {name} via GitView",
                          "content":base64.b64encode(b"").decode(),
                          "branch":branch}, timeout=20)
                self._parse_rl(r)
                if r.status_code in (200,201):
                    self.root.after(0, lambda: self._set_status(f"Created folder {name}","ok"))
                    self.root.after(0, self._refresh_dir)
                else:
                    msg = r.json().get("message","Failed")
                    self.root.after(0, lambda: self._set_status(msg,"err"))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(str(e),"err"))
            finally:
                self.root.after(0, self.progress_bar.stop)

        threading.Thread(target=_work, daemon=True).start()

    def _rename_selected(self):
        sel = self.tree.selection()
        if not sel: return
        iid  = sel[0]
        vals = self.tree.item(iid,"values")
        name = self.tree.item(iid,"text").strip()
        if vals and vals[1]=="Folder":
            messagebox.showinfo("GitView","Folder renaming not supported via API."); return
        if not self._check_write(): return
        new_name = simpledialog.askstring("Rename File", f"New name for '{name}':", parent=self.root)
        if not new_name or new_name == name: return
        old_path = f"{self.current_path}/{name}" if self.current_path else name
        new_path = f"{self.current_path}/{new_name}" if self.current_path else new_name
        branch   = self.branch_var.get()
        self.progress_bar.start()

        def _work():
            try:
                r = rget(self.session,
                         f"{self.api_base}/repos/{self.username}/{self.current_repo}/contents/{old_path}",
                         params={"ref":branch} if branch else {}, timeout=15)
                self._parse_rl(r)
                if r.status_code != 200:
                    self.root.after(0, lambda: self._set_status("Could not get file for rename","err")); return
                data    = r.json()
                content = data.get("content","")
                sha     = data.get("sha","")
                r2 = self.session.put(
                    f"{self.api_base}/repos/{self.username}/{self.current_repo}/contents/{new_path}",
                    json={"message":f"Rename {name} → {new_name} via GitView",
                          "content":content,"branch":branch}, timeout=20)
                if r2.status_code in (200,201):
                    r3 = self.session.delete(
                        f"{self.api_base}/repos/{self.username}/{self.current_repo}/contents/{old_path}",
                        json={"message":f"Remove {name} after rename","sha":sha,"branch":branch}, timeout=15)
                    self.root.after(0, lambda: self._set_status(f"Renamed to {new_name}","ok"))
                    self.root.after(0, self._refresh_dir)
                else:
                    msg = r2.json().get("message","Rename failed")
                    self.root.after(0, lambda: self._set_status(msg,"err"))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(str(e),"err"))
            finally:
                self.root.after(0, self.progress_bar.stop)

        threading.Thread(target=_work, daemon=True).start()

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel: return
        if not self._check_write(): return
        items = []
        for iid in sel:
            vals = self.tree.item(iid,"values")
            name = self.tree.item(iid,"text").strip()
            if vals and vals[1]=="File":
                items.append(name)
        if not items: return
        if not messagebox.askyesno("Delete Files",
                                   f"Delete {len(items)} file(s)?\nThis cannot be undone."):
            return
        branch = self.branch_var.get()
        self.progress_bar.start()

        def _work():
            done = 0
            for name in items:
                try:
                    path = f"{self.current_path}/{name}" if self.current_path else name
                    r = rget(self.session,
                             f"{self.api_base}/repos/{self.username}/{self.current_repo}/contents/{path}",
                             params={"ref":branch} if branch else {}, timeout=10)
                    if r.status_code==200:
                        sha = r.json().get("sha","")
                        r2  = self.session.delete(
                            f"{self.api_base}/repos/{self.username}/{self.current_repo}/contents/{path}",
                            json={"message":f"Delete {name} via GitView","sha":sha,"branch":branch}, timeout=15)
                        if r2.status_code in (200,204): done += 1
                except Exception: pass
            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, lambda: self._set_status(f"Deleted {done}/{len(items)}","ok"))
            self.root.after(0, self._refresh_dir)
            self.root.after(0, lambda: self._log(f"Deleted {done}/{len(items)} files"))

        threading.Thread(target=_work, daemon=True).start()

    def _create_repo(self):
        if not self.token:
            messagebox.showwarning("GitView","Token required to create repositories."); return
        name = simpledialog.askstring("Create Repository","Repository name:", parent=self.root)
        if not name: return
        desc = simpledialog.askstring("Description","Repository description (optional):",
                                      parent=self.root) or ""
        self.progress_bar.start()

        def _work():
            try:
                r = self.session.post(f"{self.api_base}/user/repos",
                    json={"name":name,"description":desc,"auto_init":True}, timeout=20)
                self._parse_rl(r)
                if r.status_code == 201:
                    self.root.after(0, lambda: self._set_status(f"Created repo: {name}","ok"))
                    self.root.after(0, self._load_repos)
                else:
                    msg = r.json().get("message","Failed")
                    self.root.after(0, lambda: self._set_status(msg,"err"))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(str(e),"err"))
            finally:
                self.root.after(0, self.progress_bar.stop)

        threading.Thread(target=_work, daemon=True).start()

    def _open_browser(self):
        if not self.username or not self.current_repo: return
        webbrowser.open(f"https://github.com/{self.username}/{self.current_repo}")

    def _open_selected_browser(self):
        sel = self.tree.selection()
        if not sel: return
        name   = self.tree.item(sel[0],"text").strip()
        vals   = self.tree.item(sel[0],"values")
        path   = f"{self.current_path}/{name}" if self.current_path else name
        branch = self.branch_var.get()
        kind   = "tree" if vals and vals[1]=="Folder" else "blob"
        webbrowser.open(f"https://github.com/{self.username}/{self.current_repo}"
                        f"/{kind}/{branch}/{path}")

    # ── API Rate Limit ─────────────────────────────────────────────────────
    def _parse_rl(self, r: requests.Response):
        try:
            self.rate_remaining = int(r.headers.get("X-RateLimit-Remaining", self.rate_remaining))
            self.rate_limit     = int(r.headers.get("X-RateLimit-Limit",     self.rate_limit))
            self.rate_reset_ts  = float(r.headers.get("X-RateLimit-Reset",   self.rate_reset_ts))
            self.root.after(0, self._update_rl_display)
        except Exception: pass

    def _update_rl_display(self):
        try:
            rem  = self.rate_remaining
            lim  = self.rate_limit
            pct  = (rem/lim*100) if lim else 100
            col  = (self.C["rate_ok"]   if pct>40 else
                    self.C["rate_warn"] if pct>15 else
                    self.C["rate_low"])
            self.rate_lbl.config(text=f"API  ●  {rem:,}/{lim:,}", fg=col)
            if self.rate_reset_ts:
                reset = datetime.fromtimestamp(self.rate_reset_ts).strftime("%H:%M")
                self.api_reset_lbl.config(text=f"resets {reset}", fg=self.C["fg_subtle"])
        except Exception: pass

    # ── Theme ──────────────────────────────────────────────────────────────
    def _toggle_theme(self):
        self.current_theme = "light" if self.current_theme=="dark" else "dark"
        self.C = LIGHT if self.current_theme=="light" else DARK
        self.theme_btn.config(text="☀️  Light" if self.current_theme=="dark" else "🌙  Dark")
        self._apply_styles()
        self._save_cfg()
        self._set_status(f"Theme: {self.current_theme}","ok")

    # ── Status & Log ───────────────────────────────────────────────────────
    def _set_status(self, msg: str, level: str = "info"):
        colors = {"ok":self.C["success"],"err":self.C["danger"],
                  "warn":self.C["warning"],"info":self.C["fg_muted"]}
        try:
            self.status_lbl.config(text=f"  {msg}", fg=colors.get(level, self.C["fg_muted"]))
        except Exception: pass

    def _log(self, msg: str):
        ts    = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] {msg}"
        self.op_log.append(entry)
        try:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, entry+"\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        except Exception: pass

    def _clear_log(self):
        self.op_log.clear()
        try:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete("1.0", tk.END)
            self.log_text.config(state=tk.DISABLED)
        except Exception: pass

    # ── Config Persistence ─────────────────────────────────────────────────
    def _save_cfg(self):
        try:
            cfg = {
                "theme":         self.current_theme,
                "auth_mode":     self.auth_mode,
                "token":         self.tok_var.get() if self.auth_mode=="token" else "",
                "public_user":   self.pub_var.get() if self.auth_mode=="public" else "",
                "pinned_repos":  self.pinned_repos,
                "search_history":list(self.search_history),
                "saved_searches":self.saved_searches,
            }
            CFG.write_text(json.dumps(cfg, indent=2))
        except Exception: pass

    def _load_cfg(self):
        try:
            if not CFG.exists(): return
            cfg = json.loads(CFG.read_text())
            theme = cfg.get("theme","dark")
            if theme != self.current_theme:
                self.current_theme = theme
                self.C = LIGHT if theme=="light" else DARK
                self.theme_btn.config(text="☀️  Light" if theme=="dark" else "🌙  Dark")
                self._apply_styles()
            self.pinned_repos     = cfg.get("pinned_repos",[])
            self.search_history   = deque(cfg.get("search_history",[]), maxlen=30)
            self.saved_searches   = cfg.get("saved_searches",[])
            mode = cfg.get("auth_mode","token")
            if mode=="token":
                tok = cfg.get("token","")
                if tok:
                    self.tok_var.set(tok)
                    self._sw_token()
            else:
                user = cfg.get("public_user","")
                if user:
                    self.pub_var.set(user)
                    self._sw_public()
        except Exception: pass

    # ── Help ───────────────────────────────────────────────────────────────
    def _show_help(self):
        C = self.C
        win = tk.Toplevel(self.root)
        win.title("GitView v5 — Help")
        win.geometry("800x700")
        win.configure(bg=C["bg"])
        tk.Frame(win, bg=C["accent"], height=2).pack(fill=tk.X)
        hdr = tk.Frame(win, bg=C["surface"], height=46)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"❓  GitView v{VER} — Help & Quick Start",
                 bg=C["surface"], fg=C["fg"], font=(FTIT,12,"bold")).pack(side=tk.LEFT, padx=16, pady=12)
        txt = tk.Text(win, wrap=tk.WORD, bg=C["surface"], fg=C["fg"],
                      font=(FUI,10), relief=tk.FLAT, padx=22, pady=16,
                      selectbackground=C["tree_select"], highlightthickness=0)
        sb  = ttk.Scrollbar(win, command=txt.yview)
        txt.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        txt.pack(fill=tk.BOTH, expand=True)
        HELP = f"""
GitView v{VER} — Quick Start Guide
{'─'*66}

👋  GETTING STARTED
   ① 🔑  TOKEN MODE  (5000 req/hr — full access)
      github.com → Settings → Developer settings →
      Personal access tokens → Generate new token (Classic)
      Tick 'repo' scope → paste here → Connect

   ② 👤  BROWSE PUBLIC  (60 req/hr — no account needed)
      Enter any GitHub username → Browse

⌘  COMMAND PALETTE  (Ctrl+K)
   Instant access to all features without the mouse.
   Type to filter · Enter to run · Esc to close

📁  EXPLORER TAB
   • Pick repo and branch · Double-click folders to navigate
   • Ctrl+F = filter files · Space = quick preview
   • Right-click for context menu (download, rename, delete)
   • Backspace = go up · Home = root

🔍  SEARCH TAB  (Superior Hybrid Search Engine)
   Scopes: Repos · Content · Files · Commits · Topics
   Ranking uses: exact match · recency · activity · stars · fuzzy

   ★ NEW: Saved Searches — pin your frequent queries
   ★ NEW: Live search with 600ms debounce
   ★ NEW: Activity sort (stars + push recency)
   ★ NEW: Language / extension filters

🕐  COMMITS TAB
   • Load commit history with author/path/message filters
   • Click commit → metadata + full unified diff
   • Side-by-side diff mode available
   • File list navigation within each commit
   • Infinite scroll with Load More
   • Click SHA to view on GitHub

⌨️  KEYBOARD SHORTCUTS
   Ctrl+K   Command Palette    F5       Refresh repos
   Ctrl+F   File Filter        F2       Rename
   Ctrl+D   Download           Del      Delete
   Ctrl+U   Upload File        Space    Preview file
   Ctrl+N   New file           Backspace  Go up
   Escape   Cancel search      Home     Go to root

🎨  TIPS
   • 🌙/☀️  Theme toggle (persists across sessions)
   • API badge (top right) — green ≥40% · yellow 15–40% · red <15%
   • Config saved to ~/.gitview_config.json
   • Command palette supports fuzzy filtering

{'─'*66}
Author: Ali Essam  ·  Egypt 🇪🇬
LinkedIn: https://www.linkedin.com/in/dragonked2
GitHub:   https://github.com/dragonked2/gitview
"""
        txt.insert("1.0", HELP)
        txt.config(state=tk.DISABLED)
        bot = tk.Frame(win, bg=C["surface2"], height=44)
        bot.pack(fill=tk.X, side=tk.BOTTOM)
        bot.pack_propagate(False)
        btn(bot,"✕  Close", win.destroy, style="ghost", C=C).pack(side=tk.RIGHT, padx=12, pady=6)
        btn(bot,"🔗  LinkedIn", lambda: webbrowser.open("https://www.linkedin.com/in/dragonked2"),
            style="accent", C=C).pack(side=tk.LEFT, padx=12, pady=6)
        btn(bot,"⭐  Star on GitHub", lambda: webbrowser.open("https://github.com/dragonked2/gitview"),
            style="ghost", C=C).pack(side=tk.LEFT, padx=(0,8), pady=6)


# ── Entry Point ────────────────────────────────────────────────────────────
def main():
    root = tk.Tk()
    try: root.iconbitmap(default="gitview.ico")
    except Exception: pass
    app = GitView(root)
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth()  - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.mainloop()


if __name__ == "__main__":
    main()