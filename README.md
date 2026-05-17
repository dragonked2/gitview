# ⬡ GitView

> **Professional GitHub Repository Explorer** — Browse, download, upload, and manage your GitHub repositories through a sleek, modern desktop interface.

![GitView Banner](https://img.shields.io/badge/GitView-v1.0.0-2f81f7?style=for-the-badge&logo=github&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3fb950?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-bc8cff?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-39c5cf?style=for-the-badge)

---

## ✨ Features

| Category | Capabilities |
|---|---|
| 📁 **Explorer** | Browse files & folders with smart icons, breadcrumb navigation, live search/filter |
| 📥 **Downloads** | Single file, selected files, entire folder, or full repository download |
| 📤 **Uploads** | Upload individual files or entire folder trees — committed directly to GitHub |
| ✏️ **File Ops** | Create, rename, delete files & folders in-app |
| 👁 **Preview** | Built-in file viewer with line numbers and monospace rendering |
| 🌿 **Branches** | Switch branches instantly; full branch list auto-loaded per repo |
| 🎨 **Themes** | Toggle between a refined dark and a clean light theme |
| 🔒 **Auth** | Secure token entry with show/hide toggle; token saved locally |
| ℹ️ **About** | Built-in about panel with developer info and LinkedIn link |

---

## 🖥️ Screenshots

> *Dark theme — Explorer tab with file tree, action sidebar, and breadcrumb navigation*

---

## 🚀 Getting Started

### Prerequisites

```bash
pip install requests
```

> GitView uses only `tkinter` (standard library) and `requests`. No other dependencies required.

### Run

```bash
python gitview.py
```

### Connecting to GitHub

1. Go to **GitHub** → **Settings** → **Developer settings** → **Personal access tokens**
2. Click **"Generate new token (classic)"**
3. Select scope: ✅ `repo` (full control of repositories)
4. Copy the generated token
5. Paste it into GitView's token field and click **⚡ Connect**

> Your token is saved locally to `~/.gitview_config.json` and loaded automatically on next launch.

---

## 📖 Usage

### Navigating

- Select a repository from the dropdown at the top
- Choose a branch from the branch selector
- **Double-click** folders to enter them
- Click **⌂** to return to root, **↑** to go one level up
- Click any segment in the **breadcrumb** to jump directly to that level
- Type in the **search box** to filter files in the current directory

### Downloading

| Action | How |
|---|---|
| Single file | Select → **Download Selected** button or right-click |
| Multiple files | Multi-select → **Download Selected** |
| Folder | Select folder → **Download Selected** (recursive) |
| Entire repo | **Operations tab** → **Download Entire Repository** |
| Current folder | **Operations tab** → **Download Current Folder** |

### Uploading

| Action | How |
|---|---|
| Single file | **Upload File** button → choose file → enter commit message |
| Entire folder | **Upload Folder** button → choose local folder (recursive) |
| New file | **New File** button → enter name & optional content |
| New folder | **New Folder** button → enter name (creates a `.gitkeep`) |

### File Management

- **Preview**: Double-click any text file to open the built-in viewer
- **Rename**: Select a file → **Rename** button (creates new file, deletes old)
- **Delete**: Select a file → **Delete** button (permanent, with confirmation)
- **Copy Path**: Copies the relative path to clipboard
- **Open in Web**: Opens the current path on `github.com`

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Enter` | Connect with entered token |
| `Double-click` | Enter folder / preview file |
| `Right-click` | Open context menu |

---
<img width="1917" height="1013" alt="image" src="https://github.com/user-attachments/assets/182db4ce-32a2-4af8-a4bf-99d7b22dc600" />


## 🏗️ Architecture

```
gitview.py
├── Design System        # DARK / LIGHT color palettes, font constants
├── Helpers              # fmt_size(), file_icon()
├── Tooltip              # Hover tooltip widget
├── make_btn()           # Styled button factory with hover effects
└── GitView              # Main application class
    ├── _apply_styles()  # ttk style configuration
    ├── _build_ui()      # Top-level UI construction
    │   ├── Title bar    # Branding, theme toggle, help
    │   ├── Auth bar     # Token entry, connect/disconnect, user card
    │   ├── Notebook     # Explorer / Operations / About tabs
    │   └── Status bar   # Live status, clock, repo count
    ├── Auth methods     # _connect(), _disconnect(), token save/load
    ├── Repo methods     # _load_repos(), _on_repo_select(), branches
    ├── Navigation       # _load_dir(), _populate_tree(), breadcrumb
    ├── Preview          # _preview_selected(), _show_preview()
    ├── Downloads        # _download_*() methods
    ├── Uploads          # _upload_file(), _upload_folder()
    ├── CRUD             # _create_file/folder(), _delete(), _rename()
    └── Utilities        # _copy_path(), _open_in_browser(), help dialog
```

---

## 🔧 Configuration

GitView stores your token in `~/.gitview_config.json`:

```json
{
  "token": "ghp_your_token_here",
  "saved_by": "GitView"
}
```

To clear saved credentials, click **✕ Disconnect** inside the app, or delete the file manually.

---

## 📋 Requirements

- Python **3.8** or newer
- `tkinter` (bundled with most Python distributions)
- `requests` library (`pip install requests`)
- GitHub **Personal Access Token** with `repo` scope

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Developer

<table>
<tr>
<td align="center">
<b>Ali Essam</b><br/>
🇪🇬 Egypt<br/>
<a href="https://www.linkedin.com/in/dragonked2">
  <img src="https://img.shields.io/badge/LinkedIn-dragonked2-0a66c2?style=flat&logo=linkedin" />
</a>
</td>
</tr>
</table>

---

<div align="center">

Built with ❤️ in Egypt

**⬡ GitView** — making GitHub accessible from your desktop

</div>
