#!/usr/bin/env python3
"""
GitView v9.0 — Enterprise GitHub Intelligence Platform
Author: Ali Essam · Egypt 🇪🇬 · github.com/dragonked2

CHANGES v9.0 (10x improvement release):
  - FIXED (CRITICAL): _tkinter.TclError crash — pady=(0,4) tuple in tk.Label
    is invalid in Python 3.14. Simplified to pady=4.
  - FIXED (CRITICAL): OSError on Windows — %-d strftime directive is Linux-only.
    Replaced with cross-platform str(dt.day).
  - FIXED: r.json() called twice in _load_single_repo — second call checked
    the already-filtered batch size, causing premature loop exit on filtered loads.
    Now tracks raw batch length before filtering.
  - NEW: Rate limit tracker — GitHub API X-RateLimit headers captured on every
    request; status bar shows remaining/limit with green/amber/red color coding.
  - NEW: Clickable breadcrumb path segments — click any segment to navigate there
    directly without going up one step at a time.
  - NEW: Command palette v2 — grouped sections with separator labels, arrow-key
    navigation skips separator rows, footer shows keyboard hints.
  - NEW: Toast close button — × label on every notification for early dismiss.
  - NEW: Status bar color coding — ok=green, warn=amber, err=red.
  - IMPROVED: About page — scrollable hero section, feature grid, color-coded
    changelog with FIXED/NEW/IMPROVED badges.
  - IMPROVED: Help window — added rate limit docs, v9.0 bug fixes listed.
  - IMPROVED: Empty state — accent bar, better subtitle, Ctrl+K hint.
  - IMPROVED: Session rate attributes initialized at startup (no AttributeError).
"""
import warnings, os, re, json, base64, threading, time, webbrowser, queue, csv, io
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import deque, defaultdict
from typing import Dict, List, Any, Optional, Tuple, Set
warnings.filterwarnings("ignore")

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import requests
try:
    import urllib3; urllib3.disable_warnings()
except Exception:
    pass

VER = "9.0.0"
CFG = Path.home() / ".gitview8_config.json"
RPP = 25  # results per page

_NT = os.name == "nt"
FUI   = "Segoe UI"       if _NT else "SF Pro Display"
FMONO = "Cascadia Code"  if _NT else "SF Mono"
FBOLD = "Segoe UI Bold"  if _NT else "SF Pro Display"

# ── Design Tokens ──────────────────────────────────────────────────────────
DARK = {
    "bg": "#030609", "surface": "#080F1C", "surface2": "#0D1628",
    "surface3": "#131E36", "card": "#0A1220", "card2": "#0E1830",
    "border": "#192840", "border_hi": "#243D60",
    "fg": "#E4EAF8", "fg_muted": "#6E82A0", "fg_dim": "#364A66",
    "fg_bright": "#F0F6FF",
    "accent": "#4F8EF7", "accent2": "#60A5FA", "accent_bg": "#152248",
    "accent_dim": "#0E1A38",
    "green": "#23D18B", "green_bg": "#052218",
    "teal": "#2DD4BF",  "teal_bg": "#041F1C",
    "amber": "#F0A429", "amber_bg": "#221505",
    "red": "#F06060",   "red_bg": "#200A0A",
    "purple": "#B197FC","purple_bg": "#1A1040",
    "cyan": "#38BDF8",  "cyan_bg": "#041C2C",
    "pink": "#F471B5",  "orange": "#FB923C",
    "sidebar": "#040A14", "sidebar_hl": "#111E38", "sidebar_active": "#162240",
    "topbar": "#030609", "statusbar": "#030609",
    "entry": "#050C1A", "entry_border": "#192840", "entry_focus": "#4F8EF7",
    "sel": "#1B3060", "scrollbar": "#162030", "scrollbar_hi": "#253550",
    "diff_add": "#071F0F", "diff_add_fg": "#23D18B",
    "diff_del": "#200808", "diff_del_fg": "#F06060",
    "diff_hunk": "#0F1E40", "diff_hunk_fg": "#60A5FA",
    "diff_ctx": "#080F1C", "diff_ctx_fg": "#6E82A0",
    "tag_dir": "#60A5FA", "tag_file": "#E4EAF8", "sep": "#111D30",
    "syn_kw": "#F06060", "syn_str": "#86EFAC", "syn_cmt": "#364A66",
    "syn_num": "#67E8F9", "syn_fn": "#B197FC", "syn_deco": "#FB923C",
    "syn_bi": "#38BDF8", "syn_op": "#F471B5",
}
LIGHT = {
    "bg": "#F2F5FB", "surface": "#FFFFFF", "surface2": "#F6F8FD",
    "surface3": "#EBF0FA", "card": "#FFFFFF", "card2": "#F8FAFF",
    "border": "#D4DCF0", "border_hi": "#B0BFDC",
    "fg": "#141E33", "fg_muted": "#4A6080", "fg_dim": "#8898B8",
    "fg_bright": "#0A1020",
    "accent": "#2563EB", "accent2": "#1D4ED8", "accent_bg": "#DBEAFE",
    "accent_dim": "#EFF6FF",
    "green": "#059669", "green_bg": "#D1FAE5",
    "teal": "#0D9488",  "teal_bg": "#CCFBF1",
    "amber": "#D97706", "amber_bg": "#FEF3C7",
    "red": "#DC2626",   "red_bg": "#FEE2E2",
    "purple": "#7C3AED","purple_bg": "#EDE9FE",
    "cyan": "#0891B2",  "cyan_bg": "#CFFAFE",
    "pink": "#DB2777",  "orange": "#EA580C",
    "sidebar": "#FFFFFF", "sidebar_hl": "#EEF3FC", "sidebar_active": "#DBEAFE",
    "topbar": "#FFFFFF", "statusbar": "#F6F8FD",
    "entry": "#FFFFFF", "entry_border": "#D4DCF0", "entry_focus": "#2563EB",
    "sel": "#DBEAFE", "scrollbar": "#D4DCF0", "scrollbar_hi": "#B0BFDC",
    "diff_add": "#D1FAE5", "diff_add_fg": "#059669",
    "diff_del": "#FEE2E2", "diff_del_fg": "#DC2626",
    "diff_hunk": "#DBEAFE", "diff_hunk_fg": "#1D4ED8",
    "diff_ctx": "#F6F8FD", "diff_ctx_fg": "#4A6080",
    "tag_dir": "#2563EB", "tag_file": "#141E33", "sep": "#D4DCF0",
    "syn_kw": "#DC2626", "syn_str": "#059669", "syn_cmt": "#8898B8",
    "syn_num": "#0891B2", "syn_fn": "#7C3AED", "syn_deco": "#EA580C",
    "syn_bi": "#0891B2", "syn_op": "#DB2777",
}

# ── File Icons & Language Map ──────────────────────────────────────────────
_FICONS = {
    "py": "🐍", "js": "⚡", "ts": "🔷", "jsx": "⚛", "tsx": "⚛",
    "html": "🌐", "css": "🎨", "scss": "🎨", "sass": "🎨",
    "json": "📋", "yaml": "⚙", "yml": "⚙", "toml": "⚙", "ini": "⚙",
    "md": "📝", "txt": "📄", "rst": "📝", "log": "📄",
    "sh": "💻", "bash": "💻", "zsh": "💻", "bat": "💻", "ps1": "💻",
    "c": "🔵", "cpp": "🔵", "h": "🔵", "hpp": "🔵",
    "go": "🐹", "rs": "🦀", "rb": "💎", "php": "🐘",
    "java": "☕", "kt": "🎯", "swift": "🍎", "cs": "🔷",
    "sql": "🗄", "db": "🗄",
    "png": "🖼", "jpg": "🖼", "jpeg": "🖼", "gif": "🖼",
    "svg": "🖼", "ico": "🖼", "webp": "🖼",
    "pdf": "📕", "zip": "📦", "tar": "📦", "gz": "📦", "rar": "📦",
    "mp4": "🎬", "mp3": "🎵",
    "lock": "🔒", "env": "🔑", "pem": "🔑", "key": "🔑",
    "dockerfile": "🐳", "gitignore": "🚫", "makefile": "🔨",
    "vue": "💚", "svelte": "🔥",
}
_LMAP = {
    "py": "python", "pyw": "python",
    "js": "javascript", "jsx": "javascript", "mjs": "javascript",
    "ts": "javascript", "tsx": "javascript",
    "json": "json", "html": "html", "htm": "html",
    "css": "css", "scss": "css",
    "sh": "bash", "bash": "bash", "zsh": "bash",
    "rb": "ruby", "go": "go", "rs": "rust",
    "java": "java", "c": "c", "h": "c", "cpp": "c", "hpp": "c",
    "cs": "csharp", "php": "php", "swift": "swift", "kt": "kotlin",
    "sql": "sql", "md": "markdown",
    "yaml": "yaml", "yml": "yaml", "toml": "toml",
    "vue": "javascript", "svelte": "javascript",
}
_BINARY_EXT = {
    "png", "jpg", "jpeg", "gif", "svg", "ico", "webp", "bmp",
    "pdf", "zip", "tar", "gz", "rar", "mp4", "mp3", "wav",
    "woff", "woff2", "ttf", "eot", "otf", "exe", "dll", "so",
}

def _fi(name: str) -> str:
    n = name.lower()
    for s in ("dockerfile", ".gitignore", ".env", "makefile", "readme", "license", "changelog"):
        if s in n:
            return _FICONS.get(s.lstrip("."), "📄")
    ext = n.rsplit(".", 1)[-1] if "." in n else ""
    return _FICONS.get(ext, "📄")

def _lang(name: str) -> str:
    ext = name.lower().rsplit(".", 1)[-1] if "." in name else ""
    return _LMAP.get(ext, "text")

def _is_binary(name: str) -> bool:
    ext = name.lower().rsplit(".", 1)[-1] if "." in name else ""
    return ext in _BINARY_EXT

def fmt_sz(b: int) -> str:
    if b < 1024:    return f"{b} B"
    if b < 1048576: return f"{b/1024:.1f} KB"
    if b < 1073741824: return f"{b/1048576:.1f} MB"
    return f"{b/1073741824:.1f} GB"

def rel_t(iso: str) -> str:
    if not iso: return ""
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        s = int((datetime.now(timezone.utc) - dt).total_seconds())
        if s < 60:      return "just now"
        if s < 3600:    return f"{s//60}m ago"
        if s < 86400:   return f"{s//3600}h ago"
        if s < 604800:  return f"{s//86400}d ago"
        if s < 2592000: return f"{s//604800}w ago"
        if s < 31536000:return f"{s//2592000}mo ago"
        return f"{s//31536000}y ago"
    except:
        return iso[:10] if len(iso) >= 10 else iso

def fmt_dt(iso: str) -> str:
    if not iso: return ""
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%Y-%m-%d  %H:%M")
    except:
        return iso[:10]

def date_group(iso: str) -> str:
    if not iso: return "Unknown Date"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = (now - dt).days
        if diff == 0:  return "Today"
        if diff == 1:  return "Yesterday"
        if diff < 7:   return dt.strftime("This Week — %A")
        if diff < 30:  return dt.strftime("Week of %b ") + str(dt.day)
        if diff < 365: return dt.strftime("%B %Y")
        return dt.strftime("%Y")
    except:
        return "Unknown Date"

def recency(iso: str) -> float:
    if not iso: return 0.0
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return max(0.0, 1.0 - ((datetime.now(timezone.utc) - dt).days / 730.0))
    except:
        return 0.0

def parse_gh_user(text: str) -> Optional[str]:
    text = re.sub(r"^https?://", "", text.strip().rstrip("/"))
    text = re.sub(r"^(www\.)?github\.com/?", "", text)
    parts = [p for p in text.split("/") if p]
    if not parts: return None
    u = parts[0]
    return u if re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,37}[a-zA-Z0-9])?$", u) else None


# ── Network Layer ──────────────────────────────────────────────────────────
def rget(sess: requests.Session, url: str, params=None, hdrs=None,
         timeout=18, tries=3) -> requests.Response:
    kw: Dict[str, Any] = {"params": params, "timeout": timeout}
    if hdrs:
        kw["headers"] = hdrs
    exc = None
    for i in range(tries):
        try:
            r = sess.get(url, **kw)
            # Surface rate-limit info on the session for UI display
            remaining = r.headers.get("X-RateLimit-Remaining")
            limit      = r.headers.get("X-RateLimit-Limit")
            if remaining is not None:
                sess._rate_remaining = int(remaining)
                sess._rate_limit     = int(limit or 0)
            if r.status_code in (500, 502, 503, 504) and i < tries - 1:
                time.sleep(2 ** i)
                continue
            if r.status_code == 429:
                wait = int(r.headers.get("Retry-After", 10))
                time.sleep(min(wait, 30))
                continue
            return r
        except (requests.ConnectionError, requests.Timeout) as e:
            exc = e
            if i < tries - 1:
                time.sleep(2 ** i)
    raise exc or RuntimeError(f"Failed: {url}")


# ── Search Engine ──────────────────────────────────────────────────────────
class SE:
    @staticmethod
    def score(q: str, t: str) -> int:
        if not q or not t: return 0
        ql, tl = q.lower(), t.lower()
        if tl == ql:            return 100
        if tl.startswith(ql):  return 90
        if ql in tl.split():   return 80
        if tl.endswith(ql):    return 70
        if ql in tl:           return 60
        ps = ql.split()
        if len(ps) > 1 and all(p in tl for p in ps): return 50
        hits = sum(1 for c in ql if c in tl)
        return int(hits / max(len(ql), 1) * 28)

    @classmethod
    def repo_score(cls, q: str, rd: Dict) -> int:
        ql = q.lower()
        sc  = cls.score(ql, rd.get("name", "")) * 4
        sc += cls.score(ql, rd.get("description") or "") * 1
        sc += sum(80 if ql == t.lower() else 40 if ql in t.lower() else 0
                  for t in rd.get("topics", []))
        lang = (rd.get("language") or "").lower()
        if ql == lang: sc += 35
        elif ql in lang: sc += 18
        sc += int(recency(rd.get("updated_at", "")) * 45)
        sc += int(recency(rd.get("pushed_at", "")) * 22)
        sc += min(35, int((rd.get("stargazers_count", 0) ** 0.4)))
        return sc

    @classmethod
    def commit_score(cls, q: str, c: Dict) -> int:
        ql   = q.lower()
        msg  = (c.get("commit", {}).get("message", "") or "").lower()
        auth = ((c.get("commit", {}).get("author") or {}).get("name", "") or "").lower()
        repo = (c.get("_repo", "") or "").lower()
        sc   = cls.score(ql, msg) * 3 + cls.score(ql, auth) + cls.score(ql, repo)
        sc  += int(recency((c.get("commit", {}).get("author") or {}).get("date", "")) * 40)
        if c.get("_diff") and ql in c["_diff"].lower(): sc += 50
        return sc


# ── Diff Parser ────────────────────────────────────────────────────────────
class DP:
    @staticmethod
    def parse(raw: str) -> List[Dict]:
        files: List[Dict] = []
        cur: Optional[Dict] = None
        hunk: Optional[Dict] = None
        for line in raw.splitlines():
            if line.startswith("diff --git"):
                if cur: files.append(cur)
                cur = {"path": "", "hunks": [], "additions": 0, "deletions": 0}
            elif line.startswith("+++ ") and cur is not None:
                p = line[4:]
                cur["path"] = p[2:] if p.startswith("b/") else p
            elif line.startswith("@@") and cur is not None:
                hunk = {"header": line, "lines": []}
                cur["hunks"].append(hunk)
            elif hunk is not None and cur is not None:
                if line.startswith("+"):
                    hunk["lines"].append(("add", line[1:]))
                    cur["additions"] += 1
                elif line.startswith("-"):
                    hunk["lines"].append(("del", line[1:]))
                    cur["deletions"] += 1
                else:
                    hunk["lines"].append(("ctx", line[1:] if line.startswith(" ") else line))
        if cur: files.append(cur)
        return files

    @staticmethod
    def stats(files: List[Dict]) -> Tuple[int, int]:
        a = sum(f.get("additions", 0) for f in files)
        d = sum(f.get("deletions", 0) for f in files)
        return a, d


# ── Syntax Highlighter ─────────────────────────────────────────────────────
class SH:
    _PY_KW  = r'\b(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b'
    _PY_BI  = r'\b(abs|all|any|bin|bool|bytes|callable|chr|dict|dir|enumerate|eval|filter|float|format|frozenset|getattr|globals|hasattr|hash|hex|id|input|int|isinstance|issubclass|iter|len|list|locals|map|max|min|next|object|open|ord|pow|print|property|range|repr|reversed|round|set|setattr|sorted|staticmethod|str|sum|super|tuple|type|vars|zip)\b'
    _JS_KW  = r'\b(async|await|break|case|catch|class|const|continue|debugger|default|delete|do|else|export|extends|finally|for|from|function|if|import|in|instanceof|let|new|null|of|return|static|super|switch|this|throw|try|typeof|undefined|var|void|while|with|yield|true|false)\b'
    _SQL_KW = r'\b(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|OUTER|ON|AS|AND|OR|NOT|IN|EXISTS|LIKE|BETWEEN|ORDER|BY|GROUP|HAVING|LIMIT|OFFSET|UNION|ALL|DISTINCT|CREATE|TABLE|DROP|ALTER|INDEX|VIEW|PRIMARY|KEY|FOREIGN|REFERENCES|UNIQUE|NULL|DEFAULT|BEGIN|COMMIT|ROLLBACK)\b'

    PAT: Dict[str, List] = {}
    PAT["python"] = [
        ("syn_cmt", r'#[^\n]*'),
        ("syn_str", r'("""[\s\S]*?"""|\'\'\' [\s\S]*?\'\'\'|"[^"\n]*"|\'[^\'\n]*\')'),
        ("syn_deco", r'@\w+'),
        ("syn_kw",  _PY_KW),
        ("syn_bi",  _PY_BI),
        ("syn_num", r'\b\d+(\.\d+)?\b'),
        ("syn_fn",  r'\bdef\s+(\w+)'),
    ]
    PAT["javascript"] = [
        ("syn_cmt", r'//[^\n]*|/\*[\s\S]*?\*/'),
        ("syn_str", r'(`[^`]*`|"[^"\n]*"|\'[^\'\n]*\')'),
        ("syn_kw",  _JS_KW),
        ("syn_num", r'\b\d+(\.\d+)?\b'),
        ("syn_fn",  r'\bfunction\s+(\w+)|\b(\w+)\s*=\s*(async\s*)?\('),
    ]
    PAT["json"] = [
        ("syn_str", r'"[^"\\]*(\\.[^"\\]*)*"'),
        ("syn_kw",  r'\b(true|false|null)\b'),
        ("syn_num", r'-?\b\d+(\.\d+)?([eE][+-]?\d+)?\b'),
    ]
    PAT["html"] = [
        ("syn_cmt", r'<!--[\s\S]*?-->'),
        ("syn_str", r'"[^"]*"|\'[^\']*\''),
        ("syn_kw",  r'</?[\w.-]+|>|/>'),
        ("syn_fn",  r'\s[\w-]+='),
    ]
    PAT["css"] = [
        ("syn_cmt", r'/\*[\s\S]*?\*/'),
        ("syn_str", r'"[^"]*"|\'[^\']*\''),
        ("syn_kw",  r'[\w-]+\s*(?=:)'),
        ("syn_fn",  r'#[\w-]+|\.[\w-]+'),
        ("syn_num", r'\b\d+(\.\d+)?(px|em|rem|%|vh|vw|pt|s|ms)?\b'),
    ]
    PAT["bash"] = [
        ("syn_cmt", r'#[^\n]*'),
        ("syn_str", r'"[^"]*"|\'[^\']*\''),
        ("syn_kw",  r'\b(if|then|else|elif|fi|for|while|do|done|case|esac|function|return|echo|exit|export|source|local|cd|ls|grep|awk|sed|find|chmod|chown)\b'),
        ("syn_num", r'\$[\w@#?$!*-]|\$\{[\w@#?$!*-]+\}'),
    ]
    PAT["sql"] = [
        ("syn_cmt", r'--[^\n]*|/\*[\s\S]*?\*/'),
        ("syn_str", r"'[^']*'"),
        ("syn_kw",  _SQL_KW),
        ("syn_num", r'\b\d+(\.\d+)?\b'),
    ]
    PAT["markdown"] = [
        ("syn_fn",  r'^#{1,6}\s.*$'),
        ("syn_str", r'`[^`]+`'),
        ("syn_kw",  r'\*\*[^*]+\*\*|__[^_]+__'),
        ("syn_cmt", r'\[[^\]]*\]\([^)]*\)'),
    ]
    PAT["yaml"] = [
        ("syn_cmt", r'#[^\n]*'),
        ("syn_str", r'"[^"]*"|\'[^\']*\''),
        ("syn_kw",  r'^[\w-]+(?=\s*:)'),
        ("syn_num", r'\b\d+(\.\d+)?\b'),
    ]
    PAT["toml"] = [
        ("syn_cmt", r'#[^\n]*'),
        ("syn_str", r'"[^"]*"|\'[^\']*\''),
        ("syn_kw",  r'^\[[\w.]+\]'),
        ("syn_num", r'\b\d+(\.\d+)?\b'),
    ]
    for _l in ("c", "csharp", "java", "go", "rust", "ruby", "swift", "kotlin", "php"):
        PAT[_l] = PAT["javascript"]

    @classmethod
    def apply(cls, w: tk.Text, lang: str, C: Dict) -> None:
        pats = cls.PAT.get(lang, [])
        if not pats: return
        tag_colors = {
            "syn_kw": C.get("syn_kw", "#f06060"),
            "syn_str": C.get("syn_str", "#86efac"),
            "syn_cmt": C.get("syn_cmt", "#364a66"),
            "syn_num": C.get("syn_num", "#67e8f9"),
            "syn_fn":  C.get("syn_fn",  "#b197fc"),
            "syn_deco":C.get("syn_deco","#fb923c"),
            "syn_bi":  C.get("syn_bi",  "#38bdf8"),
        }
        for tag, fg in tag_colors.items():
            w.tag_configure(tag, foreground=fg)
        content = w.get("1.0", tk.END)
        for tag, pat in pats:
            try:
                for m in re.finditer(pat, content, re.MULTILINE):
                    w.tag_add(tag, f"1.0+{m.start()}c", f"1.0+{m.end()}c")
            except (re.error, tk.TclError):
                pass


# ── Commit Index ───────────────────────────────────────────────────────────
class CommitIndex:
    def __init__(self):
        self._lock = threading.Lock()
        self._commits: List[Dict] = []
        self._shas: Set[str] = set()
        self.by_repo: Dict[str, int] = defaultdict(int)
        self.indexing = False
        self.indexed_repos: Set[str] = set()

    def clear(self):
        with self._lock:
            self._commits.clear()
            self._shas.clear()
            self.by_repo.clear()
            self.indexed_repos.clear()

    def add(self, repo: str, branch: str, commits: List[Dict]) -> int:
        added = 0
        with self._lock:
            for c in commits:
                sha = c.get("sha", "")
                if sha and sha in self._shas:
                    continue
                c = dict(c)
                c["_repo"] = repo
                c["_branch"] = branch
                self._commits.append(c)
                if sha:
                    self._shas.add(sha)
                self.by_repo[repo] += 1
                added += 1
            self.indexed_repos.add(repo)
        return added

    def total(self) -> int:
        with self._lock:
            return len(self._commits)

    def get_all(self, repo: Optional[str] = None, author_f: str = "",
                branch_f: str = "", msg_f: str = "") -> List[Dict]:
        with self._lock:
            pool = self._commits[:]
        if repo and repo != "(All Repos)":
            pool = [c for c in pool if c.get("_repo", "") == repo]
        if author_f:
            al = author_f.lower()
            pool = [c for c in pool if al in
                    ((c.get("commit", {}).get("author") or {}).get("name", "") or "").lower()]
        if branch_f:
            pool = [c for c in pool if c.get("_branch", "") == branch_f]
        if msg_f:
            ml = msg_f.lower()
            pool = [c for c in pool if ml in
                    (c.get("commit", {}).get("message", "") or "").lower()]
        pool.sort(key=lambda c: self._dk(c), reverse=True)
        return pool

    def search(self, q: str, repo: Optional[str] = None) -> List[Dict]:
        with self._lock:
            pool = self._commits[:]
        if repo and repo != "(All Repos)":
            pool = [c for c in pool if c.get("_repo", "") == repo]
        scored = [(SE.commit_score(q, c), c) for c in pool]
        scored = [x for x in scored if x[0] > 0]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:1000]]

    @staticmethod
    def _dk(c: Dict) -> datetime:
        d = (c.get("commit", {}).get("author") or {}).get("date", "")
        try:
            return datetime.fromisoformat(d.replace("Z", "+00:00"))
        except:
            return datetime.min.replace(tzinfo=timezone.utc)

    def export_csv(self) -> str:
        """Export all indexed commits to CSV string"""
        with self._lock:
            commits = self._commits[:]
        out = io.StringIO()
        w = csv.writer(out)
        w.writerow(["SHA", "Repo", "Branch", "Message", "Author", "Email", "Date"])
        for c in commits:
            commit = c.get("commit", {})
            auth   = commit.get("author") or {}
            w.writerow([
                c.get("sha", "")[:12],
                c.get("_repo", ""),
                c.get("_branch", ""),
                (commit.get("message", "") or "").split("\n")[0][:120],
                auth.get("name", ""),
                auth.get("email", ""),
                auth.get("date", ""),
            ])
        return out.getvalue()


# ── Widget Helpers ─────────────────────────────────────────────────────────
def _btn(parent, text, cmd, style="default", C=None, font=None,
         px=12, py=5, **kw) -> tk.Button:
    C = C or DARK
    font = font or (FUI, 9)
    STYLES = {
        "default": (C["surface3"],   C["fg"],        C["border_hi"],  C["fg_bright"]),
        "accent":  (C["accent"],     C["fg_bright"], C["accent2"],    C["fg_bright"]),
        "green":   (C["green"],      C["fg_bright"], "#34d399",       C["fg_bright"]),
        "red":     (C["red"],        C["fg_bright"], "#ff7070",       C["fg_bright"]),
        "ghost":   (C["surface"],    C["fg_muted"],  C["surface2"],   C["fg"]),
        "ghost2":  (C["surface2"],   C["fg_muted"],  C["surface3"],   C["fg"]),
        "active":  (C["accent_bg"],  C["accent2"],   C["accent_dim"], C["accent2"]),
        "purple":  (C["purple_bg"],  C["purple"],    C["purple"],     C["fg_bright"]),
        "amber":   (C["amber_bg"],   C["amber"],     C["amber"],      C["fg_bright"]),
    }
    bg, fg, abg, afg = STYLES.get(style, STYLES["default"])
    b = tk.Button(parent, text=text, command=cmd, font=font,
                  relief=tk.FLAT, cursor="hand2", padx=px, pady=py,
                  bd=0, highlightthickness=0, bg=bg, fg=fg,
                  activebackground=abg, activeforeground=afg, **kw)
    b.bind("<Enter>", lambda _: b.config(bg=abg, fg=afg))
    b.bind("<Leave>", lambda _: b.config(bg=bg, fg=fg))
    return b

def _entry(parent, var, C, width=22, mono=False, show=None) -> tk.Entry:
    font = (FMONO, 10) if mono else (FUI, 10)
    e = tk.Entry(parent, textvariable=var, font=font, relief=tk.FLAT,
                 bg=C["entry"], fg=C["fg"], insertbackground=C["fg"],
                 width=width, highlightthickness=1,
                 highlightbackground=C["entry_border"],
                 highlightcolor=C["entry_focus"], bd=0)
    if show:
        e.config(show=show)
    e.bind("<FocusIn>",  lambda _: e.config(highlightbackground=C["entry_focus"]))
    e.bind("<FocusOut>", lambda _: e.config(highlightbackground=C["entry_border"]))
    return e

def _sep(parent, C, h: int = 1, pad: int = 0):
    """Separator widget. Use 'pad' for padding (not 'pady')."""
    tk.Frame(parent, bg=C["sep"], height=h).pack(fill=tk.X, pady=pad)

def _lbl(parent, text, C, size=8, bold=False, color_key="fg_dim", **kw) -> tk.Label:
    font = (FUI, size, "bold") if bold else (FUI, size)
    return tk.Label(parent, text=text, bg=kw.pop("bg", C["surface"]),
                    fg=C[color_key], font=font, **kw)

def _txt(parent, C, mono=False, h=None, **kw) -> tk.Text:
    font = (FMONO, 9) if mono else (FUI, 9)
    defaults = dict(wrap=tk.WORD, bg=C["surface"], fg=C["fg"], font=font,
                    relief=tk.FLAT, highlightthickness=0, state=tk.DISABLED,
                    padx=12, pady=8, selectbackground=C["sel"],
                    insertbackground=C["fg"])
    defaults.update(kw)
    if h: defaults["height"] = h
    return tk.Text(parent, **defaults)

def _vsb(parent, cmd) -> ttk.Scrollbar:
    return ttk.Scrollbar(parent, orient=tk.VERTICAL, command=cmd)

def _hsb(parent, cmd) -> ttk.Scrollbar:
    return ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=cmd)


# ── Tooltip ────────────────────────────────────────────────────────────────
class Tip:
    def __init__(self, w: tk.Widget, text: str, C: Dict):
        self.w, self.text, self.C = w, text, C
        self._tip = self._id = None
        w.bind("<Enter>",   lambda _: self._sched(), add="+")
        w.bind("<Leave>",   self._cancel, add="+")
        w.bind("<Destroy>", self._cancel, add="+")

    def _sched(self):
        self._cancel()
        self._id = self.w.after(500, self._show)

    def _show(self):
        if not self.w.winfo_exists(): return
        x = self.w.winfo_rootx() + 10
        y = self.w.winfo_rooty() + self.w.winfo_height() + 4
        C = self.C
        self._tip = t = tk.Toplevel(self.w)
        t.wm_overrideredirect(True)
        t.wm_geometry(f"+{x}+{y}")
        t.wm_attributes("-topmost", True)
        f = tk.Frame(t, bg=C["border_hi"], padx=1, pady=1)
        f.pack()
        tk.Label(f, text=self.text, bg=C["surface3"], fg=C["fg"],
                 font=(FUI, 8), padx=10, pady=4).pack()

    def _cancel(self, _=None):
        if self._id:
            try: self.w.after_cancel(self._id)
            except: pass
            self._id = None
        if self._tip:
            try: self._tip.destroy()
            except: pass
            self._tip = None


# ══════════════════════════════════════════════════════════════════════════
class GitView:
# ══════════════════════════════════════════════════════════════════════════

    def __init__(self, root: tk.Tk):
        self.root = root
        root.title(f"GitView  {VER}")
        root.geometry("1760x980")
        root.minsize(1200, 700)

        # Session
        self.sess = requests.Session()
        self.sess.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": f"GitView/{VER}",
        })
        self.sess._rate_remaining = -1
        self.sess._rate_limit     = -1
        self.API = "https://api.github.com"

        # State
        self.token:              Optional[str] = None
        self.username:           Optional[str] = None
        self.auth_mode:          str           = "token"
        self.current_repo:       Optional[str] = None
        self.current_repo_full:  Optional[str] = None
        self.current_path:       str           = ""
        self.repo_data:          Dict[str, Any]= {}
        self.all_items:          Dict[str, List]= {"dirs": [], "files": []}
        self.sort_col:           str           = "name"
        self.sort_rev:           bool          = False
        self.pinned:             List[str]     = []
        self.recent_repos:       deque         = deque(maxlen=10)
        self.current_theme:      str           = "dark"
        self.C:                  Dict          = DARK
        self.search_history:     deque         = deque(maxlen=50)
        self.saved_searches:     List[str]     = []
        self._results:           List[Dict]    = []
        self._result_page:       int           = 1
        self.search_cancel:      threading.Event = threading.Event()
        self._index:             CommitIndex   = CommitIndex()
        self._index_cancel:      threading.Event = threading.Event()
        self._diff_cache:        Dict[str, str]= {}
        self._diff_files:        List[Dict]    = []
        self._commits_cache:     Dict[str, Dict]= {}
        self._commit_display:    List[Dict]    = []
        self._commit_page:       int           = 1
        self._debounce_id:       Optional[str] = None
        self._preview_wins:      List[tk.Toplevel] = []
        self._show_tok:          bool          = False
        self._cp_win:            Optional[tk.Toplevel] = None
        self._toast_queue:       queue.Queue   = queue.Queue()
        self._prog_running:      bool          = False
        self._current_nav:       str           = "explorer"
        self._loading_all:       bool          = False
        self._all_widgets:       List[tk.Widget] = []   # for theme re-application

        self._apply_styles()
        self._build_ui()
        self._shortcuts()
        self._load_cfg()
        self._poll_toasts()

    # ── Styles ──────────────────────────────────────────────────────────
    def _apply_styles(self):
        C = self.C
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Treeview",
                     background=C["surface"], foreground=C["fg"],
                     fieldbackground=C["surface"], rowheight=34,
                     font=(FUI, 10), borderwidth=0, relief="flat",
                     highlightthickness=0)
        s.configure("Treeview.Heading",
                     background=C["surface2"], foreground=C["fg_muted"],
                     font=(FUI, 8, "bold"), relief="flat",
                     padding=(8, 7), borderwidth=0)
        s.map("Treeview",
              background=[("selected", C["sel"])],
              foreground=[("selected", C["accent2"])])
        s.map("Treeview.Heading",
              background=[("active", C["surface3"])])
        s.configure("TNotebook",
                     background=C["bg"], borderwidth=0,
                     tabmargins=[0, 0, 0, 0])
        s.configure("TNotebook.Tab",
                     background=C["surface2"], foreground=C["fg_muted"],
                     padding=[16, 7], font=(FUI, 9, "bold"), borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", C["surface"])],
              foreground=[("selected", C["fg"])])
        s.configure("TCombobox",
                     fieldbackground=C["surface2"], background=C["surface2"],
                     foreground=C["fg"], arrowcolor=C["fg_muted"],
                     selectbackground=C["sel"], selectforeground=C["fg"],
                     relief="flat", padding=(8, 5))
        s.map("TCombobox",
              fieldbackground=[("readonly", C["surface2"])],
              foreground=[("readonly", C["fg"])])
        s.configure("TScrollbar",
                     background=C["scrollbar"], troughcolor=C["surface"],
                     arrowcolor=C["fg_dim"], relief="flat",
                     borderwidth=0, width=6)
        s.map("TScrollbar",
              background=[("active", C["scrollbar_hi"]),
                           ("pressed", C["accent"])])
        s.configure("TProgressbar",
                     troughcolor=C["surface2"], background=C["accent"],
                     borderwidth=0, thickness=3)
        self.root.configure(bg=C["bg"])
        self.root.option_add("*TCombobox*Listbox.background",       C["surface2"])
        self.root.option_add("*TCombobox*Listbox.foreground",       C["fg"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", C["sel"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", C["accent2"])
        self.root.option_add("*TCombobox*Listbox.font",             (FUI, 10))

    # ── Master Layout ────────────────────────────────────────────────────
    def _build_ui(self):
        C = self.C
        root_f = tk.Frame(self.root, bg=C["bg"])
        root_f.pack(fill=tk.BOTH, expand=True)
        self._root_f = root_f

        self._build_topbar(root_f)

        body = tk.Frame(root_f, bg=C["bg"])
        body.pack(fill=tk.BOTH, expand=True)
        self._body = body

        self._build_sidebar(body)

        main = tk.Frame(body, bg=C["bg"])
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._main_frame = main

        self._build_auth_bar(main)

        self._pages: Dict[str, tk.Frame] = {}
        for k in ("explorer", "search", "commits", "operations", "about"):
            f = tk.Frame(main, bg=C["bg"])
            self._pages[k] = f

        self._build_explorer()
        self._build_search()
        self._build_commits()
        self._build_ops()
        self._build_about()

        self._build_statusbar(root_f)
        self._build_toasts(root_f)
        self._build_ctx()
        self._nav_to("explorer")

    # ── Top Bar ──────────────────────────────────────────────────────────
    def _build_topbar(self, parent):
        C = self.C
        tk.Frame(parent, bg=C["accent"], height=2).pack(fill=tk.X)
        bar = tk.Frame(parent, bg=C["topbar"], height=50)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)
        inner = tk.Frame(bar, bg=C["topbar"])
        inner.pack(fill=tk.BOTH, expand=True, padx=16)

        # Logo
        logo_f = tk.Frame(inner, bg=C["topbar"])
        logo_f.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(logo_f, text="◈", bg=C["topbar"], fg=C["accent"],
                 font=(FUI, 22, "bold")).pack(side=tk.LEFT, padx=(0, 8), pady=8)
        tk.Label(logo_f, text="GitView", bg=C["topbar"], fg=C["fg_bright"],
                 font=(FBOLD, 15, "bold")).pack(side=tk.LEFT, pady=12)
        tk.Label(logo_f, text=f" v{VER}", bg=C["topbar"], fg=C["fg_dim"],
                 font=(FUI, 8)).pack(side=tk.LEFT, pady=16)

        # Right controls
        rf = tk.Frame(inner, bg=C["topbar"])
        rf.pack(side=tk.RIGHT, fill=tk.Y, pady=8)

        for txt, cmd, tip, st in [
            ("❓", self._show_help, "Help (F1)", "ghost"),
            ("⌘", self._open_palette, "Command Palette (Ctrl+K)", "ghost"),
            ("⭐", lambda: webbrowser.open("https://github.com/dragonked2"), "GitHub", "ghost"),
        ]:
            b = _btn(rf, txt, cmd, style=st, C=C, font=(FUI, 13), px=8, py=5)
            b.pack(side=tk.RIGHT, padx=2)
            Tip(b, tip, C)

        self._theme_btn = _btn(rf, "🌙", self._toggle_theme,
                                style="ghost", C=C, font=(FUI, 13), px=8, py=5)
        self._theme_btn.pack(side=tk.RIGHT, padx=2)
        Tip(self._theme_btn, "Toggle Theme (Ctrl+T)", C)

        self._conn_dot = tk.Label(rf, text="●", bg=C["topbar"],
                                   fg=C["fg_dim"], font=(FUI, 10))
        self._conn_dot.pack(side=tk.RIGHT, padx=(0, 8), pady=10)
        Tip(self._conn_dot, "Connection Status", C)

    # ── Sidebar Navigation ───────────────────────────────────────────────
    def _build_sidebar(self, parent):
        C = self.C
        sb = tk.Frame(parent, bg=C["sidebar"], width=216)
        sb.pack(side=tk.LEFT, fill=tk.Y)
        sb.pack_propagate(False)
        self._sidebar = sb

        # Right border
        tk.Frame(sb, bg=C["border"], width=1).pack(side=tk.RIGHT, fill=tk.Y)

        inner = tk.Frame(sb, bg=C["sidebar"])
        inner.pack(fill=tk.BOTH, expand=True, pady=10)

        self._nav_items: Dict[str, Tuple] = {}
        NAV = [
            ("explorer",   "  📁  Explorer",    "Browse files & repos (Alt+1)"),
            ("search",     "  🔍  Search",       "Search everything (Alt+2)"),
            ("commits",    "  ◎  Commits",      "History & diffs (Alt+3)"),
            ("operations", "  ⚡  Operations",   "Upload, download, manage (Alt+4)"),
            ("about",      "  ℹ  About",        "About GitView (Alt+5)"),
        ]
        for key, label, tip in NAV:
            f = tk.Frame(inner, bg=C["sidebar"], cursor="hand2")
            f.pack(fill=tk.X, padx=6, pady=1)
            lbl = tk.Label(f, text=label, bg=C["sidebar"], fg=C["fg_muted"],
                           font=(FUI, 10), anchor=tk.W, padx=6, pady=9,
                           cursor="hand2")
            lbl.pack(fill=tk.X)
            for w in (f, lbl):
                w.bind("<Button-1>", lambda e, k=key: self._nav_to(k))
                w.bind("<Enter>",    lambda e, ff=f, ll=lbl, k=key: self._nav_hover(ff, ll, k, True))
                w.bind("<Leave>",    lambda e, ff=f, ll=lbl, k=key: self._nav_hover(ff, ll, k, False))
            self._nav_items[key] = (f, lbl)
            Tip(f, tip, C)

        # FIX: use 'pad' not 'pady' — this was the original crash
        _sep(inner, C, pad=8)

        # Index status card
        idx_box = tk.Frame(inner, bg=C["sidebar_hl"],
                           highlightbackground=C["border"],
                           highlightthickness=1)
        idx_box.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(idx_box, text="COMMIT INDEX", bg=C["sidebar_hl"],
                 fg=C["fg_dim"], font=(FUI, 7, "bold"),
                 padx=8, pady=4).pack(anchor=tk.W)
        self._idx_commits_lbl = tk.Label(idx_box, text="0 commits",
                                          bg=C["sidebar_hl"], fg=C["fg_muted"],
                                          font=(FMONO, 9), padx=8)
        self._idx_commits_lbl.pack(anchor=tk.W)
        self._idx_repos_lbl = tk.Label(idx_box, text="0 repos",
                                        bg=C["sidebar_hl"], fg=C["fg_dim"],
                                        font=(FUI, 7), padx=8, pady=4)
        self._idx_repos_lbl.pack(anchor=tk.W)
        self._idx_prog = ttk.Progressbar(idx_box, mode="indeterminate",
                                          style="TProgressbar", length=150)
        self._idx_prog.pack(fill=tk.X, padx=6, pady=(0, 6))

        # Export button
        self._exp_btn = _btn(idx_box, "📥 Export CSV", self._export_commits_csv,
                              style="ghost2", C=C, font=(FUI, 7), px=6, py=3)
        self._exp_btn.pack(fill=tk.X, padx=6, pady=(0, 6))

        _sep(inner, C, pad=4)

        # Connection info
        self._sb_user_lbl = tk.Label(inner, text="Not connected",
                                      bg=C["sidebar"], fg=C["fg_dim"],
                                      font=(FUI, 8), padx=14, anchor=tk.W)
        self._sb_user_lbl.pack(fill=tk.X, pady=2)
        self._sb_mode_lbl = tk.Label(inner, text="",
                                      bg=C["sidebar"], fg=C["fg_dim"],
                                      font=(FUI, 7), padx=14, anchor=tk.W)
        self._sb_mode_lbl.pack(fill=tk.X)

    def _nav_hover(self, f, lbl, key: str, on: bool):
        if key == self._current_nav: return
        C = self.C
        bg = C["sidebar_hl"] if on else C["sidebar"]
        fg = C["fg"] if on else C["fg_muted"]
        f.config(bg=bg)
        lbl.config(bg=bg, fg=fg)

    def _nav_to(self, key: str):
        C = self.C
        prev = self._current_nav
        if prev in self._nav_items:
            f, l = self._nav_items[prev]
            f.config(bg=C["sidebar"])
            l.config(bg=C["sidebar"], fg=C["fg_muted"])
        self._current_nav = key
        if key in self._nav_items:
            f, l = self._nav_items[key]
            f.config(bg=C["sidebar_active"])
            l.config(bg=C["sidebar_active"], fg=C["accent2"])
        for k, pg in self._pages.items():
            if k != key:
                pg.pack_forget()
            else:
                pg.pack(fill=tk.BOTH, expand=True)

    # ── Auth Bar ─────────────────────────────────────────────────────────
    def _build_auth_bar(self, parent):
        C = self.C
        bar = tk.Frame(parent, bg=C["card"],
                       highlightbackground=C["border"],
                       highlightthickness=1)
        bar.pack(fill=tk.X, padx=8, pady=(6, 4))
        self._auth_bar = bar

        inner = tk.Frame(bar, bg=C["card"])
        inner.pack(fill=tk.X, padx=14, pady=10)

        # Mode toggle
        mode_f = tk.Frame(inner, bg=C["card"])
        mode_f.pack(side=tk.LEFT, fill=tk.Y)
        mrow = tk.Frame(mode_f, bg=C["card"])
        mrow.pack(anchor=tk.W)

        self._tok_tab = _btn(mrow, "🔑 Token", self._sw_token,
                              style="accent", C=C, font=(FUI, 8, "bold"), px=10, py=4)
        self._tok_tab.pack(side=tk.LEFT)
        self._pub_tab = _btn(mrow, "👤 Public", self._sw_public,
                              style="ghost2", C=C, font=(FUI, 8, "bold"), px=10, py=4)
        self._pub_tab.pack(side=tk.LEFT, padx=(3, 0))

        # Token frame
        self._tok_f = tk.Frame(mode_f, bg=C["card"])
        _lbl(self._tok_f, "PERSONAL ACCESS TOKEN", C, 6, True, bg=C["card"]).pack(anchor=tk.W, pady=(5, 2))
        trow = tk.Frame(self._tok_f, bg=C["card"])
        trow.pack(anchor=tk.W)
        self.tok_var = tk.StringVar()
        self.tok_entry = _entry(trow, self.tok_var, C, 50, True, "•")
        self.tok_entry.pack(side=tk.LEFT, ipady=6, padx=(0, 3))
        self.tok_entry.bind("<Return>", lambda _: self._connect_token())
        self._eye = _btn(trow, "👁", self._toggle_eye,
                          style="ghost2", C=C, font=(FUI, 11), px=6, py=5)
        self._eye.pack(side=tk.LEFT, padx=(0, 3))
        self.conn_btn = _btn(trow, "  Connect  ", self._connect_token,
                              style="accent", C=C, font=(FUI, 9, "bold"), px=14, py=6)
        self.conn_btn.pack(side=tk.LEFT)
        self.discon_btn = _btn(trow, "✕", self._disconnect,
                                style="red", C=C, font=(FUI, 9), px=8, py=6)
        self.discon_btn.pack(side=tk.LEFT, padx=(3, 0))
        self.discon_btn.pack_forget()

        lnk = tk.Label(self._tok_f,
                        text="Generate token at github.com/settings/tokens →",
                        bg=C["card"], fg=C["accent"], font=(FUI, 7), cursor="hand2")
        lnk.pack(anchor=tk.W, pady=(3, 0))
        lnk.bind("<Button-1>",
                  lambda _: webbrowser.open(
                      "https://github.com/settings/tokens/new?description=GitView&scopes=repo"))

        # Public frame
        self._pub_f = tk.Frame(mode_f, bg=C["card"])
        _lbl(self._pub_f, "USERNAME OR github.com/username", C, 6, True, bg=C["card"]).pack(anchor=tk.W, pady=(5, 2))
        prow = tk.Frame(self._pub_f, bg=C["card"])
        prow.pack(anchor=tk.W)
        self.pub_var = tk.StringVar()
        self.pub_entry = _entry(prow, self.pub_var, C, 36, True)
        self.pub_entry.pack(side=tk.LEFT, ipady=6, padx=(0, 4))
        self.pub_entry.bind("<Return>", lambda _: self._connect_public())
        for name in ("torvalds", "microsoft", "google", "openai"):
            _btn(prow, name,
                  lambda v=name: (self.pub_var.set(v), self._connect_public()),
                  style="ghost2", C=C, font=(FUI, 7), px=7, py=6).pack(side=tk.LEFT, padx=2)
        _btn(prow, "  Browse  ", self._connect_public,
              style="green", C=C, font=(FUI, 9, "bold"), px=14, py=6).pack(side=tk.LEFT, padx=(4, 0))

        # User info panel (right side of auth bar)
        tk.Frame(inner, bg=C["border"], width=1).pack(side=tk.RIGHT, fill=tk.Y, padx=14)
        uinfo = tk.Frame(inner, bg=C["card"])
        uinfo.pack(side=tk.RIGHT, fill=tk.Y)
        self._avatar = tk.Label(uinfo, text="◯", bg=C["card"], fg=C["fg_dim"], font=(FUI, 28))
        self._avatar.pack(side=tk.LEFT, padx=(0, 12))
        uc = tk.Frame(uinfo, bg=C["card"])
        uc.pack(side=tk.LEFT, fill=tk.Y, pady=4)
        self._uname  = tk.Label(uc, text="Not Connected",         bg=C["card"], fg=C["fg_muted"], font=(FBOLD, 12, "bold"))
        self._uname.pack(anchor=tk.W)
        self._umeta  = tk.Label(uc, text="Select Token or Public mode", bg=C["card"], fg=C["fg_dim"], font=(FUI, 8))
        self._umeta.pack(anchor=tk.W)
        self._ubio   = tk.Label(uc, text="",                      bg=C["card"], fg=C["fg_dim"], font=(FUI, 8))
        self._ubio.pack(anchor=tk.W)
        self._ubadge = tk.Label(uc, text="",                      bg=C["card"], fg=C["fg_dim"], font=(FUI, 7, "bold"))
        self._ubadge.pack(anchor=tk.W, pady=(3, 0))

        # Repo meta panel
        tk.Frame(inner, bg=C["border"], width=1).pack(side=tk.RIGHT, fill=tk.Y, padx=14)
        rm = tk.Frame(inner, bg=C["card"])
        rm.pack(side=tk.RIGHT, fill=tk.Y, pady=4)
        self._repo_meta = tk.Label(rm, text="", bg=C["card"], fg=C["fg_muted"],
                                    font=(FUI, 8), justify=tk.RIGHT)
        self._repo_meta.pack(anchor=tk.E)
        self._repo_desc = tk.Label(rm, text="", bg=C["card"], fg=C["fg_dim"],
                                    font=(FUI, 8), justify=tk.RIGHT, wraplength=260)
        self._repo_desc.pack(anchor=tk.E)

        self._tok_f.pack(fill=tk.X, pady=(5, 0))

    def _sw_token(self):
        self.auth_mode = "token"
        C = self.C
        self._tok_tab.config(bg=C["accent"], fg=C["fg_bright"])
        self._pub_tab.config(bg=C["surface2"], fg=C["fg_muted"])
        self._pub_f.pack_forget()
        self._tok_f.pack(fill=tk.X, pady=(5, 0))

    def _sw_public(self):
        self.auth_mode = "public"
        C = self.C
        self._pub_tab.config(bg=C["accent"], fg=C["fg_bright"])
        self._tok_tab.config(bg=C["surface2"], fg=C["fg_muted"])
        self._tok_f.pack_forget()
        self._pub_f.pack(fill=tk.X, pady=(5, 0))

    def _toggle_eye(self):
        self._show_tok = not self._show_tok
        self.tok_entry.config(show="" if self._show_tok else "•")

    # ── Explorer Tab ─────────────────────────────────────────────────────
    def _build_explorer(self):
        C = self.C
        f = self._pages["explorer"]

        # Controls bar
        ctrl = tk.Frame(f, bg=C["card"], highlightbackground=C["border"], highlightthickness=1)
        ctrl.pack(fill=tk.X, padx=8, pady=(0, 4))
        ci = tk.Frame(ctrl, bg=C["card"])
        ci.pack(fill=tk.X, padx=12, pady=8)

        # Repo selector
        g1 = tk.Frame(ci, bg=C["card"])
        g1.pack(side=tk.LEFT, padx=(0, 10))
        _lbl(g1, "REPOSITORY", C, 6, True, bg=C["card"]).pack(anchor=tk.W, pady=(0, 2))
        self.repo_var = tk.StringVar()
        self.repo_cb = ttk.Combobox(g1, textvariable=self.repo_var,
                                     state="readonly", font=(FUI, 10), width=34)
        self.repo_cb.pack(side=tk.LEFT, ipady=4)
        self.repo_cb.bind("<<ComboboxSelected>>", self._on_repo_sel)

        # Branch selector
        g2 = tk.Frame(ci, bg=C["card"])
        g2.pack(side=tk.LEFT, padx=(0, 10))
        _lbl(g2, "BRANCH", C, 6, True, bg=C["card"]).pack(anchor=tk.W, pady=(0, 2))
        self.branch_var = tk.StringVar()
        self.branch_cb = ttk.Combobox(g2, textvariable=self.branch_var,
                                       state="readonly", font=(FUI, 10), width=20)
        self.branch_cb.pack(side=tk.LEFT, ipady=4)
        self.branch_cb.bind("<<ComboboxSelected>>", self._on_branch_sel)

        # Nav buttons
        nav_f = tk.Frame(ci, bg=C["card"])
        nav_f.pack(side=tk.LEFT, padx=(0, 10), fill=tk.Y, pady=2)
        _lbl(nav_f, " ", C, 6, bg=C["card"]).pack(anchor=tk.W)
        for txt, cmd, tip in [
            ("⌂", self._go_home,       "Root (Home)"),
            ("↑", self._go_up,         "Up (Backspace)"),
            ("↻", self._refresh_dir,   "Refresh (F5)"),
            ("📌", self._pin_repo,      "Pin/Unpin Repo"),
        ]:
            b = _btn(nav_f, txt, cmd, style="ghost2", C=C, font=(FUI, 11), px=8, py=4)
            b.pack(side=tk.LEFT, padx=1)
            Tip(b, tip, C)

        # Filter
        ff = tk.Frame(ci, bg=C["card"])
        ff.pack(side=tk.LEFT)
        _lbl(ff, "FILTER FILES", C, 6, True, bg=C["card"]).pack(anchor=tk.W, pady=(0, 2))
        self.filter_var = tk.StringVar()
        fe = _entry(ff, self.filter_var, C, 18)
        fe.pack(side=tk.LEFT, ipady=5)
        self.filter_var.trace_add("write", lambda *_: self._apply_filter())
        Tip(fe, "Filter (Ctrl+F)", C)

        self._fc_lbl = tk.Label(ci, text="", bg=C["card"], fg=C["fg_muted"], font=(FUI, 8))
        self._fc_lbl.pack(side=tk.RIGHT, padx=6)

        # Splitter
        pane = tk.PanedWindow(f, orient=tk.HORIZONTAL, bg=C["border"],
                               sashwidth=4, sashrelief=tk.FLAT)
        pane.pack(fill=tk.BOTH, expand=True, padx=8)

        # ── File tree panel ───────────────────────────────────────────
        tp = tk.Frame(pane, bg=C["surface"],
                      highlightbackground=C["border"], highlightthickness=1)
        pane.add(tp, minsize=320)

        # Breadcrumb bar
        pb = tk.Frame(tp, bg=C["surface2"], height=30)
        pb.pack(fill=tk.X)
        pb.pack_propagate(False)
        self._pb_inner = tk.Frame(pb, bg=C["surface2"])
        self._pb_inner.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, pady=4)
        self._path_lbl = tk.Label(self._pb_inner, text="/", bg=C["surface2"],
                                   fg=C["fg_muted"], font=(FMONO, 8))
        self._path_lbl.pack(side=tk.LEFT, padx=4)
        self._pb_copy_btn = _btn(pb, "📋", self._copy_path, style="ghost", C=C,
              font=(FUI, 9), px=4, py=2)
        self._pb_copy_btn.pack(side=tk.RIGHT, padx=4)
        Tip(self._pb_copy_btn, "Copy path", C)

        # Tree widget
        tw = tk.Frame(tp, bg=C["surface"])
        tw.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(tw, columns=("ico", "kind", "size"),
                                  show="tree headings", selectmode="extended")
        self.tree.heading("#0",   text="  Name", anchor=tk.W,
                           command=lambda: self._sort_col("name"))
        self.tree.heading("ico",  text="",       anchor=tk.CENTER)
        self.tree.heading("kind", text="Type",   anchor=tk.W,
                           command=lambda: self._sort_col("kind"))
        self.tree.heading("size", text="Size",   anchor=tk.W,
                           command=lambda: self._sort_col("size"))
        self.tree.column("#0",   width=360, minwidth=140, stretch=True)
        self.tree.column("ico",  width=30,  minwidth=30,  stretch=False)
        self.tree.column("kind", width=65,  minwidth=50,  stretch=False)
        self.tree.column("size", width=75,  minwidth=55,  stretch=False)
        tvsb = _vsb(tw, self.tree.yview)
        self.tree.configure(yscrollcommand=tvsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tvsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Empty state overlay
        self._inf = tk.Frame(tp, bg=C["surface"])
        tk.Frame(self._inf, bg=C["accent"], height=2, width=60).pack(pady=(30, 0))
        self._inf_icon = tk.Label(self._inf, text="📦", bg=C["surface"],
                                   fg=C["fg_dim"], font=(FUI, 44))
        self._inf_icon.pack(pady=(16, 0))
        self._inf_main = tk.Label(self._inf, text="Select a Repository",
                                   bg=C["surface"], fg=C["fg_muted"],
                                   font=(FBOLD, 13, "bold"))
        self._inf_main.pack(pady=(10, 0))
        self._inf_sub = tk.Label(self._inf, text="Connect and choose a repo from the dropdown above",
                                  bg=C["surface"], fg=C["fg_dim"], font=(FUI, 9))
        self._inf_sub.pack(pady=(4, 0))
        tk.Label(self._inf, text="Ctrl+K → Command Palette",
                 bg=C["surface"], fg=C["fg_dim"], font=(FUI, 8)).pack(pady=(10, 0))
        self._inf.place(relx=0.5, rely=0.5, anchor="center")

        # Bindings
        self.tree.bind("<Double-1>",        self._on_dbl)
        self.tree.bind("<<TreeviewSelect>>", self._on_sel)
        self.tree.bind("<Return>",          self._on_dbl)
        self.tree.bind("<space>",           lambda _: self._expand_preview())
        self.tree.bind("<Home>",            lambda _: self._go_home())
        self.tree.bind("<BackSpace>",       lambda _: self._go_up())

        # ── Preview panel ─────────────────────────────────────────────
        pp = tk.Frame(pane, bg=C["surface"],
                      highlightbackground=C["border"], highlightthickness=1,
                      width=380)
        pane.add(pp, minsize=280)

        phdr = tk.Frame(pp, bg=C["surface2"], height=30)
        phdr.pack(fill=tk.X)
        phdr.pack_propagate(False)
        phdr_inner = tk.Frame(phdr, bg=C["surface2"])
        phdr_inner.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(phdr_inner, text="PREVIEW", bg=C["surface2"], fg=C["fg_dim"],
                 font=(FUI, 7, "bold")).pack(side=tk.LEFT)
        _btn(phdr_inner, "⤢ Open",   self._expand_preview,
              style="ghost", C=C, font=(FUI, 8), px=8, py=2).pack(side=tk.RIGHT)
        _btn(phdr_inner, "🔍 Find",   self._find_in_preview,
              style="ghost", C=C, font=(FUI, 8), px=8, py=2).pack(side=tk.RIGHT, padx=(0, 4))

        pvsb = _vsb(pp, None)
        self.prev_txt = tk.Text(pp, wrap=tk.NONE,
                                 bg=C["surface"], fg=C["fg"], font=(FMONO, 9),
                                 relief=tk.FLAT, highlightthickness=0,
                                 state=tk.DISABLED, padx=10, pady=8,
                                 selectbackground=C["sel"])
        phsb = _hsb(pp, self.prev_txt.xview)
        self.prev_txt.configure(yscrollcommand=pvsb.set, xscrollcommand=phsb.set)
        pvsb.config(command=self.prev_txt.yview)
        phsb.pack(side=tk.BOTTOM, fill=tk.X)
        pvsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.prev_txt.pack(fill=tk.BOTH, expand=True)

        # Preview info label
        self._prev_info = tk.Label(pp, text="", bg=C["surface2"], fg=C["fg_dim"],
                                    font=(FUI, 7), padx=8, pady=2)
        self._prev_info.pack(fill=tk.X, side=tk.BOTTOM)

    # ── Search Tab ───────────────────────────────────────────────────────
    def _build_search(self):
        C = self.C
        f = self._pages["search"]

        # Status banner
        self._banner_f = tk.Frame(f, bg=C["amber_bg"],
                                   highlightbackground=C["amber"],
                                   highlightthickness=1)
        self._banner_f.pack(fill=tk.X, padx=8, pady=(4, 0))
        self._banner_lbl = tk.Label(
            self._banner_f,
            text="ℹ  Connect a GitHub account to begin searching.",
            bg=C["amber_bg"], fg=C["amber"], font=(FUI, 9), padx=12, pady=7)
        self._banner_lbl.pack(anchor=tk.W)

        # Search bar
        sbar = tk.Frame(f, bg=C["card"],
                         highlightbackground=C["border"], highlightthickness=1)
        sbar.pack(fill=tk.X, padx=8, pady=(4, 0))
        si = tk.Frame(sbar, bg=C["card"])
        si.pack(fill=tk.X, padx=12, pady=10)

        self.sq_var = tk.StringVar()
        self.sq_entry = _entry(si, self.sq_var, C, 56, True)
        self.sq_entry.pack(side=tk.LEFT, ipady=8, padx=(0, 6))
        self.sq_entry.bind("<Return>", lambda _: self._do_search())
        self.sq_var.trace_add("write", self._debounce)

        _btn(si, "🕐", self._show_hist, style="ghost2", C=C, font=(FUI, 12), px=8, py=7).pack(side=tk.LEFT)
        self._go_btn = _btn(si, "  Search  ", self._do_search,
                             style="accent", C=C, font=(FUI, 9, "bold"), px=14, py=7)
        self._go_btn.pack(side=tk.LEFT, padx=(4, 0))
        self._stop_btn = _btn(si, "✕", self._cancel_search,
                               style="red", C=C, font=(FUI, 9), px=8, py=7)
        self._stop_btn.pack(side=tk.LEFT, padx=(3, 0))
        self._stop_btn.config(state=tk.DISABLED)
        self._sprog_lbl = tk.Label(si, text="", bg=C["card"], fg=C["fg_muted"], font=(FUI, 8))
        self._sprog_lbl.pack(side=tk.LEFT, padx=10)
        _btn(si, "⭐ Saved", self._show_saved, style="ghost2", C=C, font=(FUI, 8), px=8, py=7).pack(side=tk.RIGHT, padx=3)
        _btn(si, "+ Save",  self._save_search, style="ghost2", C=C, font=(FUI, 8), px=8, py=7).pack(side=tk.RIGHT)

        # Scope bar
        sf2 = tk.Frame(sbar, bg=C["card"])
        sf2.pack(fill=tk.X, padx=12, pady=(0, 8))
        self._scope_var = tk.StringVar(value="Repos")
        self._scope_btns: Dict[str, tk.Button] = {}
        for scope in ("Repos", "Content", "Files", "Commits", "Topics", "Index"):
            b = _btn(sf2, scope,
                      lambda s=scope: self._sel_scope(s),
                      style="active" if scope == "Repos" else "ghost2",
                      C=C, font=(FUI, 8, "bold"), px=10, py=4)
            b.pack(side=tk.LEFT, padx=(0, 3))
            self._scope_btns[scope] = b

        frow = tk.Frame(sf2, bg=C["card"])
        frow.pack(side=tk.LEFT, padx=(12, 0))
        self._lang_var = tk.StringVar()
        self._ext_var  = tk.StringVar()
        for lbl_t, var, w in [("Lang:", self._lang_var, 10), ("Ext:", self._ext_var, 8)]:
            tk.Label(frow, text=lbl_t, bg=C["card"], fg=C["fg_dim"], font=(FUI, 8)).pack(side=tk.LEFT, padx=(8, 2))
            _entry(frow, var, C, w).pack(side=tk.LEFT, ipady=3)

        # Results area
        outer = tk.Frame(f, bg=C["bg"])
        outer.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 0))
        lp = tk.Frame(outer, bg=C["bg"])
        lp.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Results header
        rh = tk.Frame(lp, bg=C["card"], highlightbackground=C["border"],
                       highlightthickness=1, height=34)
        rh.pack(fill=tk.X)
        rh.pack_propagate(False)
        self._rcount = tk.Label(rh, text="", bg=C["card"], fg=C["fg_muted"],
                                 font=(FUI, 8, "bold"))
        self._rcount.pack(side=tk.LEFT, padx=12, pady=8)
        sortf = tk.Frame(rh, bg=C["card"])
        sortf.pack(side=tk.RIGHT, padx=8, pady=5)
        tk.Label(sortf, text="Sort:", bg=C["card"], fg=C["fg_dim"], font=(FUI, 7)).pack(side=tk.LEFT)
        self._sort_var = tk.StringVar(value="relevance")
        for sv, sl in [("relevance", "Relevance"), ("name", "Name"),
                        ("date", "Date"), ("activity", "Activity")]:
            tk.Radiobutton(sortf, text=sl, variable=self._sort_var, value=sv,
                            bg=C["card"], fg=C["fg_muted"], selectcolor=C["surface3"],
                            activebackground=C["card"], font=(FUI, 8),
                            cursor="hand2", command=self._re_sort).pack(side=tk.LEFT, padx=2)

        # Scrollable result list
        rcv_f = tk.Frame(lp, bg=C["bg"])
        rcv_f.pack(fill=tk.BOTH, expand=True)
        self._rcv = tk.Canvas(rcv_f, bg=C["bg"], highlightthickness=0)
        rvsb = _vsb(rcv_f, self._rcv.yview)
        self._rcv.configure(yscrollcommand=rvsb.set)
        rvsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._rcv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._rin = tk.Frame(self._rcv, bg=C["bg"])
        self._rwin = self._rcv.create_window((0, 0), window=self._rin, anchor="nw")
        self._rin.bind("<Configure>", lambda _: self._rcv.configure(scrollregion=self._rcv.bbox("all")))
        self._rcv.bind("<Configure>", lambda e: self._rcv.itemconfig(self._rwin, width=e.width))
        self._rcv.bind("<MouseWheel>", lambda e: self._rcv.yview_scroll(int(-1*(e.delta/120)), "units"))
        self._rcv.bind("<Button-4>",   lambda _: self._rcv.yview_scroll(-1, "units"))
        self._rcv.bind("<Button-5>",   lambda _: self._rcv.yview_scroll(1,  "units"))

        # Pager
        pg_f = tk.Frame(lp, bg=C["card"], highlightbackground=C["border"],
                          highlightthickness=1, height=36)
        pg_f.pack(fill=tk.X, side=tk.BOTTOM)
        pg_f.pack_propagate(False)
        self._pg_f = pg_f
        pg_i = tk.Frame(pg_f, bg=C["card"])
        pg_i.pack(fill=tk.Y, pady=4, padx=8)
        self._pg_prev = _btn(pg_i, "← Prev", lambda: self._pg(-1), style="ghost2", C=C, font=(FUI, 8), px=8, py=3)
        self._pg_prev.pack(side=tk.LEFT)
        self._pg_lbl = tk.Label(pg_i, text="", bg=C["card"], fg=C["fg_muted"], font=(FUI, 8))
        self._pg_lbl.pack(side=tk.LEFT, padx=8)
        self._pg_next = _btn(pg_i, "Next →", lambda: self._pg(1), style="ghost2", C=C, font=(FUI, 8), px=8, py=3)
        self._pg_next.pack(side=tk.LEFT)

        # Detail panel
        dp = tk.Frame(outer, bg=C["card"], highlightbackground=C["border"],
                       highlightthickness=1, width=380)
        dp.pack(side=tk.RIGHT, fill=tk.Y, padx=(6, 0))
        dp.pack_propagate(False)
        dhdr = tk.Frame(dp, bg=C["surface2"], height=30)
        dhdr.pack(fill=tk.X)
        dhdr.pack_propagate(False)
        tk.Label(dhdr, text="DETAILS", bg=C["surface2"], fg=C["fg_dim"],
                 font=(FUI, 7, "bold")).pack(side=tk.LEFT, padx=10, pady=6)
        dvsb = _vsb(dp, None)
        self._det = _txt(dp, C)
        self._det.configure(yscrollcommand=dvsb.set)
        dvsb.config(command=self._det.yview)
        dvsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._det.pack(fill=tk.BOTH, expand=True)
        dbf = tk.Frame(dp, bg=C["card"])
        dbf.pack(fill=tk.X, padx=10, pady=(0, 10))
        self._det_open = _btn(dbf, "🌐 Open on GitHub", lambda: None,
                               style="accent", C=C, font=(FUI, 9), py=5)
        self._det_open.pack(fill=tk.X)
        self._det_nav = _btn(dbf, "📁 Navigate in Explorer", lambda: None,
                              style="ghost2", C=C, font=(FUI, 9), py=5)
        self._det_nav.pack(fill=tk.X, pady=(4, 0))

        self._show_search_empty()

    # ── Commits Tab ──────────────────────────────────────────────────────
    def _build_commits(self):
        C = self.C
        f = self._pages["commits"]

        # Controls
        ctrl = tk.Frame(f, bg=C["card"],
                         highlightbackground=C["border"], highlightthickness=1)
        ctrl.pack(fill=tk.X, padx=8, pady=(0, 4))
        ci = tk.Frame(ctrl, bg=C["card"])
        ci.pack(fill=tk.X, padx=12, pady=8)

        g0 = tk.Frame(ci, bg=C["card"])
        g0.pack(side=tk.LEFT, padx=(0, 10))
        _lbl(g0, "REPOSITORY", C, 6, True, bg=C["card"]).pack(anchor=tk.W, pady=(0, 2))
        self._cr_var = tk.StringVar()
        self._cr_cb = ttk.Combobox(g0, textvariable=self._cr_var,
                                    state="readonly", font=(FUI, 9), width=26)
        self._cr_cb.pack(side=tk.LEFT, ipady=4)

        for attr, lbl_t in [("_cauth_var", "AUTHOR"), ("_cmsg_var", "MESSAGE"), ("_cpath_var", "PATH")]:
            g = tk.Frame(ci, bg=C["card"])
            g.pack(side=tk.LEFT, padx=(0, 8))
            _lbl(g, lbl_t, C, 6, True, bg=C["card"]).pack(anchor=tk.W, pady=(0, 2))
            var = tk.StringVar()
            setattr(self, attr, var)
            _entry(g, var, C, 14).pack(ipady=4)

        ab = tk.Frame(ci, bg=C["card"])
        ab.pack(side=tk.LEFT, padx=(4, 0), fill=tk.Y)
        _lbl(ab, " ", C, 6, bg=C["card"]).pack(anchor=tk.W)
        self._cload_btn = _btn(ab, "  Load Commits  ", self._load_commits,
                                style="accent", C=C, font=(FUI, 9, "bold"), py=5)
        self._cload_btn.pack(side=tk.LEFT)
        self._call_btn = _btn(ab, "  Load ALL Repos  ", self._load_all_repos_commits,
                               style="green", C=C, font=(FUI, 9, "bold"), py=5)
        self._call_btn.pack(side=tk.LEFT, padx=(5, 0))
        self._cstop_btn = _btn(ab, "✕ Stop", self._stop_index,
                                style="red", C=C, font=(FUI, 9), py=5)
        self._cstop_btn.pack(side=tk.LEFT, padx=(4, 0))
        self._cstop_btn.config(state=tk.DISABLED)

        cs = tk.Frame(ci, bg=C["card"])
        cs.pack(side=tk.RIGHT, fill=tk.Y, pady=2)
        self._ctotal_lbl = tk.Label(cs, text="", bg=C["card"], fg=C["fg_muted"], font=(FUI, 9))
        self._ctotal_lbl.pack(anchor=tk.E)
        self._cprog = ttk.Progressbar(cs, mode="indeterminate",
                                       style="TProgressbar", length=130)
        self._cprog.pack(anchor=tk.E, pady=(3, 0))

        # Main splitter
        splitter = tk.PanedWindow(f, orient=tk.HORIZONTAL, bg=C["border"],
                                   sashwidth=4, sashrelief=tk.FLAT)
        splitter.pack(fill=tk.BOTH, expand=True, padx=8)

        # Commit list
        clp = tk.Frame(splitter, bg=C["surface"],
                        highlightbackground=C["border"], highlightthickness=1)
        splitter.add(clp, minsize=340)
        chdr = tk.Frame(clp, bg=C["surface2"], height=30)
        chdr.pack(fill=tk.X)
        chdr.pack_propagate(False)
        tk.Label(chdr, text="TIMELINE", bg=C["surface2"], fg=C["fg_dim"],
                 font=(FUI, 7, "bold")).pack(side=tk.LEFT, padx=10, pady=6)
        self._cmore_btn = _btn(chdr, "⬇ Load More", self._load_more,
                                style="ghost2", C=C, font=(FUI, 8), px=8, py=2)
        self._cmore_btn.pack(side=tk.RIGHT, padx=8, pady=4)
        cw = tk.Frame(clp, bg=C["surface"])
        cw.pack(fill=tk.BOTH, expand=True)
        self.ctree = ttk.Treeview(cw, columns=("sha", "author", "date", "repo"),
                                   show="tree headings", selectmode="browse")
        self.ctree.heading("#0",     text="  Commit Message", anchor=tk.W)
        self.ctree.heading("sha",    text="SHA",    anchor=tk.W)
        self.ctree.heading("author", text="Author", anchor=tk.W)
        self.ctree.heading("date",   text="When",   anchor=tk.W)
        self.ctree.heading("repo",   text="Repo",   anchor=tk.W)
        self.ctree.column("#0",     width=300, minwidth=160, stretch=True)
        self.ctree.column("sha",    width=72,  minwidth=60,  stretch=False)
        self.ctree.column("author", width=110, minwidth=70,  stretch=False)
        self.ctree.column("date",   width=88,  minwidth=65,  stretch=False)
        self.ctree.column("repo",   width=110, minwidth=70,  stretch=False)
        cvsb = _vsb(cw, self.ctree.yview)
        self.ctree.configure(yscrollcommand=cvsb.set)
        self.ctree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cvsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.ctree.bind("<<TreeviewSelect>>", self._on_csel)
        self.ctree.bind("<Double-1>",         self._on_cdbl)

        # Diff panel
        dp = tk.Frame(splitter, bg=C["surface"],
                       highlightbackground=C["border"], highlightthickness=1)
        splitter.add(dp, minsize=480)
        dtabs = ttk.Notebook(dp)
        dtabs.pack(fill=tk.BOTH, expand=True)
        self._dtabs = dtabs

        # Details tab
        meta_f = tk.Frame(dtabs, bg=C["surface"])
        dtabs.add(meta_f, text="  📋 Details  ")
        mvsb = _vsb(meta_f, None)
        self._cmeta = _txt(meta_f, C)
        self._cmeta.configure(yscrollcommand=mvsb.set)
        mvsb.config(command=self._cmeta.yview)
        mvsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._cmeta.pack(fill=tk.BOTH, expand=True)
        mbf = tk.Frame(meta_f, bg=C["surface"])
        mbf.pack(fill=tk.X, padx=10, pady=(0, 10))
        self._copen_btn     = _btn(mbf, "🌐 View on GitHub",  lambda: None, style="accent", C=C, font=(FUI, 9), py=5)
        self._copen_btn.pack(fill=tk.X)
        self._ccopy_btn     = _btn(mbf, "📋 Copy SHA",        lambda: None, style="ghost2", C=C, font=(FUI, 9), py=5)
        self._ccopy_btn.pack(fill=tk.X, pady=(4, 0))
        self._cdownload_btn = _btn(mbf, "📥 Download Patch",  lambda: None, style="ghost2", C=C, font=(FUI, 9), py=5)
        self._cdownload_btn.pack(fill=tk.X, pady=(4, 0))

        # Diff tab
        diff_f = tk.Frame(dtabs, bg=C["surface"])
        dtabs.add(diff_f, text="  Δ Diff  ")
        dsplit = tk.PanedWindow(diff_f, orient=tk.HORIZONTAL, bg=C["border"],
                                 sashwidth=3, sashrelief=tk.FLAT)
        dsplit.pack(fill=tk.BOTH, expand=True)
        flp = tk.Frame(dsplit, bg=C["surface"],
                        highlightbackground=C["border"], highlightthickness=1)
        dsplit.add(flp, minsize=180)
        flhdr = tk.Frame(flp, bg=C["surface2"], height=28)
        flhdr.pack(fill=tk.X)
        flhdr.pack_propagate(False)
        tk.Label(flhdr, text="FILES", bg=C["surface2"], fg=C["fg_dim"],
                 font=(FUI, 7, "bold")).pack(side=tk.LEFT, padx=8, pady=5)
        self._dstat = tk.Label(flhdr, text="", bg=C["surface2"],
                                fg=C["fg_dim"], font=(FUI, 7))
        self._dstat.pack(side=tk.RIGHT, padx=8)
        self.dftree = ttk.Treeview(flp, show="tree", selectmode="browse")
        self.dftree.column("#0", width=200, stretch=True)
        dfvsb = _vsb(flp, self.dftree.yview)
        self.dftree.configure(yscrollcommand=dfvsb.set)
        self.dftree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dfvsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.dftree.bind("<<TreeviewSelect>>", self._on_dfsel)

        dcp = tk.Frame(dsplit, bg=C["surface"])
        dsplit.add(dcp, minsize=320)
        dtbar = tk.Frame(dcp, bg=C["surface2"], height=28)
        dtbar.pack(fill=tk.X)
        dtbar.pack_propagate(False)
        self._dmode = tk.StringVar(value="unified")
        for m, ml in [("unified", "Unified"), ("split", "Side-by-side")]:
            tk.Radiobutton(dtbar, text=ml, variable=self._dmode, value=m,
                            bg=C["surface2"], fg=C["fg_muted"],
                            selectcolor=C["surface3"], activebackground=C["surface2"],
                            font=(FUI, 8), cursor="hand2",
                            command=self._redraw_diff).pack(side=tk.LEFT, padx=(8, 0), pady=5)
        self._dload_lbl = tk.Label(dtbar, text="", bg=C["surface2"],
                                    fg=C["fg_muted"], font=(FUI, 8))
        self._dload_lbl.pack(side=tk.RIGHT, padx=8)
        self._dtxt = tk.Text(dcp, wrap=tk.NONE, bg=C["surface"], fg=C["fg"],
                              font=(FMONO, 9), relief=tk.FLAT, highlightthickness=0,
                              state=tk.DISABLED, padx=8, pady=6,
                              selectbackground=C["sel"], insertbackground=C["fg"])
        dvs = _vsb(dcp, self._dtxt.yview)
        dhs = _hsb(dcp, self._dtxt.xview)
        self._dtxt.configure(yscrollcommand=dvs.set, xscrollcommand=dhs.set)
        dhs.pack(side=tk.BOTTOM, fill=tk.X)
        dvs.pack(side=tk.RIGHT, fill=tk.Y)
        self._dtxt.pack(fill=tk.BOTH, expand=True)

    # ── Operations Tab ───────────────────────────────────────────────────
    def _build_ops(self):
        C = self.C
        f = self._pages["operations"]
        outer = tk.Frame(f, bg=C["bg"])
        outer.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        left = tk.Frame(outer, bg=C["bg"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        self._ocard(left, "📥  Download", [
            ("📦 Download Entire Repository",   self._dl_all,       "accent"),
            ("📁 Download Current Folder",      self._dl_folder,    "default"),
            ("📄 Download Selected Files",      self._dl_selected,  "default"),
            ("🌐 Open Repository in Browser",   self._open_browser, "ghost2"),
        ])
        self._ocard(left, "📤  Upload & Create", [
            ("📤 Upload File to Current Path",  self._upload_file,   "default"),
            ("📁 Upload Entire Folder",         self._upload_folder, "default"),
            ("✏  Create New File",             self._create_file,   "default"),
            ("📂 Create New Folder",            self._create_folder, "default"),
        ])

        right = tk.Frame(outer, bg=C["bg"], width=380)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        right.pack_propagate(False)

        self._ocard(right, "🔧  Repository Actions", [
            ("➕ Create New Repository",              self._create_repo,            "accent"),
            ("🔄 Refresh All Repositories",           self._load_repos,             "default"),
            ("◎ Load Commit History",                self._load_commits,           "default"),
            ("⚙ Index ALL Repos (All Commits)",      self._load_all_repos_commits, "green"),
            ("📥 Export Indexed Commits to CSV",      self._export_commits_csv,     "ghost2"),
        ])

        # Progress card
        pc = tk.Frame(right, bg=C["card"],
                       highlightbackground=C["border"], highlightthickness=1)
        pc.pack(fill=tk.X, pady=(0, 8))
        ph = tk.Frame(pc, bg=C["surface2"], height=30)
        ph.pack(fill=tk.X)
        ph.pack_propagate(False)
        tk.Label(ph, text="PROGRESS", bg=C["surface2"], fg=C["fg_dim"],
                 font=(FUI, 7, "bold")).pack(side=tk.LEFT, padx=10, pady=6)
        pb_w = tk.Frame(pc, bg=C["card"])
        pb_w.pack(fill=tk.X, padx=10, pady=(6, 4))
        self._prog = ttk.Progressbar(pb_w, mode="indeterminate", style="TProgressbar")
        self._prog.pack(fill=tk.X)
        self._prog_var = tk.StringVar(value="No active operations")
        tk.Label(pc, textvariable=self._prog_var, bg=C["card"], fg=C["fg_muted"],
                 font=(FUI, 8), wraplength=320, justify=tk.LEFT).pack(
                     padx=10, pady=(0, 8), anchor=tk.W)

        # Log card
        lc = tk.Frame(right, bg=C["card"],
                       highlightbackground=C["border"], highlightthickness=1)
        lc.pack(fill=tk.BOTH, expand=True)
        lh = tk.Frame(lc, bg=C["surface2"], height=30)
        lh.pack(fill=tk.X)
        lh.pack_propagate(False)
        tk.Label(lh, text="OPERATION LOG", bg=C["surface2"], fg=C["fg_dim"],
                 font=(FUI, 7, "bold")).pack(side=tk.LEFT, padx=10, pady=6)
        _btn(lh, "Clear", self._clear_log, style="ghost", C=C, font=(FUI, 7), px=8, py=3).pack(
            side=tk.RIGHT, padx=8, pady=4)
        lvsb = _vsb(lc, None)
        self._log_txt = _txt(lc, C, mono=True)
        self._log_txt.configure(yscrollcommand=lvsb.set)
        lvsb.config(command=self._log_txt.yview)
        lvsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._log_txt.pack(fill=tk.BOTH, expand=True)

    def _ocard(self, parent, title: str, actions: List[Tuple]):
        C = self.C
        card = tk.Frame(parent, bg=C["card"],
                         highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill=tk.X, pady=(0, 8))
        hdr = tk.Frame(card, bg=C["surface2"], height=30)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text=title, bg=C["surface2"], fg=C["fg_muted"],
                 font=(FUI, 8, "bold")).pack(side=tk.LEFT, padx=10, pady=6)
        bi = tk.Frame(card, bg=C["card"])
        bi.pack(fill=tk.X, padx=10, pady=8)
        for label, cmd, style in actions:
            _btn(bi, label, cmd, style=style, C=C, font=(FUI, 9), py=6).pack(
                fill=tk.X, pady=(0, 4))

    # ── About Tab ────────────────────────────────────────────────────────
    def _build_about(self):
        C = self.C
        f = self._pages["about"]
        outer = tk.Frame(f, bg=C["bg"])
        outer.pack(fill=tk.BOTH, expand=True)
        # Scrollable wrapper
        cv = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        vsb = _vsb(outer, cv.yview)
        cv.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        cv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        w = tk.Frame(cv, bg=C["bg"])
        wid = cv.create_window((0, 0), window=w, anchor="nw")
        w.bind("<Configure>", lambda _: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>", lambda e: cv.itemconfig(wid, width=e.width))
        cv.bind("<MouseWheel>", lambda e: cv.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Hero section
        hero = tk.Frame(w, bg=C["accent_dim"],
                         highlightbackground=C["border_hi"], highlightthickness=1)
        hero.pack(fill=tk.X, padx=60, pady=30)
        tk.Frame(hero, bg=C["accent"], height=3).pack(fill=tk.X)
        hi = tk.Frame(hero, bg=C["accent_dim"])
        hi.pack(fill=tk.X, padx=40, pady=30)
        tk.Label(hi, text="◈", bg=C["accent_dim"], fg=C["accent"],
                 font=(FUI, 56, "bold")).pack(side=tk.LEFT, padx=(0, 24))
        hc = tk.Frame(hi, bg=C["accent_dim"])
        hc.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(hc, text=f"GitView  v{VER}", bg=C["accent_dim"], fg=C["fg_bright"],
                 font=(FBOLD, 28, "bold")).pack(anchor=tk.W)
        tk.Label(hc, text="Enterprise GitHub Intelligence Platform",
                 bg=C["accent_dim"], fg=C["accent2"], font=(FUI, 13)).pack(anchor=tk.W, pady=(4, 0))
        tk.Label(hc, text="Ali Essam  ·  Egypt 🇪🇬  ·  @dragonked2",
                 bg=C["accent_dim"], fg=C["fg_muted"], font=(FUI, 10)).pack(anchor=tk.W, pady=(8, 0))

        # Feature grid
        features = [
            ("📁 File Explorer",  "Browse any GitHub repo tree, filter files, preview with syntax highlighting"),
            ("🔍 6-Scope Search", "Repos · Content · Files · Commits · Topics · Index search engines"),
            ("◎ Commit History", "Load all commits, diff viewer with unified & side-by-side modes"),
            ("⚡ Operations",     "Upload, download, create repos/files/folders with write token"),
            ("⌨ Keyboard First", "Ctrl+K palette, Alt+1-5 nav, full shortcut suite"),
            ("🎨 Dual Theme",     "Dark & light modes, persistent config, live TTK style updates"),
        ]
        gf = tk.Frame(w, bg=C["bg"])
        gf.pack(fill=tk.X, padx=60, pady=(0, 20))
        cols = 3
        for idx, (title, desc) in enumerate(features):
            row_idx = idx // cols
            col_idx = idx % cols
            if col_idx == 0:
                row_f = tk.Frame(gf, bg=C["bg"])
                row_f.pack(fill=tk.X, pady=4)
            card = tk.Frame(row_f, bg=C["card"],
                             highlightbackground=C["border"], highlightthickness=1)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
            tk.Label(card, text=title, bg=C["card"], fg=C["accent2"],
                     font=(FBOLD, 10, "bold"), padx=12, pady=8).pack(anchor=tk.W)
            tk.Label(card, text=desc, bg=C["card"], fg=C["fg_muted"],
                     font=(FUI, 8), padx=12, pady=6,
                     wraplength=200, justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 4))

        # Changelog
        cl_f = tk.Frame(w, bg=C["card"],
                         highlightbackground=C["border"], highlightthickness=1)
        cl_f.pack(fill=tk.X, padx=60, pady=(0, 20))
        ch = tk.Frame(cl_f, bg=C["surface2"], height=32)
        ch.pack(fill=tk.X)
        ch.pack_propagate(False)
        tk.Label(ch, text=f"WHAT'S NEW IN v{VER}", bg=C["surface2"], fg=C["fg_dim"],
                 font=(FUI, 8, "bold"), padx=14).pack(side=tk.LEFT, pady=6)
        changes = [
            ("🔴 FIXED",  "Critical crash: pady tuple in tk.Label (_tkinter.TclError) — fixed"),
            ("🔴 FIXED",  "Windows crash: %-d strftime format replaced with cross-platform code"),
            ("🔴 FIXED",  "API double-call bug in _load_single_repo: r.json() called twice"),
            ("🟢 NEW",    "Clickable breadcrumb — click any path segment to navigate there"),
            ("🟢 NEW",    "Rate limit tracker in status bar with color-coded warning levels"),
            ("🟢 NEW",    "Command palette redesigned: grouped sections, separator labels, footer hints"),
            ("🟢 NEW",    "Arrow key navigation in command palette with separator skipping"),
            ("🟢 NEW",    "Toast close button (×) for dismissing notifications early"),
            ("🟢 NEW",    "Status bar color-coding: green/amber/red for ok/warn/error messages"),
            ("🟡 IMPROVED","Empty state: better icon, subtitle, and keyboard hint"),
            ("🟡 IMPROVED","Toast: top accent stripe + close button + wider text area"),
            ("🟡 IMPROVED","About page: scrollable hero + feature grid + changelog"),
        ]
        for badge, msg in changes:
            row = tk.Frame(cl_f, bg=C["card"])
            row.pack(fill=tk.X, padx=12, pady=2)
            col = C["red"] if "FIXED" in badge else C["green"] if "NEW" in badge else C["amber"]
            tk.Label(row, text=badge, bg=C["card"], fg=col,
                     font=(FUI, 7, "bold"), width=12, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=msg, bg=C["card"], fg=C["fg_muted"],
                     font=(FUI, 8), anchor=tk.W).pack(side=tk.LEFT, fill=tk.X)
        tk.Frame(cl_f, height=8, bg=C["card"]).pack()

        # Links
        br = tk.Frame(w, bg=C["bg"])
        br.pack(pady=24)
        for txt, url, st in [
            ("  LinkedIn  ",  "https://www.linkedin.com/in/dragonked2", "accent"),
            ("  GitHub  ",    "https://github.com/dragonked2",          "ghost2"),
            ("  Get Token  ", "https://github.com/settings/tokens/new", "ghost2"),
        ]:
            _btn(br, txt, lambda u=url: webbrowser.open(u),
                  style=st, C=C, font=(FUI, 10), px=18, py=9).pack(side=tk.LEFT, padx=5)

    # ── Status Bar ───────────────────────────────────────────────────────
    def _build_statusbar(self, parent):
        C = self.C
        sb = tk.Frame(parent, bg=C["statusbar"],
                       highlightbackground=C["sep"],
                       highlightthickness=1, height=26)
        sb.pack(fill=tk.X, side=tk.BOTTOM)
        sb.pack_propagate(False)
        self._status = tk.Label(sb, text="  Ready", bg=C["statusbar"],
                                 fg=C["fg_dim"], font=(FUI, 8))
        self._status.pack(side=tk.LEFT, padx=4)
        # Rate limit display
        self._rate_lbl = tk.Label(sb, text="", bg=C["statusbar"],
                                   fg=C["fg_dim"], font=(FUI, 8))
        self._rate_lbl.pack(side=tk.RIGHT, padx=12)
        self._idx_status = tk.Label(sb, text="", bg=C["statusbar"],
                                     fg=C["fg_dim"], font=(FUI, 8))
        self._idx_status.pack(side=tk.RIGHT, padx=4)
        # Poll rate limit every 5s
        self._poll_rate()

    def _poll_rate(self):
        try:
            rem = getattr(self.sess, "_rate_remaining", -1)
            lim = getattr(self.sess, "_rate_limit",     -1)
            if rem >= 0 and lim > 0:
                pct = rem / lim
                col = (self.C["green"] if pct > 0.5 else
                       self.C["amber"] if pct > 0.15 else
                       self.C["red"])
                self._rate_lbl.config(text=f"API: {rem:,}/{lim:,}", fg=col)
            elif rem == 0:
                self._rate_lbl.config(text="⚠ Rate limited", fg=self.C["red"])
        except:
            pass
        self.root.after(5000, self._poll_rate)

    # ── Toast Notifications ───────────────────────────────────────────────
    def _build_toasts(self, parent):
        self._toast_root = parent

    def _toast(self, msg: str, kind: str = "info", duration: int = 3000):
        self._toast_queue.put((msg, kind, duration))

    def _poll_toasts(self):
        try:
            if not self._toast_queue.empty():
                msg, kind, dur = self._toast_queue.get_nowait()
                self._show_toast(msg, kind, dur)
        except:
            pass
        self.root.after(100, self._poll_toasts)

    def _show_toast(self, msg: str, kind: str, duration: int):
        C = self.C
        KINDS = {
            "ok":   (C["green_bg"], C["green"],  "✓"),
            "err":  (C["red_bg"],   C["red"],    "✕"),
            "warn": (C["amber_bg"], C["amber"],  "⚠"),
            "info": (C["accent_bg"],C["accent2"],"ℹ"),
        }
        bg, fg, icon = KINDS.get(kind, KINDS["info"])
        t = tk.Toplevel(self.root)
        t.wm_overrideredirect(True)
        t.wm_attributes("-topmost", True)
        t.configure(bg=C["border_hi"])
        # Position bottom-right with margin
        rw = self.root.winfo_width()
        rh = self.root.winfo_height()
        rx = self.root.winfo_x()
        ry = self.root.winfo_y()
        toast_w = 380
        w = rx + rw - toast_w - 16
        h = ry + rh - 90
        t.wm_geometry(f"+{w}+{h}")

        outer = tk.Frame(t, bg=bg, highlightbackground=fg,
                          highlightthickness=1)
        outer.pack()
        # Top accent stripe
        tk.Frame(outer, bg=fg, height=2).pack(fill=tk.X)
        row = tk.Frame(outer, bg=bg, padx=14, pady=10)
        row.pack()
        tk.Label(row, text=icon, bg=bg, fg=fg,
                 font=(FUI, 12, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(row, text=msg[:90], bg=bg, fg=fg, font=(FUI, 9),
                 wraplength=280, justify=tk.LEFT).pack(side=tk.LEFT)
        # Close button
        def _close():
            try: t.destroy()
            except: pass
        close_btn = tk.Label(row, text="×", bg=bg, fg=fg,
                              font=(FUI, 12, "bold"), cursor="hand2", padx=6)
        close_btn.pack(side=tk.RIGHT, padx=(8, 0))
        close_btn.bind("<Button-1>", lambda _: _close())

        # Fade out after duration
        self.root.after(duration, lambda: _close() if t.winfo_exists() else None)

    # ── Context Menu ─────────────────────────────────────────────────────
    def _build_ctx(self):
        C = self.C
        self._ctx = tk.Menu(self.root, tearoff=0, bg=C["surface2"], fg=C["fg"],
                             activebackground=C["sel"], activeforeground=C["accent2"],
                             font=(FUI, 9), relief=tk.FLAT, bd=0)
        self._ctx.add_command(label="  📂  Open / Preview",   command=self._on_dbl)
        self._ctx.add_command(label="  ⤢  Open in Window",   command=self._expand_preview)
        self._ctx.add_command(label="  📥  Download",          command=self._dl_selected)
        self._ctx.add_command(label="  🌐  Open on GitHub",    command=self._open_sel_browser)
        self._ctx.add_separator()
        self._ctx.add_command(label="  📋  Copy Path",         command=self._copy_path)
        self._ctx.add_separator()
        self._ctx.add_command(label="  ✏  Rename",            command=self._rename_sel)
        self._ctx.add_command(label="  🗑  Delete",            command=self._delete_sel)
        self.tree.bind("<Button-3>", self._show_ctx)
        self.tree.bind("<Button-2>", self._show_ctx)

    def _show_ctx(self, e):
        iid = self.tree.identify_row(e.y)
        if iid:
            self.tree.selection_set(iid)
        self._ctx.post(e.x_root, e.y_root)

    # ── Keyboard Shortcuts ───────────────────────────────────────────────
    def _shortcuts(self):
        binds = [
            ("<Control-k>",  self._open_palette),
            ("<Control-K>",  self._open_palette),
            ("<Control-f>",  lambda e: (self._nav_to("explorer"),
                                         self.filter_var.set(""))),
            ("<Control-d>",  lambda e: self._dl_selected()),
            ("<Control-u>",  lambda e: self._upload_file()),
            ("<Control-n>",  lambda e: self._create_file()),
            ("<Control-t>",  lambda e: self._toggle_theme()),
            ("<Control-g>",  lambda e: self._find_in_preview()),
            ("<F5>",         lambda e: self._load_repos()),
            ("<F1>",         lambda e: self._show_help()),
            ("<F2>",         lambda e: self._rename_sel()),
            ("<Delete>",     lambda e: self._delete_sel()),
            ("<Escape>",     lambda e: self._cancel_search()),
            # Alt+1–5 nav
            ("<Alt-1>",      lambda e: self._nav_to("explorer")),
            ("<Alt-2>",      lambda e: self._nav_to("search")),
            ("<Alt-3>",      lambda e: self._nav_to("commits")),
            ("<Alt-4>",      lambda e: self._nav_to("operations")),
            ("<Alt-5>",      lambda e: self._nav_to("about")),
        ]
        for k, fn in binds:
            self.root.bind(k, fn)

    # ── Command Palette ──────────────────────────────────────────────────
    def _open_palette(self, _=None):
        if self._cp_win and self._cp_win.winfo_exists():
            self._cp_win.focus_set()
            return
        C = self.C
        self._cp_win = win = tk.Toplevel(self.root)
        win.wm_overrideredirect(True)
        win.wm_attributes("-topmost", True)
        win.configure(bg=C["border_hi"])
        x = self.root.winfo_x() + (self.root.winfo_width() - 680) // 2
        y = self.root.winfo_y() + 70
        win.wm_geometry(f"680x500+{x}+{y}")
        wrap = tk.Frame(win, bg=C["surface"], padx=1, pady=1)
        wrap.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        # Accent bar
        tk.Frame(wrap, bg=C["accent"], height=2).pack(fill=tk.X)
        # Search row
        sr = tk.Frame(wrap, bg=C["surface"])
        sr.pack(fill=tk.X, padx=0)
        tk.Label(sr, text="⌘", bg=C["surface"], fg=C["accent"],
                 font=(FUI, 16, "bold")).pack(side=tk.LEFT, padx=14, pady=12)
        pv = tk.StringVar()
        pe = tk.Entry(sr, textvariable=pv, relief=tk.FLAT,
                       bg=C["surface"], fg=C["fg"], insertbackground=C["fg"],
                       font=(FUI, 14), highlightthickness=0, bd=0)
        pe.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=12)
        pe.focus_set()
        tk.Label(sr, text="ESC to close", bg=C["surface"], fg=C["fg_dim"],
                 font=(FUI, 8), padx=12).pack(side=tk.RIGHT)
        tk.Frame(wrap, bg=C["border"], height=1).pack(fill=tk.X)
        # Group label
        self._cp_grp = tk.Label(wrap, text="  ALL COMMANDS", bg=C["surface"],
                                 fg=C["fg_dim"], font=(FUI, 7, "bold"),
                                 anchor=tk.W, padx=8, pady=4)
        self._cp_grp.pack(fill=tk.X)
        lb = tk.Listbox(wrap, bg=C["surface"], fg=C["fg"], font=(FUI, 11),
                         relief=tk.FLAT, highlightthickness=0, bd=0,
                         selectbackground=C["sel"], selectforeground=C["accent2"],
                         activestyle="none", height=16)
        lb.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        # Footer
        tk.Frame(wrap, bg=C["border"], height=1).pack(fill=tk.X)
        ft = tk.Frame(wrap, bg=C["surface2"])
        ft.pack(fill=tk.X, padx=14, pady=6)
        tk.Label(ft, text="↑↓ navigate   ↵ run   esc close",
                 bg=C["surface2"], fg=C["fg_dim"], font=(FUI, 8)).pack(side=tk.LEFT)

        CMDS = [
            ("  📁  Explorer  — browse files",         lambda: self._nav_to("explorer")),
            ("  🔍  Search  — search everything",       lambda: self._nav_to("search")),
            ("  ◎  Commits  — commit history",          lambda: (self._nav_to("commits"), self._load_commits())),
            ("  ⚡  Operations  — upload, download",    lambda: self._nav_to("operations")),
            ("  ℹ  About  — about GitView",             lambda: self._nav_to("about")),
            ("  ─────  Actions  ─────", None),
            ("  🌙  Toggle Theme  (Ctrl+T)",             self._toggle_theme),
            ("  🔄  Refresh Repositories  (F5)",         self._load_repos),
            ("  ◎  Load All Commits",                   self._load_all_repos_commits),
            ("  📥  Export Commits to CSV",              self._export_commits_csv),
            ("  ─────  File  ─────", None),
            ("  📦  Download Entire Repo",               self._dl_all),
            ("  📤  Upload File  (Ctrl+U)",              self._upload_file),
            ("  ✏  Create New File  (Ctrl+N)",          self._create_file),
            ("  📂  Create New Folder",                  self._create_folder),
            ("  ─────  Repo  ─────", None),
            ("  ➕  Create Repository",                   self._create_repo),
            ("  ⌂  Go to Root",                          self._go_home),
            ("  🌐  Open Repo in Browser",               self._open_browser),
            ("  📋  Copy Current Path",                   self._copy_path),
            ("  ─────  Help  ─────", None),
            ("  ❓  Help & Shortcuts  (F1)",              self._show_help),
        ]

        def _ref(q=""):
            lb.delete(0, tk.END)
            q = q.lower()
            count = 0
            for label, cmd in CMDS:
                if cmd is None:
                    if not q:
                        lb.insert(tk.END, label)
                        lb.itemconfig(tk.END, fg=C["fg_dim"])
                    continue
                if not q or q in label.lower():
                    lb.insert(tk.END, label)
                    count += 1
            if lb.size():
                # Select first non-separator
                for i in range(lb.size()):
                    if CMDS[i][1] is not None if i < len(CMDS) else True:
                        try: lb.selection_set(i); break
                        except: pass
            self._cp_grp.config(
                text=f"  {count} COMMANDS" if q else "  ALL COMMANDS")

        def _run():
            sel = lb.curselection()
            q   = pv.get().lower()
            matches = [(lbl, c) for lbl, c in CMDS if c is not None and
                       (not q or q in lbl.lower())]
            if sel:
                # Find which match corresponds to listbox selection
                lb_idx  = sel[0]
                visible = [i for i in range(lb.size())
                           if lb.get(i).strip().startswith("─") is False]
                active_matches = []
                for label, cmd in CMDS:
                    if cmd is None: continue
                    if not q or q in label.lower():
                        active_matches.append(cmd)
                # Map selected lb index to cmd
                non_sep = 0
                for i in range(lb.size()):
                    txt = lb.get(i)
                    # Skip separators
                    is_sep = "─────" in txt
                    if i == lb_idx and not is_sep:
                        if non_sep < len(active_matches):
                            win.destroy()
                            active_matches[non_sep]()
                        return
                    if not is_sep:
                        non_sep += 1

        def _nav_lb(delta):
            cur = lb.curselection()
            sz  = lb.size()
            if not sz: return
            idx = (cur[0] if cur else -1) + delta
            # Skip separators
            for _ in range(sz):
                idx = max(0, min(sz - 1, idx))
                if "─────" not in lb.get(idx):
                    break
                idx += delta
            lb.selection_clear(0, tk.END)
            lb.selection_set(idx)
            lb.see(idx)

        pv.trace_add("write", lambda *_: _ref(pv.get()))
        lb.bind("<Return>",   lambda _: _run())
        lb.bind("<Double-1>", lambda _: _run())
        pe.bind("<Return>",   lambda _: _run())
        pe.bind("<Down>",     lambda _: (lb.focus_set(), _nav_lb(1)))
        pe.bind("<Up>",       lambda _: (lb.focus_set(), _nav_lb(-1)))
        lb.bind("<Up>",       lambda _: _nav_lb(-1))
        lb.bind("<Down>",     lambda _: _nav_lb(1))
        lb.bind("<Escape>",   lambda _: win.destroy())
        win.bind("<Escape>",  lambda _: win.destroy())
        win.bind("<FocusOut>",lambda e: win.destroy() if e.widget == win else None)
        _ref()

    # ── Connection ───────────────────────────────────────────────────────
    def _connect_token(self):
        tok = self.tok_var.get().strip()
        if not tok:
            self._toast("Please enter a Personal Access Token", "warn")
            return
        self.token = tok
        self.sess.headers["Authorization"] = f"token {tok}"
        self._set_status("Connecting…")
        self._prog_start()
        self.conn_btn.config(state=tk.DISABLED, text=" Connecting… ")

        def _work():
            try:
                r = rget(self.sess, f"{self.API}/user", timeout=15)
                if r.status_code == 200:
                    self.root.after(0, lambda: self._on_connected(r.json(), "token"))
                elif r.status_code == 401:
                    self.root.after(0, lambda: (
                        self._toast("Token invalid or expired", "err"),
                        self._set_status("Auth failed", "err")))
                else:
                    self.root.after(0, lambda: self._toast(f"Error {r.status_code}", "err"))
            except Exception as e:
                self.root.after(0, lambda: self._toast(str(e), "err"))
            finally:
                self.root.after(0, self._prog_stop)
                self.root.after(0, lambda: self.conn_btn.config(state=tk.NORMAL, text="  Connect  "))

        threading.Thread(target=_work, daemon=True).start()

    def _connect_public(self):
        user = parse_gh_user(self.pub_var.get().strip())
        if not user:
            self._toast("Invalid username or URL", "warn")
            return
        self.token = None
        self.sess.headers.pop("Authorization", None)
        self._set_status(f"Connecting to @{user}…")
        self._prog_start()

        def _work():
            try:
                r = rget(self.sess, f"{self.API}/users/{user}", timeout=15)
                if r.status_code == 200:
                    self.username = r.json().get("login", "")
                    self.root.after(0, lambda: self._on_connected(r.json(), "public"))
                elif r.status_code == 404:
                    self.root.after(0, lambda: self._toast(f"User '{user}' not found", "err"))
                else:
                    self.root.after(0, lambda: self._toast(f"Error {r.status_code}", "err"))
            except Exception as e:
                self.root.after(0, lambda: self._toast(str(e), "err"))
            finally:
                self.root.after(0, self._prog_stop)

        threading.Thread(target=_work, daemon=True).start()

    def _on_connected(self, data: Dict, mode: str):
        C = self.C
        login = data.get("login", "")
        name  = data.get("name") or login
        repos = data.get("public_repos", 0)
        fol   = data.get("followers", 0)
        bio   = (data.get("bio") or "")[:60]
        self.username  = login
        self.auth_mode = mode

        self._uname.config(text=name, fg=C["fg_bright"])
        self._umeta.config(text=f"@{login}  ·  {repos:,} repos  ·  {fol:,} followers",
                            fg=C["fg_muted"])
        self._ubio.config(text=bio, fg=C["fg_dim"])
        self._ubadge.config(
            text="🔑 TOKEN" if mode == "token" else "👤 PUBLIC",
            fg=C["green"] if mode == "token" else C["amber"])
        self._avatar.config(text="●", fg=C["green"])
        self._conn_dot.config(fg=C["green"])
        self.discon_btn.pack(side=tk.LEFT, padx=(3, 0))
        self.conn_btn.config(text="  ✓ Connected  ")
        self._sb_user_lbl.config(text=f"  @{login}", fg=C["fg_muted"])
        self._sb_mode_lbl.config(
            text=f"  {'Token (5k/hr)' if mode=='token' else 'Public (60/hr)'}",
            fg=C["fg_dim"])
        self._update_banner(True)
        self._toast(f"Connected as @{login}", "ok")
        self._set_status(f"Connected as @{login}", "ok")
        self._log(f"Connected: @{login} [{mode}]")
        self._save_cfg()
        self._load_repos()

    def _disconnect(self):
        self.token = self.username = None
        self.sess.headers.pop("Authorization", None)
        self.current_repo = self.current_repo_full = None
        self.current_path = ""
        self.repo_data.clear()
        self.repo_cb["values"]  = []
        self.branch_cb["values"] = []
        self.tree.delete(*self.tree.get_children())
        self._index.clear()
        self.ctree.delete(*self.ctree.get_children())
        C = self.C
        self._uname.config(text="Not Connected",              fg=C["fg_muted"])
        self._umeta.config(text="Select Token or Public mode",fg=C["fg_dim"])
        self._ubio.config(text="")
        self._ubadge.config(text="")
        self._avatar.config(text="◯", fg=C["fg_dim"])
        self._conn_dot.config(fg=C["fg_dim"])
        self.discon_btn.pack_forget()
        self.conn_btn.config(text="  Connect  ")
        self._sb_user_lbl.config(text="Not connected", fg=C["fg_dim"])
        self._sb_mode_lbl.config(text="",              fg=C["fg_dim"])
        self._update_banner(False)
        self._update_idx_display()
        self._toast("Disconnected", "info")
        self._set_status("Disconnected")

    def _update_banner(self, connected: bool):
        try:
            C = self.C
            if connected:
                total = self._index.total()
                self._banner_lbl.config(
                    text=f"✅  @{self.username}  ·  {'🔑 Token' if self.auth_mode=='token' else '👤 Public'}"
                         f"  ·  {total:,} commits indexed  ·  Ctrl+K for palette",
                    bg=C["green_bg"], fg=C["green"])
                self._banner_f.config(bg=C["green_bg"], highlightbackground=C["green"])
            else:
                self._banner_lbl.config(
                    text="ℹ  Connect a GitHub account to search across all repositories.",
                    bg=C["amber_bg"], fg=C["amber"])
                self._banner_f.config(bg=C["amber_bg"], highlightbackground=C["amber"])
        except:
            pass

    # ── Repository Loading ───────────────────────────────────────────────
    def _load_repos(self):
        if not self.username:
            self._toast("Connect first", "warn")
            return
        self._set_status("Loading repositories…")
        self._prog_start()

        def _work():
            try:
                repos: List[Dict] = []
                page = 1
                while True:
                    url = (f"{self.API}/user/repos"
                           if self.auth_mode == "token"
                           else f"{self.API}/users/{self.username}/repos")
                    r = rget(self.sess, url,
                              params={"per_page": 100, "page": page,
                                      "sort": "updated", "type": "all"},
                              timeout=20)
                    if r.status_code != 200: break
                    batch = r.json()
                    if not batch: break
                    repos.extend(batch)
                    if len(batch) < 100: break
                    page += 1
                self.root.after(0, lambda: self._on_repos(repos))
            except Exception as e:
                self.root.after(0, lambda: self._toast(str(e), "err"))
                self.root.after(0, self._prog_stop)

        threading.Thread(target=_work, daemon=True).start()

    def _on_repos(self, repos: List[Dict]):
        self._prog_stop()
        self.repo_data.clear()
        for rd in repos:
            self.repo_data[rd.get("full_name", "")] = rd
        names = self._repo_names()
        self.repo_cb["values"] = names
        all_names = ["(All Repos)"] + [rd.get("name", "") for rd in repos]
        try:
            self._cr_cb["values"] = all_names
            self._cr_var.set("(All Repos)")
        except:
            pass
        if names:
            prev = self.current_repo_full
            self.repo_cb.set(prev if prev and prev in names else names[0])
            self._on_repo_sel()
        n = len(repos)
        self._set_status(f"Loaded {n} repositories", "ok")
        self._log(f"Loaded {n} repos for @{self.username}")
        self._show_inf("📦", f"{n} repositories loaded",
                        f"@{self.username}  ·  Select a repo to explore")
        self._toast(f"Loaded {n} repositories", "ok")

    def _repo_names(self) -> List[str]:
        pinned = [k for k in self.pinned if k in self.repo_data]
        return pinned + [k for k in self.repo_data if k not in pinned]

    def _on_repo_sel(self, _=None):
        key = self.repo_var.get()
        if not key or key not in self.repo_data: return
        rd = self.repo_data[key]
        self.current_repo      = rd.get("name", key.split("/")[-1])
        self.current_repo_full = key
        self.current_path      = ""
        # Track recent repos
        if key not in self.recent_repos:
            self.recent_repos.appendleft(key)
        self._update_repo_meta()
        self._load_branches()
        self._log(f"Selected: {key}")

    def _update_repo_meta(self):
        key = self.repo_var.get()
        if key not in self.repo_data: return
        rd   = self.repo_data[key]
        lang = rd.get("language") or "—"
        self._repo_meta.config(
            text=f"★{rd.get('stargazers_count',0):,}  🍴{rd.get('forks_count',0):,}"
                 f"  {lang}  ·  {rel_t(rd.get('updated_at',''))}")
        self._repo_desc.config(text=(rd.get("description") or "No description")[:120])

    def _load_branches(self):
        if not self.current_repo: return

        def _work():
            try:
                r = rget(self.sess,
                          f"{self.API}/repos/{self.username}/{self.current_repo}/branches",
                          params={"per_page": 100}, timeout=15)
                if r.status_code == 200:
                    branches = [b["name"] for b in r.json()]
                    self.root.after(0, lambda: self._on_branches(branches))
            except:
                pass

        threading.Thread(target=_work, daemon=True).start()

    def _on_branches(self, branches: List[str]):
        self.branch_cb["values"] = branches
        rd = self.repo_data.get(self.current_repo_full or "", {})
        default = rd.get("default_branch", "main")
        self.branch_var.set(
            default if default in branches else (branches[0] if branches else ""))
        self._load_dir("")

    def _on_branch_sel(self, _=None):
        self.current_path = ""
        self._load_dir("")

    def _pin_repo(self):
        key = self.repo_var.get()
        if not key: return
        if key in self.pinned:
            self.pinned.remove(key)
            self._toast(f"Unpinned: {key}", "info")
        else:
            self.pinned.append(key)
            self._toast(f"Pinned: {key}", "ok")
        self.repo_cb["values"] = self._repo_names()
        self._save_cfg()

    # ── Directory Loading ────────────────────────────────────────────────
    def _load_dir(self, path: str):
        if not self.current_repo: return
        self.current_path = path
        branch = self.branch_var.get()
        # Build clickable breadcrumb
        self._rebuild_breadcrumb(path)
        self._show_inf("⏳", "Loading…", "Fetching from GitHub API")
        self.tree.delete(*self.tree.get_children())
        self.filter_var.set("")
        self._clr_prev()

        def _work():
            try:
                url = (f"{self.API}/repos/{self.username}/{self.current_repo}"
                        f"/contents/{path}")
                r = rget(self.sess, url,
                          params={"ref": branch} if branch else {},
                          timeout=20)
                if r.status_code == 200:
                    items = r.json()
                    if not isinstance(items, list):
                        items = [items]
                    self.root.after(0, lambda: self._populate(items))
                elif r.status_code == 404:
                    self.root.after(0, lambda: self._show_inf(
                        "⚠", "Not Found", f"'{path}' not found on '{branch}'"))
                else:
                    m = r.json().get("message", "Error")
                    self.root.after(0, lambda: self._set_status(m, "err"))
            except Exception as e:
                self.root.after(0, lambda: self._set_status(str(e), "err"))

        threading.Thread(target=_work, daemon=True).start()

    def _rebuild_breadcrumb(self, path: str):
        """Rebuild clickable breadcrumb navigation"""
        try:
            # Clear existing breadcrumb labels (keep copy btn)
            for w in list(self._pb_inner.winfo_children()):
                if w is not self._pb_copy_btn:
                    w.destroy()
            C = self.C
            # Root segment
            root_lbl = tk.Label(self._pb_inner, text="/",
                                 bg=C["surface2"], fg=C["accent"],
                                 font=(FMONO, 8), cursor="hand2")
            root_lbl.pack(side=tk.LEFT, padx=2)
            root_lbl.bind("<Button-1>", lambda _: self._load_dir(""))
            root_lbl.bind("<Enter>", lambda _, w=root_lbl: w.config(fg=C["accent2"]))
            root_lbl.bind("<Leave>", lambda _, w=root_lbl: w.config(fg=C["accent"]))
            # Path segments
            if path:
                parts = path.split("/")
                for i, part in enumerate(parts):
                    tk.Label(self._pb_inner, text=" › ",
                              bg=C["surface2"], fg=C["fg_dim"],
                              font=(FUI, 8)).pack(side=tk.LEFT)
                    sub_path = "/".join(parts[:i+1])
                    is_last  = (i == len(parts) - 1)
                    seg = tk.Label(self._pb_inner, text=part,
                                    bg=C["surface2"],
                                    fg=C["fg_muted"] if is_last else C["accent"],
                                    font=(FMONO, 8),
                                    cursor="hand2" if not is_last else "")
                    seg.pack(side=tk.LEFT)
                    if not is_last:
                        def _go(p=sub_path): self._load_dir(p)
                        seg.bind("<Button-1>", lambda _, fn=_go: fn())
                        seg.bind("<Enter>", lambda _, w=seg: w.config(fg=C["accent2"]))
                        seg.bind("<Leave>", lambda _, w=seg: w.config(fg=C["accent"]))
        except Exception:
            # Fallback: simple text
            try: self._path_lbl.config(text="/" + path if path else "/")
            except: pass

    def _populate(self, items: List[Dict]):
        self.all_items = {"dirs": [], "files": []}
        for i in items:
            bucket = "dirs" if i.get("type") == "dir" else "files"
            self.all_items[bucket].append(i)
        self._render_tree(self.all_items["dirs"] + self.all_items["files"])
        d   = len(self.all_items["dirs"])
        fi  = len(self.all_items["files"])
        self._fc_lbl.config(text=f"{d} folders  ·  {fi} files")
        self._set_status(
            f"{d+fi} items  ·  {self.current_repo}/{self.current_path or ''}",
            "ok")
        self._inf.place_forget()

    def _render_tree(self, items: List[Dict]):
        self.tree.delete(*self.tree.get_children())
        C = self.C
        for item in items:
            is_d = item.get("type") == "dir"
            name = item.get("name", "")
            sz   = item.get("size", 0)
            self.tree.insert(
                "", "end",
                text=f"  {name}",
                values=(_fi(name), "Folder" if is_d else "File",
                        "—" if is_d else fmt_sz(sz)),
                tags=("d" if is_d else "f",))
        self.tree.tag_configure("d", foreground=C["tag_dir"])
        self.tree.tag_configure("f", foreground=C["tag_file"])

    def _show_inf(self, icon: str, main: str, sub: str):
        self.tree.delete(*self.tree.get_children())
        self._inf_icon.config(text=icon)
        self._inf_main.config(text=main)
        self._inf_sub.config(text=sub)
        self._inf.place(relx=0.5, rely=0.5, anchor="center")

    def _on_dbl(self, _=None):
        sel = self.tree.selection()
        if not sel: return
        iid  = sel[0]
        vals = self.tree.item(iid, "values")
        name = self.tree.item(iid, "text").strip()
        if vals and vals[1] == "Folder":
            self._load_dir(f"{self.current_path}/{name}" if self.current_path else name)
        else:
            self._open_preview(name)

    def _on_sel(self, _=None):
        sel = self.tree.selection()
        if not sel: return
        iid  = sel[0]
        vals = self.tree.item(iid, "values")
        name = self.tree.item(iid, "text").strip()
        if vals and vals[1] == "File":
            self._quick_prev(name)

    def _go_home(self):
        if self.current_repo:
            self._load_dir("")

    def _go_up(self):
        if not self.current_path: return
        self._load_dir("/".join(self.current_path.rsplit("/", 1)[:-1]))

    def _refresh_dir(self):
        self._load_dir(self.current_path)

    def _copy_path(self):
        path = ("/" + self.current_path) if self.current_path else "/"
        self.root.clipboard_clear()
        self.root.clipboard_append(path)
        self._toast(f"Copied: {path}", "ok")

    def _apply_filter(self):
        q = self.filter_var.get().lower()
        if not q:
            self._render_tree(self.all_items["dirs"] + self.all_items["files"])
            self._fc_lbl.config(text="")
            return
        filtered = [i for i in self.all_items["dirs"] + self.all_items["files"]
                    if q in i["name"].lower()]
        self._render_tree(filtered)
        n = len(filtered)
        self._fc_lbl.config(text=f"Filter: {n} match{'es' if n != 1 else ''}")

    def _sort_col(self, col: str):
        self.sort_rev = (not self.sort_rev) if self.sort_col == col else False
        self.sort_col = col
        kf = {
            "name": lambda i: i.get("name", "").lower(),
            "kind": lambda i: i.get("type", ""),
            "size": lambda i: i.get("size", 0),
        }.get(col, lambda i: "")
        dirs  = sorted(self.all_items["dirs"],  key=kf, reverse=self.sort_rev)
        files = sorted(self.all_items["files"], key=kf, reverse=self.sort_rev)
        self._render_tree(dirs + files)

    # ── Preview ──────────────────────────────────────────────────────────
    def _clr_prev(self):
        self.prev_txt.config(state=tk.NORMAL)
        self.prev_txt.delete("1.0", tk.END)
        self.prev_txt.config(state=tk.DISABLED)
        self._prev_info.config(text="")

    def _set_prev(self, text: str, lang: str = "text", size_bytes: int = 0):
        self.prev_txt.config(state=tk.NORMAL)
        self.prev_txt.delete("1.0", tk.END)
        preview = text[:80000]
        self.prev_txt.insert("1.0", preview)
        if lang != "text":
            SH.apply(self.prev_txt, lang, self.C)
        self.prev_txt.config(state=tk.DISABLED)
        lines = preview.count("\n") + 1
        info = f"{lines:,} lines"
        if size_bytes:
            info += f"  ·  {fmt_sz(size_bytes)}"
        if lang and lang != "text":
            info += f"  ·  {lang}"
        self._prev_info.config(text=info)

    def _quick_prev(self, name: str):
        if not self.current_repo: return
        if _is_binary(name):
            self._set_prev(f"[Binary file: {name}]\n\nDouble-click to download.")
            return
        path   = f"{self.current_path}/{name}" if self.current_path else name
        branch = self.branch_var.get()
        self._set_prev(f"Loading {name}…")

        def _work():
            try:
                r = rget(self.sess,
                          f"{self.API}/repos/{self.username}/{self.current_repo}"
                          f"/contents/{path}",
                          params={"ref": branch} if branch else {},
                          timeout=15)
                if r.status_code == 200:
                    jd = r.json()
                    size = jd.get("size", 0)
                    try:
                        text = base64.b64decode(
                            jd.get("content", "")).decode("utf-8", errors="replace")
                    except:
                        text = "[Binary file]"
                    self.root.after(0, lambda: self._set_prev(text, _lang(name), size))
            except Exception as e:
                self.root.after(0, lambda: self._set_prev(f"Error: {e}"))

        threading.Thread(target=_work, daemon=True).start()

    def _expand_preview(self):
        sel = self.tree.selection()
        if not sel: return
        iid  = sel[0]
        vals = self.tree.item(iid, "values")
        name = self.tree.item(iid, "text").strip()
        if vals and vals[1] == "File":
            self._open_preview(name)

    def _open_preview(self, name: str):
        if not self.current_repo: return
        path   = f"{self.current_path}/{name}" if self.current_path else name
        branch = self.branch_var.get()
        self._set_status(f"Opening {name}…")

        def _work():
            try:
                r = rget(self.sess,
                          f"{self.API}/repos/{self.username}/{self.current_repo}"
                          f"/contents/{path}",
                          params={"ref": branch} if branch else {},
                          timeout=15)
                if r.status_code == 200:
                    jd = r.json()
                    try:
                        text = base64.b64decode(
                            jd.get("content", "")).decode("utf-8", errors="replace")
                    except:
                        text = "[Binary]"
                    self.root.after(0, lambda: self._open_win(
                        name, text, fmt_sz(jd.get("size", 0)), _lang(name)))
            except Exception as e:
                self.root.after(0, lambda: self._toast(str(e), "err"))

        threading.Thread(target=_work, daemon=True).start()

    def _open_win(self, name: str, text: str, size: str, lang: str):
        C = self.C
        win = tk.Toplevel(self.root)
        win.title(f"{name}  —  GitView")
        win.geometry("1100x780")
        win.configure(bg=C["bg"])
        self._preview_wins.append(win)
        win.protocol("WM_DELETE_WINDOW",
                      lambda: (self._preview_wins.remove(win)
                               if win in self._preview_wins else None,
                               win.destroy()))

        tk.Frame(win, bg=C["accent"], height=2).pack(fill=tk.X)
        hdr = tk.Frame(win, bg=C["surface"], height=44)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        hi = tk.Frame(hdr, bg=C["surface"])
        hi.pack(fill=tk.BOTH, expand=True, padx=14)
        tk.Label(hi, text=f"{_fi(name)}  {name}", bg=C["surface"],
                 fg=C["fg_bright"], font=(FBOLD, 11, "bold")).pack(side=tk.LEFT, pady=10)
        lines = text.count("\n") + 1
        tk.Label(hi, text=f"  ·  {size}  ·  {lang or 'text'}  ·  {lines:,} lines  ·  {self.current_repo}",
                 bg=C["surface"], fg=C["fg_muted"], font=(FUI, 9)).pack(side=tk.LEFT)

        for t, cmd, st in [
            ("✕",         win.destroy, "ghost"),
            ("📥 Download",lambda: self._dl_one(name), "accent"),
            ("📋 Copy",    lambda: (win.clipboard_clear(),
                                    win.clipboard_append(text),
                                    self._toast("Copied", "ok")), "ghost2"),
            ("🔍 Find",    lambda: self._find_in_text(tw), "ghost2"),
        ]:
            _btn(hi, t, cmd, style=st, C=C, font=(FUI, 9), py=4).pack(
                side=tk.RIGHT, padx=3, pady=8)

        cf = tk.Frame(win, bg=C["surface"])
        cf.pack(fill=tk.BOTH, expand=True)
        ln = tk.Text(cf, width=6, wrap=tk.NONE, bg=C["surface2"], fg=C["fg_dim"],
                      font=(FMONO, 10), relief=tk.FLAT, highlightthickness=0,
                      state=tk.NORMAL, selectbackground=C["surface2"])
        ln.insert("1.0", "\n".join(str(i) for i in range(1, lines + 1)))
        ln.config(state=tk.DISABLED)
        ln.pack(side=tk.LEFT, fill=tk.Y)

        tw = tk.Text(cf, wrap=tk.NONE, bg=C["surface"], fg=C["fg"],
                      font=(FMONO, 10), relief=tk.FLAT, highlightthickness=0,
                      insertbackground=C["fg"], selectbackground=C["sel"],
                      padx=12, pady=8)
        vs = _vsb(cf, None)
        hs = _hsb(win, tw.xview)

        def sync(*a):
            tw.yview(*a)
            ln.yview(*a)

        vs.config(command=sync)
        tw.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        ln.configure(yscrollcommand=vs.set)
        hs.pack(side=tk.BOTTOM, fill=tk.X)
        vs.pack(side=tk.RIGHT, fill=tk.Y)
        tw.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tw.insert("1.0", text)
        tw.config(state=tk.DISABLED)
        SH.apply(tw, lang, C)

    def _find_in_preview(self, _=None):
        self._find_in_text(self.prev_txt)

    def _find_in_text(self, widget: tk.Text):
        """Open find dialog for a Text widget"""
        C = self.C
        win = tk.Toplevel(self.root)
        win.title("Find")
        win.geometry("360x60")
        win.configure(bg=C["surface"])
        win.wm_attributes("-topmost", True)
        fv = tk.StringVar()
        row = tk.Frame(win, bg=C["surface"])
        row.pack(fill=tk.X, padx=10, pady=8)
        tk.Label(row, text="🔍", bg=C["surface"], fg=C["accent"],
                 font=(FUI, 12)).pack(side=tk.LEFT, padx=(0, 6))
        fe = _entry(row, fv, C, 28)
        fe.pack(side=tk.LEFT, ipady=4)
        fe.focus_set()

        def _find(fwd=True):
            q = fv.get()
            if not q: return
            widget.tag_remove("find_hl", "1.0", tk.END)
            idx = "1.0"
            first = None
            while True:
                pos = widget.search(q, idx, nocase=True, stopindex=tk.END)
                if not pos: break
                end = f"{pos}+{len(q)}c"
                widget.tag_add("find_hl", pos, end)
                if first is None:
                    first = pos
                    widget.see(pos)
                idx = end
            widget.tag_configure("find_hl", background=C["amber_bg"], foreground=C["amber"])

        fe.bind("<Return>",  lambda _: _find())
        fe.bind("<Escape>",  lambda _: (widget.tag_remove("find_hl", "1.0", tk.END), win.destroy()))
        win.bind("<Escape>", lambda _: (widget.tag_remove("find_hl", "1.0", tk.END), win.destroy()))
        _btn(row, "Find", _find, style="accent", C=C, font=(FUI, 9), px=10, py=4).pack(side=tk.LEFT, padx=(4, 0))

    # ── Search ───────────────────────────────────────────────────────────
    def _debounce(self, *_):
        if self._debounce_id:
            try: self.root.after_cancel(self._debounce_id)
            except: pass
        q = self.sq_var.get().strip()
        if len(q) >= 3:
            self._debounce_id = self.root.after(700, self._do_search)

    def _do_search(self, _=None):
        if not self.username:
            self._toast("Connect first", "warn")
            return
        q = self.sq_var.get().strip()
        if len(q) < 2:
            self._toast("Enter at least 2 characters", "warn")
            return
        if q in self.search_history:
            self.search_history.remove(q)
        self.search_history.appendleft(q)
        scope = self._scope_var.get()
        self._result_page = 1
        self._results = []
        for w in self._rin.winfo_children():
            w.destroy()
        tk.Label(self._rin, text="🔄  Searching…", bg=self.C["bg"],
                 fg=self.C["fg_muted"], font=(FUI, 11)).pack(pady=40)
        self._rcount.config(text="Searching…")
        self._sprog_lbl.config(text=f"● {scope}…")
        self._stop_btn.config(state=tk.NORMAL)
        self._go_btn.config(state=tk.DISABLED)
        self.search_cancel.clear()

        def _work():
            try:
                dispatch = {
                    "Repos":   self._srch_repos,
                    "Content": self._srch_content,
                    "Files":   self._srch_files,
                    "Commits": self._srch_commits,
                    "Topics":  self._srch_topics,
                    "Index":   self._srch_index,
                }
                results = dispatch.get(scope, self._srch_repos)(q)
                if not self.search_cancel.is_set():
                    self.root.after(0, lambda: self._show_results(results, scope, q))
            except Exception as e:
                if not self.search_cancel.is_set():
                    self.root.after(0, lambda: self._toast(str(e), "err"))
            finally:
                self.root.after(0, lambda: self._stop_btn.config(state=tk.DISABLED))
                self.root.after(0, lambda: self._go_btn.config(state=tk.NORMAL))
                self.root.after(0, lambda: self._sprog_lbl.config(text=""))

        threading.Thread(target=_work, daemon=True).start()

    def _sel_scope(self, scope: str):
        self._scope_var.set(scope)
        C = self.C
        for s, b in self._scope_btns.items():
            on = (s == scope)
            b.config(
                bg=C["accent_bg"]  if on else C["surface2"],
                fg=C["accent2"]    if on else C["fg_muted"],
                activebackground=C["accent_dim"] if on else C["surface3"])

    def _cancel_search(self):
        self.search_cancel.set()
        self._stop_btn.config(state=tk.DISABLED)
        self._go_btn.config(state=tk.NORMAL)
        self._sprog_lbl.config(text="")
        self._toast("Search cancelled", "info")

    def _srch_repos(self, q: str) -> List[Dict]:
        lq = q.lower()
        lf = self._lang_var.get().strip().lower()
        res = []
        for key, rd in self.repo_data.items():
            lang = (rd.get("language") or "").lower()
            if lf and lf not in lang: continue
            sc = SE.repo_score(lq, rd)
            if sc > 0:
                res.append({"type": "repo", "key": key, "data": rd, "_score": sc})
        res.sort(key=lambda x: x["_score"], reverse=True)
        return res

    def _srch_topics(self, q: str) -> List[Dict]:
        ql = q.lower()
        res = []
        for key, rd in self.repo_data.items():
            topics = [t.lower() for t in rd.get("topics", [])]
            lang   = (rd.get("language") or "").lower()
            sc = 0
            if ql in topics:                   sc += 100
            elif any(ql in t for t in topics): sc += 60
            if ql == lang:   sc += 80
            elif ql in lang: sc += 40
            if sc > 0:
                res.append({"type": "repo", "key": key, "data": rd, "_score": sc})
        res.sort(key=lambda x: x["_score"], reverse=True)
        return res

    def _srch_index(self, q: str) -> List[Dict]:
        total = self._index.total()
        if total == 0:
            return [{"type": "error", "key": "x", "data": {
                "message": "No commits indexed yet.\n"
                           "→ Go to Commits tab → click 'Load ALL Repos'"
                           " to index everything."}}]
        repo_f = self._cr_var.get() if hasattr(self, "_cr_var") else None
        pool   = self._index.search(
            q, repo=repo_f if repo_f and repo_f != "(All Repos)" else None)
        return [{"type": "commit", "key": c.get("sha", ""), "data": c,
                 "_score": SE.commit_score(q, c)} for c in pool]

    def _srch_content(self, q: str) -> List[Dict]:
        res = []
        lf  = self._lang_var.get().strip()
        ef  = self._ext_var.get().strip()
        query = f"{q} user:{self.username}"
        if lf: query += f" language:{lf}"
        if ef: query += f" extension:{ef.lstrip('.')}"
        hdrs = {"Accept": "application/vnd.github.text-match+json"}
        if self.token: hdrs["Authorization"] = f"token {self.token}"
        page = 1
        while page <= 4 and not self.search_cancel.is_set():
            try:
                r = rget(self.sess, f"{self.API}/search/code",
                          params={"q": query, "per_page": 30, "page": page},
                          hdrs=hdrs, timeout=25)
                if r.status_code == 200:
                    batch = r.json().get("items", [])
                    for item in batch:
                        res.append({"type": "content", "key": str(id(item)),
                                    "data": item, "_score": 100})
                    if len(batch) < 30: break
                    page += 1
                    time.sleep(0.4)
                elif r.status_code == 403:
                    res.append({"type": "error", "key": "e", "data": {
                        "message": "Content search requires Token authentication."}})
                    break
                elif r.status_code == 422:
                    res.append({"type": "error", "key": "e", "data": {
                        "message": "Query too short. Use 3+ characters."}})
                    break
                else:
                    break
            except Exception as e:
                res.append({"type": "error", "key": "e", "data": {"message": str(e)}})
                break
        return res

    def _srch_files(self, q: str) -> List[Dict]:
        res = []
        lf  = self._lang_var.get().strip()
        ef  = self._ext_var.get().strip()
        query = f"filename:{q} user:{self.username}"
        if lf: query += f" language:{lf}"
        if ef: query += f" extension:{ef.lstrip('.')}"
        hdrs = {"Accept": "application/vnd.github.text-match+json"}
        if self.token: hdrs["Authorization"] = f"token {self.token}"
        try:
            r = rget(self.sess, f"{self.API}/search/code",
                      params={"q": query, "per_page": 100},
                      hdrs=hdrs, timeout=25)
            if r.status_code == 200:
                for item in r.json().get("items", []):
                    sc = SE.score(q.lower(), item.get("name", ""))
                    res.append({"type": "file", "key": str(id(item)),
                                "data": item, "_score": sc})
                res.sort(key=lambda x: x["_score"], reverse=True)
            elif r.status_code == 403:
                res.append({"type": "error", "key": "e", "data": {
                    "message": "File search requires Token authentication."}})
            elif r.status_code == 422:
                res.append({"type": "error", "key": "e", "data": {
                    "message": "Filename too short."}})
        except Exception as e:
            res.append({"type": "error", "key": "e", "data": {"message": str(e)}})
        return res

    def _srch_commits(self, q: str) -> List[Dict]:
        res = []
        hdrs = {"Accept": "application/vnd.github.cloak-preview+json"}
        if self.token: hdrs["Authorization"] = f"token {self.token}"
        try:
            r = rget(self.sess, f"{self.API}/search/commits",
                      params={"q": f"{q} author:{self.username}", "per_page": 100},
                      hdrs=hdrs, timeout=25)
            if r.status_code == 200:
                for item in r.json().get("items", []):
                    res.append({"type": "commit", "key": str(id(item)),
                                "data": item, "_score": SE.commit_score(q, item)})
                res.sort(key=lambda x: x["_score"], reverse=True)
            else:
                local = self._srch_index(q)
                if local: res = local
        except Exception as e:
            res.append({"type": "error", "key": "e", "data": {"message": str(e)}})
        return res

    def _show_results(self, results: List[Dict], scope: str, q: str):
        self._results = results
        self._result_page = 1
        errs = [r for r in results if r.get("type") == "error"]
        good = [r for r in results if r.get("type") != "error"]
        n = len(good)
        self._rcount.config(text=f"{n} result{'s' if n!=1 else ''}")
        self._set_status(f"{n} results for '{q}' [{scope}]",
                          "ok" if n > 0 else "warn")
        self._log(f"Search [{scope}] '{q}' → {n} results")
        if errs:
            self._show_err_card(errs[0]["data"].get("message", "Error"))
            return
        self._re_sort()
        self._render_page()

    def _re_sort(self):
        if not self._results: return
        pref = self._sort_var.get()
        if pref == "name":
            self._results.sort(key=lambda r: (
                r.get("data", {}).get("name", "") or
                (r.get("data", {}).get("commit", {}).get("message", "")[:30])
            ).lower())
        elif pref == "date":
            def _dk(r):
                d = r.get("data", {})
                if r["type"] == "repo":   return d.get("updated_at", "")
                if r["type"] == "commit": return (d.get("commit", {}).get("author") or {}).get("date", "")
                return ""
            self._results.sort(key=_dk, reverse=True)
        elif pref == "activity":
            def _ak(r):
                d = r.get("data", {})
                if r["type"] == "repo":
                    return d.get("stargazers_count", 0) + int(recency(d.get("pushed_at", "")) * 200)
                return r.get("_score", 0)
            self._results.sort(key=_ak, reverse=True)

    def _pg(self, delta: int):
        good  = [r for r in self._results if r.get("type") != "error"]
        total = len(good)
        maxp  = max(1, (total + RPP - 1) // RPP)
        new   = max(1, min(maxp, self._result_page + delta))
        if new != self._result_page:
            self._result_page = new
            self._render_page()

    def _render_page(self):
        C    = self.C
        q    = self.sq_var.get().strip()
        good = [r for r in self._results if r.get("type") != "error"]
        total = len(good)
        maxp  = max(1, (total + RPP - 1) // RPP)
        page  = min(self._result_page, maxp)
        self._result_page = page
        start = (page - 1) * RPP
        items = good[start:start + RPP]
        self._pg_lbl.config(text=f"Page {page} / {maxp}")
        self._pg_prev.config(state=tk.NORMAL if page > 1    else tk.DISABLED)
        self._pg_next.config(state=tk.NORMAL if page < maxp else tk.DISABLED)
        for w in self._rin.winfo_children():
            w.destroy()
        if not items:
            fx = tk.Frame(self._rin, bg=C["bg"])
            fx.pack(pady=50)
            tk.Label(fx, text="🔎  No results", bg=C["bg"], fg=C["fg_muted"],
                     font=(FBOLD, 13, "bold")).pack()
            tk.Label(fx, text="Try a different keyword or scope", bg=C["bg"],
                     fg=C["fg_dim"], font=(FUI, 9)).pack(pady=(4, 0))
            return
        for ent in items:
            self._render_card(ent, q)
        self._rcv.yview_moveto(0)

    def _render_card(self, ent: Dict, q: str):
        C     = self.C
        etype = ent.get("type", "")
        data  = ent.get("data", {})
        BADGE = {
            "repo":    ("📦", "REPO",   C["accent_bg"],  C["accent2"]),
            "content": ("📄", "FILE",   C["purple_bg"],  C["purple"]),
            "file":    ("🗂", "FILE",   C["purple_bg"],  C["purple"]),
            "commit":  ("◎", "COMMIT", C["cyan_bg"],    C["cyan"]),
        }
        ico, badge, bbg, bfg = BADGE.get(etype, ("📄", etype.upper(), C["surface2"], C["fg_muted"]))
        if etype in ("content", "file"):
            ico = _fi(data.get("name", ""))

        card = tk.Frame(self._rin, bg=C["card"],
                         highlightbackground=C["border"], highlightthickness=1,
                         cursor="hand2")
        card.pack(fill=tk.X, padx=8, pady=3)
        row = tk.Frame(card, bg=C["card"])
        row.pack(fill=tk.X, padx=12, pady=10)

        il = tk.Frame(row, bg=C["card"])
        il.pack(side=tk.LEFT, padx=(0, 12))
        tk.Label(il, text=ico, bg=C["card"], fg=C["fg"], font=(FUI, 20)).pack()
        tk.Label(il, text=badge, bg=bbg, fg=bfg,
                 font=(FUI, 6, "bold"), padx=4, pady=1).pack()

        body = tk.Frame(row, bg=C["card"])
        body.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        hr = tk.Frame(body, bg=C["card"])
        hr.pack(fill=tk.X)

        if etype == "repo":
            rd    = data
            name  = rd.get("name", "")
            stars = rd.get("stargazers_count", 0)
            lang  = rd.get("language") or ""
            desc  = (rd.get("description") or "No description")[:130]
            topics = rd.get("topics", [])[:6]
            tk.Label(hr, text=name, bg=C["card"], fg=C["accent2"],
                     font=(FBOLD, 11, "bold"), cursor="hand2").pack(side=tk.LEFT)
            if rd.get("private"):
                tk.Label(hr, text=" 🔒", bg=C["card"], fg=C["fg_dim"], font=(FUI, 9)).pack(side=tk.LEFT)
            meta = f"  ★{stars:,}"
            if lang: meta += f"  ·  {lang}"
            meta += f"  ·  {rel_t(rd.get('updated_at', ''))}"
            sc_txt = f"  ·  score:{ent.get('_score', 0)}"
            tk.Label(hr, text=meta, bg=C["card"], fg=C["fg_muted"], font=(FUI, 8)).pack(side=tk.LEFT, padx=6)
            tk.Label(hr, text=sc_txt, bg=C["card"], fg=C["fg_dim"], font=(FUI, 7)).pack(side=tk.LEFT)
            tk.Label(body, text=desc, bg=C["card"], fg=C["fg_muted"],
                     font=(FUI, 9), anchor=tk.W).pack(fill=tk.X, pady=(2, 0))
            if topics:
                tr = tk.Frame(body, bg=C["card"])
                tr.pack(fill=tk.X, pady=(5, 0))
                for t in topics:
                    tk.Label(tr, text=t, bg=C["accent_bg"], fg=C["accent2"],
                             font=(FUI, 7), padx=5, pady=1).pack(side=tk.LEFT, padx=(0, 3))

        elif etype in ("content", "file"):
            name = data.get("name", "")
            path = data.get("path", "")
            repo = data.get("repository", {}).get("full_name", "")
            tk.Label(hr, text=name, bg=C["card"], fg=C["accent2"],
                     font=(FBOLD, 11, "bold")).pack(side=tk.LEFT)
            tk.Label(hr, text=f"  ·  {repo}", bg=C["card"], fg=C["fg_dim"],
                     font=(FUI, 8)).pack(side=tk.LEFT)
            if path != name:
                tk.Label(body, text=f"📂  {path}", bg=C["card"], fg=C["fg_dim"],
                         font=(FMONO, 8)).pack(anchor=tk.W, pady=(2, 0))
            frags = data.get("text_matches", [])
            if frags:
                ff = tk.Frame(body, bg=C["surface2"],
                               highlightbackground=C["border"], highlightthickness=1)
                ff.pack(fill=tk.X, pady=(6, 0))
                for frag in frags[:2]:
                    ft = frag.get("fragment", "").strip()
                    if ft:
                        self._render_frag(ff, ft, q)

        elif etype == "commit":
            commit = data.get("commit", {})
            msg    = (commit.get("message", "") or "").split("\n")[0][:100]
            sha    = data.get("sha", "")[:10]
            repo   = (data.get("repository", {}).get("full_name", "")
                      or data.get("_repo", ""))
            author = (commit.get("author") or {}).get("name", "")
            d      = rel_t((commit.get("author") or {}).get("date", ""))
            tk.Label(hr, text=msg, bg=C["card"], fg=C["fg_bright"],
                     font=(FUI, 10, "bold"), wraplength=500,
                     justify=tk.LEFT).pack(side=tk.LEFT, anchor=tk.W)
            meta2 = f"  {sha}"
            if author: meta2 += f"  ·  {author}"
            meta2 += f"  ·  {d}"
            if repo:   meta2 += f"  ·  {repo}"
            tk.Label(body, text=meta2, bg=C["card"], fg=C["fg_muted"],
                     font=(FMONO, 8)).pack(anchor=tk.W, pady=(2, 0))

        def _click(e=None, ent=ent): self._on_card_click(ent)
        def _enter(_): card.config(bg=C["card2"], highlightbackground=C["border_hi"])
        def _leave(_): card.config(bg=C["card"],  highlightbackground=C["border"])
        for w in (card, row, body, hr, il):
            w.bind("<Button-1>", _click)
            w.bind("<Enter>",    _enter)
            w.bind("<Leave>",    _leave)

    def _render_frag(self, parent: tk.Frame, frag: str, q: str):
        C = self.C
        ft = tk.Text(parent, wrap=tk.WORD, bg=C["surface2"], fg=C["fg_muted"],
                      font=(FMONO, 8), relief=tk.FLAT, highlightthickness=0,
                      height=3, padx=8, pady=4)
        ft.pack(fill=tk.X)
        ft.insert("1.0", frag)
        ft.tag_configure("hl", background=C["green_bg"], foreground=C["green"],
                          font=(FMONO, 8, "bold"))
        ql = q.lower()
        cl = frag.lower()
        s  = 0
        while True:
            i = cl.find(ql, s)
            if i == -1: break
            ft.tag_add("hl", f"1.0+{i}c", f"1.0+{i+len(ql)}c")
            s = i + 1
        ft.config(state=tk.DISABLED)

    def _show_search_empty(self):
        C = self.C
        for w in self._rin.winfo_children():
            w.destroy()
        f = tk.Frame(self._rin, bg=C["bg"])
        f.pack(pady=70)
        tk.Label(f, text="🔍", bg=C["bg"], fg=C["fg_dim"], font=(FUI, 40)).pack()
        tk.Label(f, text="Search GitHub", bg=C["bg"], fg=C["fg_muted"],
                 font=(FBOLD, 14, "bold")).pack(pady=(10, 0))
        tk.Label(f, text="Repos  ·  Content  ·  Files  ·  Commits  ·  Topics  ·  Index",
                 bg=C["bg"], fg=C["fg_dim"], font=(FUI, 9), justify=tk.CENTER).pack(pady=(6, 0))

    def _show_err_card(self, msg: str):
        C = self.C
        for w in self._rin.winfo_children():
            w.destroy()
        f = tk.Frame(self._rin, bg=C["red_bg"],
                      highlightbackground=C["red"], highlightthickness=1)
        f.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(f, text="⚠  Note", bg=C["red_bg"], fg=C["red"],
                 font=(FUI, 10, "bold"), padx=12, pady=8).pack(anchor=tk.W)
        tk.Label(f, text=msg, bg=C["red_bg"], fg=C["fg"],
                 font=(FUI, 9), padx=12, pady=6,
                 justify=tk.LEFT, wraplength=600).pack(anchor=tk.W, pady=(0, 4))
        self._rcount.config(text="")

    def _on_card_click(self, ent: Dict):
        C     = self.C
        etype = ent.get("type", "")
        data  = ent.get("data", {})
        t     = self._det
        t.config(state=tk.NORMAL)
        t.delete("1.0", tk.END)
        for tag, kw in [
            ("h",   {"font": (FBOLD, 11, "bold"),  "foreground": C["accent2"]}),
            ("k",   {"font": (FUI,   8,  "bold"),  "foreground": C["fg_dim"]}),
            ("v",   {"font": (FUI,   9),            "foreground": C["fg_muted"]}),
            ("m",   {"font": (FMONO, 9),            "foreground": C["fg"]}),
            ("sha", {"font": (FMONO, 10, "bold"),  "foreground": C["purple"]}),
        ]:
            t.tag_configure(tag, **kw)

        def ins(txt: str, tg: str = "v"):
            t.insert(tk.END, txt, tg)

        url = ""
        if etype == "repo":
            url = data.get("html_url", "")
            ins(data.get("full_name", ""), "h"); ins("\n")
            for k, v in [
                ("Language",  data.get("language") or "—"),
                ("Stars",     f"{data.get('stargazers_count', 0):,}"),
                ("Forks",     f"{data.get('forks_count', 0):,}"),
                ("Watchers",  f"{data.get('watchers_count', 0):,}"),
                ("Updated",   rel_t(data.get("updated_at", ""))),
                ("Pushed",    rel_t(data.get("pushed_at", ""))),
                ("Branch",    data.get("default_branch", "—")),
                ("License",   (data.get("license") or {}).get("name", "—")),
                ("Private",   str(data.get("private", False))),
                ("Fork",      str(data.get("fork", False))),
                ("Size",      fmt_sz(data.get("size", 0) * 1024)),
            ]:
                ins(f"\n{k:12}", "k"); ins(str(v))
            desc = data.get("description") or ""
            if desc: ins("\n\nDescription\n", "k"); ins(desc)
            topics = data.get("topics", [])
            if topics: ins("\n\nTopics  ", "k"); ins("  ".join(topics), "m")
            self._det_open.config(command=lambda u=url: webbrowser.open(u))
            self._det_nav.config(command=lambda k=data.get("full_name", ""),
                                           n=data.get("name", ""): self._nav_to_repo(k, n))

        elif etype in ("content", "file"):
            url  = data.get("html_url", "")
            ins(data.get("name", ""), "h"); ins("\n")
            ins("\nPath      ", "k"); ins(data.get("path", ""))
            ins("\nRepo      ", "k"); ins(data.get("repository", {}).get("full_name", ""))
            ins("\nURL       ", "k"); ins(url, "m")
            self._det_open.config(command=lambda u=url: webbrowser.open(u))
            self._det_nav.config(command=lambda: None)

        elif etype == "commit":
            sha    = data.get("sha", "")
            commit = data.get("commit", {})
            repo   = (data.get("repository", {}).get("full_name", "")
                      or data.get("_repo", ""))
            url    = (data.get("html_url", "")
                      or f"https://github.com/{repo}/commit/{sha}")
            ins(sha[:12], "sha"); ins("\n")
            ins("\nMessage   ", "k"); ins((commit.get("message", "")[:300]), "m")
            auth = commit.get("author") or {}
            ins("\n\nAuthor    ", "k"); ins(auth.get("name", ""))
            ins("\nEmail     ", "k"); ins(auth.get("email", ""))
            ins("\nDate      ", "k"); ins(
                f"{rel_t(auth.get('date', ''))}  ({fmt_dt(auth.get('date', ''))})")
            if repo:   ins("\nRepo      ", "k"); ins(repo)
            branch = data.get("_branch", "")
            if branch: ins("\nBranch    ", "k"); ins(branch)
            self._det_open.config(command=lambda u=url: webbrowser.open(u))
            self._det_nav.config(command=lambda d=data: self._show_from_search(d))

        t.config(state=tk.DISABLED)

    def _nav_to_repo(self, full_name: str, repo_name: str):
        if full_name in self.repo_data:
            self.repo_var.set(full_name)
            self.current_repo      = repo_name
            self.current_repo_full = full_name
            self._nav_to("explorer")
            self._on_repo_sel()

    def _show_hist(self, _=None):
        if not self.search_history: return
        C   = self.C
        pop = tk.Toplevel(self.root)
        pop.wm_overrideredirect(True)
        pop.wm_attributes("-topmost", True)
        x = self.sq_entry.winfo_rootx()
        y = self.sq_entry.winfo_rooty() + self.sq_entry.winfo_height() + 2
        pop.wm_geometry(f"+{x}+{y}")
        outer = tk.Frame(pop, bg=C["border_hi"], padx=1, pady=1)
        outer.pack()
        inner = tk.Frame(outer, bg=C["surface2"])
        inner.pack()
        for q in list(self.search_history)[:20]:
            lbl = tk.Label(inner, text=f"  🕐  {q}", bg=C["surface2"], fg=C["fg"],
                            font=(FUI, 9), anchor=tk.W, padx=10, pady=6,
                            cursor="hand2", width=50)
            lbl.pack(fill=tk.X)
            def _pick(qq=q, p=pop):
                self.sq_var.set(qq)
                p.destroy()
                self._do_search()
            lbl.bind("<Button-1>", lambda _, fn=_pick: fn())
            lbl.bind("<Enter>",    lambda e, w=lbl: w.config(bg=C["sel"]))
            lbl.bind("<Leave>",    lambda e, w=lbl: w.config(bg=C["surface2"]))
        pop.bind("<Escape>",   lambda _: pop.destroy())
        pop.focus_set()
        pop.bind("<FocusOut>", lambda e: pop.destroy())

    def _save_search(self):
        q = self.sq_var.get().strip()
        if q and q not in self.saved_searches:
            self.saved_searches.append(q)
            self._save_cfg()
            self._toast(f"Saved: {q}", "ok")

    def _show_saved(self):
        if not self.saved_searches:
            self._toast("No saved searches yet", "info")
            return
        C = self.C
        win = tk.Toplevel(self.root)
        win.title("Saved Searches")
        win.geometry("360x400")
        win.configure(bg=C["bg"])
        tk.Frame(win, bg=C["accent"], height=2).pack(fill=tk.X)
        hdr = tk.Frame(win, bg=C["surface"], height=40)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⭐  Saved Searches", bg=C["surface"], fg=C["fg"],
                 font=(FBOLD, 11, "bold")).pack(side=tk.LEFT, padx=14, pady=10)
        lb = tk.Listbox(win, bg=C["surface"], fg=C["fg"], font=(FUI, 10),
                         relief=tk.FLAT, highlightthickness=0,
                         selectbackground=C["sel"], selectforeground=C["accent2"],
                         activestyle="none")
        lb.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        for s in self.saved_searches:
            lb.insert(tk.END, f"  {s}")

        def _run():
            sel = lb.curselection()
            if sel:
                self.sq_var.set(self.saved_searches[sel[0]])
                win.destroy()
                self._do_search()

        def _del():
            sel = lb.curselection()
            if sel:
                self.saved_searches.pop(sel[0])
                lb.delete(sel[0])
                self._save_cfg()

        bf = tk.Frame(win, bg=C["surface"])
        bf.pack(fill=tk.X, padx=10, pady=(0, 10))
        _btn(bf, "▶ Run", _run, style="accent", C=C).pack(side=tk.LEFT, padx=(0, 4))
        _btn(bf, "🗑 Del", _del, style="red",    C=C).pack(side=tk.LEFT)
        _btn(bf, "Close",  win.destroy, style="ghost", C=C).pack(side=tk.RIGHT)
        lb.bind("<Double-1>", lambda _: _run())

    # ── Commits: Load ────────────────────────────────────────────────────
    def _load_commits(self, _=None):
        if not self.username:
            self._toast("Connect first", "warn")
            return
        repo_sel = self._cr_var.get() if hasattr(self, "_cr_var") else ""
        if repo_sel and repo_sel != "(All Repos)":
            self._load_single_repo(repo_sel)
        elif self.current_repo:
            self._load_single_repo(self.current_repo)
        else:
            self._toast("Select a repository first", "warn")

    def _load_single_repo(self, repo_name: str):
        self._commit_page = 1
        self.ctree.delete(*self.ctree.get_children())
        self._commits_cache.clear()
        self._ctotal_lbl.config(text="Loading…")
        self._cprog.start()
        author = self._cauth_var.get().strip() if hasattr(self, "_cauth_var") else ""
        path   = self._cpath_var.get().strip() if hasattr(self, "_cpath_var") else ""
        msg_f  = self._cmsg_var.get().strip()  if hasattr(self, "_cmsg_var")  else ""
        branch = self.branch_var.get()

        def _work():
            all_commits: List[Dict] = []
            page = 1
            while True:
                try:
                    params: Dict[str, Any] = {"per_page": 100, "page": page}
                    if branch: params["sha"]    = branch
                    if author: params["author"] = author
                    if path:   params["path"]   = path
                    r = rget(self.sess,
                              f"{self.API}/repos/{self.username}/{repo_name}/commits",
                              params=params, timeout=25)
                    if r.status_code != 200: break
                    batch = r.json()
                    if not batch: break
                    raw_len = len(batch)
                    for c in batch:
                        c["_repo"]   = repo_name
                        c["_branch"] = branch
                    if msg_f:
                        ml    = msg_f.lower()
                        batch = [c for c in batch if ml in
                                  (c.get("commit", {}).get("message", "") or "").lower()]
                    all_commits.extend(batch)
                    self.root.after(0, lambda n=len(all_commits):
                                    self._ctotal_lbl.config(text=f"Loading… {n}"))
                    if raw_len < 100: break
                    page += 1
                except Exception:
                    break
            self._index.add(repo_name, branch, all_commits)
            self.root.after(0, lambda cs=all_commits: self._on_commits(cs))

        threading.Thread(target=_work, daemon=True).start()

    def _load_more(self):
        self._commit_page += 1
        self._fetch_commit_page(self._commit_page)

    def _fetch_commit_page(self, page: int):
        if not self.current_repo: return
        branch = self.branch_var.get()

        def _work():
            try:
                params = {"per_page": 100, "page": page}
                if branch: params["sha"] = branch
                r = rget(self.sess,
                          f"{self.API}/repos/{self.username}/{self.current_repo}/commits",
                          params=params, timeout=25)
                if r.status_code == 200:
                    batch = r.json()
                    for c in batch:
                        c["_repo"]   = self.current_repo
                        c["_branch"] = branch
                    self._index.add(self.current_repo, branch, batch)
                    self.root.after(0, lambda cs=batch: self._append_commits(cs))
            except Exception as e:
                self.root.after(0, lambda: self._toast(str(e), "err"))

        threading.Thread(target=_work, daemon=True).start()

    def _on_commits(self, commits: List[Dict]):
        self._cprog.stop()
        self._render_commits(commits, clear=True)
        n = len(commits)
        self._ctotal_lbl.config(text=f"{n:,} commits")
        self._set_status(
            f"Loaded {n:,} commits from "
            f"{commits[0].get('_repo', '') if commits else '?'}", "ok")
        self._log(f"Commits: {n}")
        self._update_idx_display()
        self._update_banner(True)
        self._toast(f"Loaded {n:,} commits", "ok")

    def _append_commits(self, commits: List[Dict]):
        self._render_commits(commits, clear=False)
        n = len(self.ctree.get_children())
        self._ctotal_lbl.config(text=f"{n:,} commits")

    # ── Load ALL Repos ALL Commits ────────────────────────────────────────
    def _load_all_repos_commits(self):
        if not self.username:
            self._toast("Connect first", "warn"); return
        if self._loading_all:
            self._toast("Already loading — click Stop to cancel", "warn"); return
        if not self.repo_data:
            self._toast("Load repositories first (F5)", "warn"); return

        self._loading_all = True
        self._index_cancel.clear()
        self._index.clear()
        self.ctree.delete(*self.ctree.get_children())
        self._commits_cache.clear()
        self._cprog.start()
        self._cload_btn.config(state=tk.DISABLED)
        self._cstop_btn.config(state=tk.NORMAL)
        self._call_btn.config(state=tk.DISABLED)
        self._idx_prog.start()
        self._toast(f"Indexing ALL repos ({len(self.repo_data)}) — this may take a while",
                     "info", 5000)
        self._set_status("Indexing all repositories…")
        repos = list(self.repo_data.values())

        def _work():
            total_repos = len(repos)
            done_repos  = 0
            for rd in repos:
                if self._index_cancel.is_set(): break
                repo_name  = rd.get("name", "")
                done_repos += 1
                try:
                    br_r = rget(self.sess,
                                 f"{self.API}/repos/{self.username}/{repo_name}/branches",
                                 params={"per_page": 100}, timeout=12)
                    branches = ([b["name"] for b in br_r.json()]
                                if br_r.status_code == 200
                                else [rd.get("default_branch", "main")])
                    for branch in branches:
                        if self._index_cancel.is_set(): break
                        page = 1
                        while not self._index_cancel.is_set():
                            try:
                                r = rget(self.sess,
                                          f"{self.API}/repos/{self.username}"
                                          f"/{repo_name}/commits",
                                          params={"per_page": 100, "page": page,
                                                  "sha": branch},
                                          timeout=25)
                                if r.status_code != 200: break
                                batch = r.json()
                                if not batch: break
                                added = self._index.add(repo_name, branch, batch)
                                if added > 0:
                                    self.root.after(
                                        0, lambda cs=batch[:], rn=repo_name, br=branch:
                                        self._live_add_commits(cs, rn, br))
                                if len(batch) < 100: break
                                page += 1
                                time.sleep(0.05)
                            except Exception:
                                break
                except Exception:
                    pass
                pct = (f"{done_repos}/{total_repos} repos  ·  "
                        f"{self._index.total():,} commits")
                self.root.after(0, lambda t=pct: (
                    self._ctotal_lbl.config(text=t),
                    self._set_idx_status(t)))
            self.root.after(0, self._on_all_done)

        threading.Thread(target=_work, daemon=True).start()

    def _live_add_commits(self, commits: List[Dict], repo: str, branch: str):
        for c in commits:
            c["_repo"]   = repo
            c["_branch"] = branch
        self._render_commits(commits, clear=False)

    def _on_all_done(self):
        self._loading_all = False
        self._cprog.stop()
        self._idx_prog.stop()
        self._cload_btn.config(state=tk.NORMAL)
        self._cstop_btn.config(state=tk.DISABLED)
        self._call_btn.config(state=tk.NORMAL)
        total = self._index.total()
        repos = len(self._index.indexed_repos)
        msg   = f"✓ Indexed {total:,} commits across {repos} repositories"
        self._ctotal_lbl.config(text=f"{total:,} commits indexed")
        self._set_status(msg, "ok")
        self._log(msg)
        self._update_idx_display()
        self._update_banner(True)
        self._toast(msg, "ok", 5000)
        # Re-sort tree
        all_c = self._index.get_all()
        self.ctree.delete(*self.ctree.get_children())
        self._commits_cache.clear()
        self._render_commits(all_c, clear=False)

    def _stop_index(self):
        self._index_cancel.set()
        self._loading_all = False
        self._cprog.stop()
        self._idx_prog.stop()
        self._cload_btn.config(state=tk.NORMAL)
        self._cstop_btn.config(state=tk.DISABLED)
        self._call_btn.config(state=tk.NORMAL)
        self._toast(f"Stopped. {self._index.total():,} commits indexed so far", "warn")

    def _render_commits(self, commits: List[Dict], clear: bool = False):
        C = self.C
        if clear:
            self.ctree.delete(*self.ctree.get_children())
            self._commits_cache.clear()

        # Build set of known SHAs for deduplication (fast O(1) lookup)
        known_shas: Set[str] = {
            c.get("sha", "") for c in self._commits_cache.values()
        }

        last_group = ""
        for cd in commits:
            sha = cd.get("sha", "")
            if sha and sha in known_shas:
                continue
            if sha:
                known_shas.add(sha)

            commit   = cd.get("commit", {})
            msg      = (commit.get("message", "") or "").split("\n")[0][:90]
            author   = (commit.get("author") or {}).get("name", "")
            date_iso = (commit.get("author") or {}).get("date", "")
            date     = rel_t(date_iso)
            repo     = cd.get("_repo", "") or self.current_repo or ""
            group    = date_group(date_iso)

            if group != last_group:
                last_group = group
                self.ctree.insert("", "end",
                                   text=f"  ── {group} ──",
                                   values=("", "", "", ""),
                                   tags=("g",))
                self.ctree.tag_configure("g", foreground=C["fg_dim"], font=(FUI, 8))

            iid = self.ctree.insert("", "end",
                                     text=f"  {msg}",
                                     values=(sha[:8], author, date, repo),
                                     tags=("c",))
            self.ctree.tag_configure("c", foreground=C["fg"])
            self._commits_cache[iid] = cd

    # ── Commit Detail ─────────────────────────────────────────────────────
    def _on_csel(self, _=None):
        sel = self.ctree.selection()
        if not sel: return
        cd = self._commits_cache.get(sel[0])
        if not cd: return
        self._show_cmeta(cd)
        self._dtabs.select(0)
        sha  = cd.get("sha", "")
        repo = cd.get("_repo", "") or self.current_repo or ""
        if sha and repo:
            self._load_diff(sha, repo)

    def _on_cdbl(self, _=None):
        sel = self.ctree.selection()
        if not sel: return
        cd   = self._commits_cache.get(sel[0])
        sha  = cd.get("sha", "") if cd else ""
        repo = (cd.get("_repo", "") or self.current_repo or "") if cd else ""
        url  = cd.get("html_url", "") if cd else ""
        if not url and sha and repo:
            url = f"https://github.com/{self.username}/{repo}/commit/{sha}"
        if url:
            webbrowser.open(url)

    def _show_cmeta(self, cd: Dict):
        C = self.C
        t = self._cmeta
        t.config(state=tk.NORMAL)
        t.delete("1.0", tk.END)
        for tag, kw in [
            ("h",   {"font": (FBOLD, 12, "bold"),   "foreground": C["accent2"]}),
            ("k",   {"font": (FUI,   8,  "bold"),   "foreground": C["fg_dim"]}),
            ("v",   {"font": (FUI,   9),             "foreground": C["fg_muted"]}),
            ("m",   {"font": (FMONO, 9),             "foreground": C["fg"]}),
            ("sha", {"font": (FMONO, 11, "bold"),   "foreground": C["purple"]}),
            ("add", {"font": (FUI,   9),             "foreground": C["green"]}),
            ("del", {"font": (FUI,   9),             "foreground": C["red"]}),
        ]:
            t.tag_configure(tag, **kw)

        sha    = cd.get("sha", "")
        commit = cd.get("commit", {})
        author = commit.get("author") or {}
        cmtr   = commit.get("committer") or {}
        msg    = commit.get("message", "")
        stats  = cd.get("stats", {})
        files  = cd.get("files", [])
        repo   = cd.get("_repo", "") or self.current_repo or ""
        branch = cd.get("_branch", "")

        t.insert(tk.END, sha[:16], "sha"); t.insert(tk.END, "\n\n")
        if repo:   t.insert(tk.END, "Repository   ", "k"); t.insert(tk.END, repo + "\n", "v")
        if branch: t.insert(tk.END, "Branch       ", "k"); t.insert(tk.END, branch + "\n", "v")
        t.insert(tk.END, "\nMessage\n", "k"); t.insert(tk.END, msg, "m")
        t.insert(tk.END, "\n\nAuthor       ", "k"); t.insert(tk.END, author.get("name", ""), "v")
        t.insert(tk.END, "\nEmail        ", "k"); t.insert(tk.END, author.get("email", ""), "v")
        t.insert(tk.END, "\nDate         ", "k")
        t.insert(tk.END,
                  f"{rel_t(author.get('date', ''))}  ({fmt_dt(author.get('date', ''))})", "v")

        if cmtr.get("name", "") != author.get("name", ""):
            t.insert(tk.END, "\nCommitter    ", "k"); t.insert(tk.END, cmtr.get("name", ""), "v")

        parents = cd.get("parents", [])
        if parents:
            t.insert(tk.END, "\nParents      ", "k")
            for p in parents:
                t.insert(tk.END, p.get("sha", "")[:10] + " ", "sha")

        if stats:
            t.insert(tk.END, "\n\nStats        ", "k")
            t.insert(tk.END, f"+{stats.get('additions', 0)} ", "add")
            t.insert(tk.END, f"-{stats.get('deletions', 0)}",  "del")

        if files:
            t.insert(tk.END, f"\n\nFiles Changed  ({len(files)})\n", "k")
            for fi in files:
                st = fi.get("status", "")[:1].upper()
                fn = fi.get("filename", "")
                a  = fi.get("additions", 0)
                d  = fi.get("deletions", 0)
                t.insert(tk.END, f"  [{st}] {fn}  ", "v")
                t.insert(tk.END, f"+{a} ", "add")
                t.insert(tk.END, f"-{d}\n", "del")

        t.config(state=tk.DISABLED)
        url = cd.get("html_url", "") or f"https://github.com/{self.username}/{repo}/commit/{sha}"
        self._copen_btn.config(command=lambda u=url: webbrowser.open(u))
        self._ccopy_btn.config(command=lambda s=sha: (
            self.root.clipboard_clear(),
            self.root.clipboard_append(s),
            self._toast("SHA copied", "ok")))
        patch_url = f"https://github.com/{self.username}/{repo}/commit/{sha}.patch"
        self._cdownload_btn.config(command=lambda u=patch_url: webbrowser.open(u))

    def _show_from_search(self, cd: Dict):
        repo      = (cd.get("repository", {}).get("full_name", "")
                     or cd.get("_repo", ""))
        repo_name = repo.split("/")[-1] if "/" in repo else repo
        if repo_name:
            self.current_repo = repo_name
        self._nav_to("commits")
        self._show_cmeta(cd)
        sha = cd.get("sha", "")
        if sha:
            self._load_diff(sha, repo_name or self.current_repo or "")

    # ── Diff Rendering ────────────────────────────────────────────────────
    def _load_diff(self, sha: str, repo: str = ""):
        repo = repo or self.current_repo or ""
        if sha in self._diff_cache:
            self._render_diff(self._diff_cache[sha])
            return
        self._dload_lbl.config(text="Loading diff…")
        self._dtxt.config(state=tk.NORMAL)
        self._dtxt.delete("1.0", tk.END)
        self._dtxt.config(state=tk.DISABLED)

        def _work():
            try:
                r = rget(self.sess,
                          f"{self.API}/repos/{self.username}/{repo}/commits/{sha}",
                          hdrs={"Accept": "application/vnd.github.diff"},
                          timeout=25)
                if r.status_code == 200:
                    raw = r.text
                    if len(self._diff_cache) > 80:
                        del self._diff_cache[next(iter(self._diff_cache))]
                    self._diff_cache[sha] = raw
                    self.root.after(0, lambda: self._render_diff(raw))
                else:
                    self.root.after(0, lambda: self._dload_lbl.config(
                        text=f"Diff N/A ({r.status_code})"))
            except Exception as e:
                self.root.after(0, lambda: self._dload_lbl.config(text=f"Error: {e}"))

        threading.Thread(target=_work, daemon=True).start()

    def _render_diff(self, raw: str):
        self._dload_lbl.config(text="")
        files = DP.parse(raw)
        self._diff_files = files
        adds, dels = DP.stats(files)
        self._dstat.config(text=f"+{adds}  −{dels}")
        self.dftree.delete(*self.dftree.get_children())
        for fi in files:
            path = fi.get("path", "")
            fa   = fi.get("additions", 0)
            fd   = fi.get("deletions", 0)
            self.dftree.insert("", "end",
                                text=f"  {_fi(path)}  {path}  +{fa}−{fd}")
        children = self.dftree.get_children()
        if children:
            self.dftree.selection_set(children[0])
            if files:
                self._render_diff_file(files[0])

    def _on_dfsel(self, _=None):
        sel = self.dftree.selection()
        if not sel: return
        idx = self.dftree.index(sel[0])
        if idx < len(self._diff_files):
            self._render_diff_file(self._diff_files[idx])

    def _redraw_diff(self):
        sel = self.dftree.selection()
        if not sel or not self._diff_files: return
        idx = self.dftree.index(sel[0])
        if idx < len(self._diff_files):
            self._render_diff_file(self._diff_files[idx])

    def _render_diff_file(self, fi: Dict):
        C    = self.C
        t    = self._dtxt
        mode = self._dmode.get()
        t.config(state=tk.NORMAL)
        t.delete("1.0", tk.END)
        TAGS = [
            ("add",  C["diff_add"],  C["diff_add_fg"]),
            ("del",  C["diff_del"],  C["diff_del_fg"]),
            ("hunk", C["diff_hunk"], C["diff_hunk_fg"]),
            ("ctx",  C["diff_ctx"],  C["diff_ctx_fg"]),
        ]
        for tag, bg, fg in TAGS:
            t.tag_configure(tag, background=bg, foreground=fg, font=(FMONO, 9))
        path = fi.get("path", "")
        fa   = fi.get("additions", 0)
        fd   = fi.get("deletions", 0)
        t.insert(tk.END, f"  {path}   +{fa}  −{fd}\n", "hunk")
        t.insert(tk.END, "─" * 80 + "\n", "hunk")
        for hunk in fi.get("hunks", []):
            t.insert(tk.END, f"\n{hunk.get('header', '')}\n", "hunk")
            if mode == "unified":
                for kind, line in hunk.get("lines", []):
                    pfx = {"add": "+", "del": "−", "ctx": " "}.get(kind, " ")
                    t.insert(tk.END, f"{pfx} {line}\n", kind)
            else:
                left  = [(k, l) for k, l in hunk.get("lines", []) if k in ("del", "ctx")]
                right = [(k, l) for k, l in hunk.get("lines", []) if k in ("add", "ctx")]
                W = 48
                for i in range(max(len(left), len(right))):
                    lk, ll = left[i]  if i < len(left)  else ("ctx", "")
                    rk, rl = right[i] if i < len(right) else ("ctx", "")
                    t.insert(tk.END, f"{'−' if lk=='del' else ' '} {ll:<{W}}", lk)
                    t.insert(tk.END, " │ ", "ctx")
                    t.insert(tk.END, f"{'+'if rk=='add'else' '} {rl}\n", rk)
        t.config(state=tk.DISABLED)

    # ── Operations ────────────────────────────────────────────────────────
    def _chk_write(self) -> bool:
        if self.auth_mode != "token" or not self.token:
            self._toast("Write operations require Token authentication", "warn")
            return False
        if not self.current_repo:
            self._toast("Select a repository first", "warn")
            return False
        return True

    def _dl_selected(self):
        if not self.current_repo:
            self._toast("Select a repository first", "warn"); return
        sel   = self.tree.selection()
        items = []
        for iid in sel:
            vals = self.tree.item(iid, "values")
            name = self.tree.item(iid, "text").strip()
            if vals and vals[1] == "File":
                path = f"{self.current_path}/{name}" if self.current_path else name
                items.append((name, path))
        if not items:
            self._toast("Select one or more files", "warn"); return
        dest = filedialog.askdirectory(title="Choose Download Destination")
        if dest:
            self._dl_items(items, dest)

    def _dl_one(self, name: str):
        path = f"{self.current_path}/{name}" if self.current_path else name
        dest = filedialog.askdirectory(title="Choose Download Destination")
        if dest:
            self._dl_items([(name, path)], dest)

    def _dl_items(self, items: List[Tuple[str, str]], dest: str):
        branch = self.branch_var.get()
        total  = len(items)
        self._prog_start()

        def _work():
            done = 0
            errs = []
            for name, path in items:
                self.root.after(0, lambda n=name: self._prog_var.set(f"Downloading {n}…"))
                try:
                    r = rget(self.sess,
                              f"{self.API}/repos/{self.username}/{self.current_repo}"
                              f"/contents/{path}",
                              params={"ref": branch} if branch else {},
                              timeout=20)
                    if r.status_code == 200:
                        with open(os.path.join(dest, name), "wb") as fh:
                            fh.write(base64.b64decode(r.json().get("content", "")))
                        done += 1
                    else:
                        errs.append(name)
                except Exception as e:
                    errs.append(f"{name}: {e}")
            self.root.after(0, self._prog_stop)
            if errs:
                self.root.after(0, lambda: self._toast(f"Errors: {', '.join(errs[:3])}", "err"))
            else:
                self.root.after(0, lambda: self._toast(f"Downloaded {done} file(s)", "ok"))
            self.root.after(0, lambda: self._log(f"Downloaded {done}/{total}"))

        threading.Thread(target=_work, daemon=True).start()

    def _dl_all(self):
        if not self.current_repo:
            self._toast("Select a repository first", "warn"); return
        branch = self.branch_var.get() or "main"
        webbrowser.open(
            f"https://github.com/{self.username}/{self.current_repo}"
            f"/archive/refs/heads/{branch}.zip")
        self._toast(f"Downloading {self.current_repo} as ZIP…", "ok")
        self._log(f"ZIP download: {self.current_repo}")

    def _dl_folder(self):
        if not self.current_repo:
            self._toast("Select a repository first", "warn"); return
        dest = filedialog.askdirectory(title="Choose Destination")
        if dest:
            items = [(f["name"], f.get("path", "")) for f in self.all_items["files"]]
            if items:
                self._dl_items(items, dest)
            else:
                self._toast("No files in current folder", "warn")

    def _upload_file(self):
        if not self._chk_write(): return
        path = filedialog.askopenfilename(title="Choose File to Upload")
        if not path: return
        name = os.path.basename(path)
        dest = simpledialog.askstring(
            "Upload Path", "Destination path in repo (blank for root):",
            parent=self.root) or ""
        dest_path = (f"{dest.strip('/')}/{name}" if dest.strip() else name)
        branch    = self.branch_var.get()
        self._prog_start()

        def _work():
            try:
                with open(path, "rb") as fh:
                    content = base64.b64encode(fh.read()).decode()
                r = rget(self.sess,
                          f"{self.API}/repos/{self.username}/{self.current_repo}"
                          f"/contents/{dest_path}",
                          timeout=10)
                sha = r.json().get("sha", "") if r.status_code == 200 else ""
                payload: Dict[str, Any] = {
                    "message": f"Upload {name} via GitView",
                    "content": content,
                    "branch": branch,
                }
                if sha: payload["sha"] = sha
                r2 = self.sess.put(
                    f"{self.API}/repos/{self.username}/{self.current_repo}"
                    f"/contents/{dest_path}",
                    json=payload, timeout=25)
                if r2.status_code in (200, 201):
                    self.root.after(0, lambda: self._toast(f"Uploaded {name}", "ok"))
                    self.root.after(0, self._refresh_dir)
                else:
                    m = r2.json().get("message", "Upload failed")
                    self.root.after(0, lambda: self._toast(m, "err"))
            except Exception as e:
                self.root.after(0, lambda: self._toast(str(e), "err"))
            finally:
                self.root.after(0, self._prog_stop)

        threading.Thread(target=_work, daemon=True).start()

    def _upload_folder(self):
        if not self._chk_write(): return
        folder = filedialog.askdirectory(title="Choose Folder to Upload")
        if not folder: return
        dest  = simpledialog.askstring(
            "Destination", "Destination path in repo (blank for root):",
            parent=self.root) or ""
        files = [(str(p), os.path.relpath(str(p), folder))
                  for p in Path(folder).rglob("*") if os.path.isfile(str(p))]
        if not files:
            self._toast("No files found", "warn"); return
        branch = self.branch_var.get()
        total  = len(files)
        self._prog_start()

        def _work():
            done = 0
            for local, rel in files:
                rp = (f"{dest.strip('/')}/{rel}" if dest.strip() else rel).replace("\\", "/")
                self.root.after(0, lambda r=rel: self._prog_var.set(f"Uploading {r}…"))
                try:
                    with open(local, "rb") as fh:
                        content = base64.b64encode(fh.read()).decode()
                    r = rget(self.sess,
                              f"{self.API}/repos/{self.username}/{self.current_repo}"
                              f"/contents/{rp}",
                              timeout=10)
                    sha = r.json().get("sha", "") if r.status_code == 200 else ""
                    payload: Dict[str, Any] = {
                        "message": f"Upload {rel} via GitView",
                        "content": content,
                        "branch": branch,
                    }
                    if sha: payload["sha"] = sha
                    r2 = self.sess.put(
                        f"{self.API}/repos/{self.username}/{self.current_repo}"
                        f"/contents/{rp}",
                        json=payload, timeout=20)
                    if r2.status_code in (200, 201):
                        done += 1
                except:
                    pass
            self.root.after(0, self._prog_stop)
            self.root.after(0, lambda: self._toast(f"Uploaded {done}/{total} files", "ok"))
            self.root.after(0, lambda: self._log(f"Folder upload: {done}/{total}"))

        threading.Thread(target=_work, daemon=True).start()

    def _create_file(self):
        if not self._chk_write(): return
        name = simpledialog.askstring("Create File", "Filename:", parent=self.root)
        if not name: return
        content = simpledialog.askstring(
            "Initial Content", "Content (leave blank for empty):",
            parent=self.root) or ""
        path   = f"{self.current_path}/{name}" if self.current_path else name
        branch = self.branch_var.get()
        self._prog_start()

        def _work():
            try:
                r = self.sess.put(
                    f"{self.API}/repos/{self.username}/{self.current_repo}/contents/{path}",
                    json={"message": f"Create {name} via GitView",
                           "content": base64.b64encode(content.encode()).decode(),
                           "branch": branch},
                    timeout=20)
                if r.status_code in (200, 201):
                    self.root.after(0, lambda: self._toast(f"Created {name}", "ok"))
                    self.root.after(0, self._refresh_dir)
                else:
                    m = r.json().get("message", "Failed")
                    self.root.after(0, lambda: self._toast(m, "err"))
            except Exception as e:
                self.root.after(0, lambda: self._toast(str(e), "err"))
            finally:
                self.root.after(0, self._prog_stop)

        threading.Thread(target=_work, daemon=True).start()

    def _create_folder(self):
        if not self._chk_write(): return
        name = simpledialog.askstring("Create Folder", "Folder name:", parent=self.root)
        if not name: return
        path   = (f"{self.current_path}/{name}/.gitkeep"
                   if self.current_path else f"{name}/.gitkeep")
        branch = self.branch_var.get()
        self._prog_start()

        def _work():
            try:
                r = self.sess.put(
                    f"{self.API}/repos/{self.username}/{self.current_repo}/contents/{path}",
                    json={"message": f"Create {name}/ via GitView",
                           "content": base64.b64encode(b"").decode(),
                           "branch": branch},
                    timeout=20)
                if r.status_code in (200, 201):
                    self.root.after(0, lambda: self._toast(f"Created folder {name}", "ok"))
                    self.root.after(0, self._refresh_dir)
                else:
                    m = r.json().get("message", "Failed")
                    self.root.after(0, lambda: self._toast(m, "err"))
            except Exception as e:
                self.root.after(0, lambda: self._toast(str(e), "err"))
            finally:
                self.root.after(0, self._prog_stop)

        threading.Thread(target=_work, daemon=True).start()

    def _rename_sel(self):
        sel = self.tree.selection()
        if not sel: return
        iid  = sel[0]
        vals = self.tree.item(iid, "values")
        name = self.tree.item(iid, "text").strip()
        if vals and vals[1] == "Folder":
            self._toast("Folder renaming not supported via API", "warn"); return
        if not self._chk_write(): return
        new = simpledialog.askstring("Rename", f"New name for '{name}':", parent=self.root)
        if not new or new == name: return
        old_path = f"{self.current_path}/{name}" if self.current_path else name
        new_path = f"{self.current_path}/{new}"  if self.current_path else new
        branch   = self.branch_var.get()
        self._prog_start()

        def _work():
            try:
                r = rget(self.sess,
                          f"{self.API}/repos/{self.username}/{self.current_repo}"
                          f"/contents/{old_path}",
                          params={"ref": branch} if branch else {},
                          timeout=15)
                if r.status_code != 200:
                    self.root.after(0, lambda: self._toast("Could not read file", "err"))
                    return
                jd      = r.json()
                content = jd.get("content", "")
                sha     = jd.get("sha", "")
                r2 = self.sess.put(
                    f"{self.API}/repos/{self.username}/{self.current_repo}"
                    f"/contents/{new_path}",
                    json={"message": f"Rename {name} → {new} via GitView",
                           "content": content, "branch": branch},
                    timeout=20)
                if r2.status_code in (200, 201):
                    self.sess.delete(
                        f"{self.API}/repos/{self.username}/{self.current_repo}"
                        f"/contents/{old_path}",
                        json={"message": f"Remove {name} after rename",
                               "sha": sha, "branch": branch},
                        timeout=15)
                    self.root.after(0, lambda: self._toast(f"Renamed to {new}", "ok"))
                    self.root.after(0, self._refresh_dir)
                else:
                    m = r2.json().get("message", "Failed")
                    self.root.after(0, lambda: self._toast(m, "err"))
            except Exception as e:
                self.root.after(0, lambda: self._toast(str(e), "err"))
            finally:
                self.root.after(0, self._prog_stop)

        threading.Thread(target=_work, daemon=True).start()

    def _delete_sel(self):
        sel = self.tree.selection()
        if not sel: return
        if not self._chk_write(): return
        items = []
        for iid in sel:
            vals = self.tree.item(iid, "values")
            name = self.tree.item(iid, "text").strip()
            if vals and vals[1] == "File":
                items.append(name)
        if not items: return
        if not messagebox.askyesno("Delete Files",
                                    f"Delete {len(items)} file(s)?\nThis cannot be undone.",
                                    icon="warning"):
            return
        branch = self.branch_var.get()
        self._prog_start()

        def _work():
            done = 0
            for name in items:
                try:
                    path = f"{self.current_path}/{name}" if self.current_path else name
                    r = rget(self.sess,
                              f"{self.API}/repos/{self.username}/{self.current_repo}"
                              f"/contents/{path}",
                              params={"ref": branch} if branch else {},
                              timeout=10)
                    if r.status_code == 200:
                        sha = r.json().get("sha", "")
                        r2  = self.sess.delete(
                            f"{self.API}/repos/{self.username}/{self.current_repo}"
                            f"/contents/{path}",
                            json={"message": f"Delete {name} via GitView",
                                   "sha": sha, "branch": branch},
                            timeout=15)
                        if r2.status_code in (200, 204):
                            done += 1
                except:
                    pass
            self.root.after(0, self._prog_stop)
            self.root.after(0, lambda: self._toast(
                f"Deleted {done}/{len(items)}",
                "ok" if done == len(items) else "warn"))
            self.root.after(0, self._refresh_dir)
            self.root.after(0, lambda: self._log(f"Deleted {done}/{len(items)}"))

        threading.Thread(target=_work, daemon=True).start()

    def _create_repo(self):
        if not self.token:
            self._toast("Token required to create repos", "warn"); return
        name = simpledialog.askstring("Create Repository", "Repository name:", parent=self.root)
        if not name: return
        desc = simpledialog.askstring("Description", "Repository description (optional):", parent=self.root) or ""
        priv = messagebox.askyesno("Visibility", "Make repository private?")
        self._prog_start()

        def _work():
            try:
                r = self.sess.post(f"{self.API}/user/repos",
                                    json={"name": name, "description": desc,
                                           "auto_init": True, "private": priv},
                                    timeout=20)
                if r.status_code == 201:
                    self.root.after(0, lambda: self._toast(f"Created: {name}", "ok"))
                    self.root.after(0, self._load_repos)
                else:
                    m = r.json().get("message", "Failed")
                    self.root.after(0, lambda: self._toast(m, "err"))
            except Exception as e:
                self.root.after(0, lambda: self._toast(str(e), "err"))
            finally:
                self.root.after(0, self._prog_stop)

        threading.Thread(target=_work, daemon=True).start()

    def _open_browser(self):
        if self.username and self.current_repo:
            webbrowser.open(f"https://github.com/{self.username}/{self.current_repo}")

    def _open_sel_browser(self):
        sel = self.tree.selection()
        if not sel: return
        name   = self.tree.item(sel[0], "text").strip()
        vals   = self.tree.item(sel[0], "values")
        path   = f"{self.current_path}/{name}" if self.current_path else name
        branch = self.branch_var.get()
        kind   = "tree" if vals and vals[1] == "Folder" else "blob"
        webbrowser.open(
            f"https://github.com/{self.username}/{self.current_repo}"
            f"/{kind}/{branch}/{path}")

    def _export_commits_csv(self):
        total = self._index.total()
        if total == 0:
            self._toast("No commits indexed yet. Load commits first.", "warn")
            return
        dest = filedialog.asksaveasfilename(
            title="Save Commits CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not dest: return
        try:
            csv_data = self._index.export_csv()
            with open(dest, "w", newline="", encoding="utf-8") as fh:
                fh.write(csv_data)
            self._toast(f"Exported {total:,} commits to CSV", "ok")
            self._log(f"Exported {total:,} commits → {dest}")
        except Exception as e:
            self._toast(str(e), "err")

    # ── Progress Helpers ──────────────────────────────────────────────────
    def _prog_start(self):
        if not self._prog_running:
            self._prog_running = True
            self._prog.start()

    def _prog_stop(self):
        if self._prog_running:
            self._prog_running = False
            self._prog.stop()
        self._prog_var.set("No active operations")

    # ── Status / Index Display ────────────────────────────────────────────
    def _set_status(self, msg: str, level: str = "info"):
        COLORS = {
            "ok":   self.C["green"],
            "err":  self.C["red"],
            "warn": self.C["amber"],
            "info": self.C["fg_dim"],
        }
        try:
            self._status.config(text=f"  {msg}", fg=COLORS.get(level, self.C["fg_dim"]))
        except:
            pass

    def _set_idx_status(self, text: str):
        try: self._idx_status.config(text=text)
        except: pass

    def _update_idx_display(self):
        total = self._index.total()
        repos = len(self._index.indexed_repos)
        try:
            self._idx_commits_lbl.config(text=f"{total:,} commits")
            self._idx_repos_lbl.config(text=f"{repos} repo{'s' if repos != 1 else ''}")
            self._idx_status.config(
                text=f"Index: {total:,} commits · {repos} repos" if total > 0 else "")
        except:
            pass

    def _log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        try:
            self._log_txt.config(state=tk.NORMAL)
            self._log_txt.insert(tk.END, f"[{ts}] {msg}\n")
            self._log_txt.see(tk.END)
            self._log_txt.config(state=tk.DISABLED)
        except:
            pass

    def _clear_log(self):
        try:
            self._log_txt.config(state=tk.NORMAL)
            self._log_txt.delete("1.0", tk.END)
            self._log_txt.config(state=tk.DISABLED)
        except:
            pass

    # ── Theme Toggle ──────────────────────────────────────────────────────
    def _toggle_theme(self, _=None):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.C = LIGHT if self.current_theme == "light" else DARK
        self._apply_styles()
        self._save_cfg()
        self._toast(f"Switched to {self.current_theme} mode", "info")
        # Note: full widget re-coloring requires a restart for tkinter
        # but ttk styles update immediately for tree/notebook/scrollbars

    # ── Config ────────────────────────────────────────────────────────────
    def _save_cfg(self):
        try:
            CFG.write_text(json.dumps({
                "theme":       self.current_theme,
                "auth_mode":   self.auth_mode,
                "token":       self.tok_var.get() if self.auth_mode == "token" else "",
                "public_user": self.pub_var.get() if self.auth_mode == "public" else "",
                "pinned":      self.pinned,
                "history":     list(self.search_history),
                "saved":       self.saved_searches,
                "recent":      list(self.recent_repos),
            }, indent=2))
        except:
            pass

    def _load_cfg(self):
        try:
            if not CFG.exists(): return
            cfg = json.loads(CFG.read_text())
            th  = cfg.get("theme", "dark")
            if th != self.current_theme:
                self.current_theme = th
                self.C = LIGHT if th == "light" else DARK
                self._apply_styles()
            self.pinned         = cfg.get("pinned",  [])
            self.search_history = deque(cfg.get("history", []), maxlen=50)
            self.saved_searches = cfg.get("saved",   [])
            self.recent_repos   = deque(cfg.get("recent", []), maxlen=10)
            mode = cfg.get("auth_mode", "token")
            if mode == "token":
                tok = cfg.get("token", "")
                if tok:
                    self.tok_var.set(tok)
                    self._sw_token()
            else:
                user = cfg.get("public_user", "")
                if user:
                    self.pub_var.set(user)
                    self._sw_public()
        except:
            pass

    # ── Help ──────────────────────────────────────────────────────────────
    def _show_help(self, _=None):
        C = self.C
        win = tk.Toplevel(self.root)
        win.title("GitView — Help")
        win.geometry("860x740")
        win.configure(bg=C["bg"])
        tk.Frame(win, bg=C["accent"], height=2).pack(fill=tk.X)
        hdr = tk.Frame(win, bg=C["surface"], height=44)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"❓  GitView v{VER}  —  Help & Quick Start",
                 bg=C["surface"], fg=C["fg_bright"],
                 font=(FBOLD, 12, "bold")).pack(side=tk.LEFT, padx=14, pady=12)
        t = tk.Text(win, wrap=tk.WORD, bg=C["surface"], fg=C["fg"],
                     font=(FUI, 10), relief=tk.FLAT, padx=22, pady=14,
                     selectbackground=C["sel"], highlightthickness=0, state=tk.NORMAL)
        vsb = _vsb(win, t.yview)
        t.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        t.pack(fill=tk.BOTH, expand=True)

        HELP = f"""
GitView v{VER}  —  Enterprise GitHub Intelligence Platform
{"─"*64}

👋  QUICK START

  ① TOKEN MODE  (Recommended — 5,000 req/hr)
     GitHub → Settings → Developer settings → Personal access tokens
     → Generate new token (Classic) → tick "repo" → paste here → Connect

  ② PUBLIC MODE  (No auth — 60 req/hr)
     Enter any GitHub username or github.com/username URL → Browse

──────────────────────────────────────────────────────────────

⌘  COMMAND PALETTE  (Ctrl+K)
   Access everything instantly. Arrow keys navigate, Enter runs.

📁  EXPLORER
   • Select repo + branch from dropdowns
   • Click breadcrumb path segments → jump to any parent folder
   • Double-click folders to navigate  |  Backspace to go up
   • Single-click files → instant preview in side panel
   • Ctrl+F = focus filter bar  |  Space = expand preview window
   • Ctrl+G = Find in preview  |  Right-click for context menu
   • Click 📋 in breadcrumb to copy current path

🔍  SEARCH  (6 intelligent scopes)
   • Repos    — Search all repositories with smart ranking
   • Content  — Search code content (needs Token)
   • Files    — Search filenames across repos (needs Token)
   • Commits  — Search commit messages via GitHub API
   • Topics   — Search by repository topic / language
   • Index    — Search locally indexed commits (blazing fast)

◎  COMMITS
   • Load Commits    — loads all commits from selected repo (ALL pages)
   • Load ALL Repos  — indexes EVERY commit from EVERY repo, EVERY branch
   • Streams results live  |  Click commit → Details tab
   • Δ Diff tab → unified or side-by-side diff with per-file stats
   • Double-click commit → open on GitHub
   • Export to CSV via sidebar button or Operations tab

📊  RATE LIMIT  (bottom-right status bar)
   Green = >50% remaining  |  Amber = 15-50%  |  Red = <15%
   Token mode: 5,000/hr  |  Public mode: 60/hr

⌨️  KEYBOARD SHORTCUTS
   Ctrl+K   Command Palette       Ctrl+T   Toggle Theme
   Ctrl+F   Filter Files          Ctrl+N   New File
   Ctrl+D   Download Selected     Ctrl+U   Upload File
   Ctrl+G   Find in Preview       F5       Refresh Repos
   F1       Help                  F2       Rename
   Delete   Delete                Escape   Cancel Search
   Backspace  Go up directory
   Alt+1–5  Navigate to tab

🐛  BUGS FIXED in v{VER}
   • CRASH: pady=(0,4) tuple in tk.Label → _tkinter.TclError — FIXED
   • CRASH: %-d strftime on Windows → OSError — FIXED (cross-platform)
   • BUG:   r.json() called twice in commit loader — FIXED

💾  CONFIG  →  ~/.gitview{VER.split('.')[0]}_config.json
{"─"*64}
Author: Ali Essam  ·  Egypt 🇪🇬  ·  github.com/dragonked2
"""
        t.insert("1.0", HELP)
        t.config(state=tk.DISABLED)
        bot = tk.Frame(win, bg=C["surface2"], height=42)
        bot.pack(fill=tk.X, side=tk.BOTTOM)
        bot.pack_propagate(False)
        _btn(bot, "  LinkedIn  ",
              lambda: webbrowser.open("https://www.linkedin.com/in/dragonked2"),
              style="accent", C=C).pack(side=tk.LEFT, padx=12, pady=6)
        _btn(bot, "  ⭐ GitHub  ",
              lambda: webbrowser.open("https://github.com/dragonked2"),
              style="ghost2", C=C).pack(side=tk.LEFT, padx=(0, 8), pady=6)
        _btn(bot, "  Close  ",
              win.destroy, style="ghost", C=C).pack(side=tk.RIGHT, padx=12, pady=6)


# ── Entry Point ────────────────────────────────────────────────────────────
def main():
    root = tk.Tk()
    try:
        root.iconbitmap(default="gitview.ico")
    except:
        pass
    app = GitView(root)
    root.update_idletasks()
    W = root.winfo_width()
    H = root.winfo_height()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")
    root.mainloop()


if __name__ == "__main__":
    main()