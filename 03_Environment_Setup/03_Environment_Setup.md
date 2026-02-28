# 03 — Environment Setup

> **Phase:** 1 — Foundations
> **Covers:** VS Code, Python, uv, Node.js/npm/npx, Claude Desktop, GitHub, API Keys

---

## Table of Contents

1. [Claude Subscription vs API Key — Read This First](#1-claude-subscription-vs-api-key--read-this-first)
2. [What You Need and Why](#2-what-you-need-and-why)
3. [VS Code](#3-vs-code)
4. [Python](#4-python)
5. [uv — Python Package Manager](#5-uv--python-package-manager)
6. [Node.js, npm, and npx](#6-nodejs-npm-and-npx)
7. [Claude Desktop](#7-claude-desktop)
8. [GitHub Account](#8-github-account)
9. [API Keys](#9-api-keys)
10. [Verify Everything Works](#10-verify-everything-works)
11. [Quick Reference](#11-quick-reference)

---

## 1. Claude Subscription vs API Key — Read This First

This is a common confusion. Here is the exact difference:

```
CLAUDE SUBSCRIPTION (claude.ai Pro/Max)
  What it is:  A monthly plan to USE Claude via web/app
  Cost:        $20/month (Pro) or $100/month (Max)
  Gives you:   Claude Desktop app + web access
  API access:  NO — subscription does not include API

ANTHROPIC API KEY
  What it is:  Programmatic access to Claude via code
  Cost:        Pay per token (separate billing from subscription)
  Gives you:   Call Claude from your own programs/scripts
  For MCP:     Only needed if YOU are building an MCP HOST app
```

### For Learning MCP — What do YOU need?

Since you have a **Claude subscription**, here is what applies to you:

| Task | Need API Key? | Your Subscription Works? |
|------|--------------|--------------------------|
| Run MCP servers and test with Claude Desktop | NO | YES |
| Build and test MCP tools/resources/prompts | NO | YES |
| Connect Claude Desktop to custom MCP servers | NO | YES |
| Build your own AI app that calls Claude API | YES | NO |
| Use OpenAI or Gemini models in your code | YES (theirs) | NO |

**Bottom line:** For everything in this MCP learning roadmap up to Phase 5,
your Claude subscription + Claude Desktop is all you need.
You do not need an Anthropic API key to build and test MCP servers.

> API keys (Section 9) are covered for completeness — you will need them
> later when integrating with OpenAI, Gemini, or building production apps.

---

## 2. What You Need and Why

| Tool | Why You Need It |
|------|----------------|
| **VS Code** | Code editor — write your MCP servers here |
| **Python 3.10+** | Primary language for building MCP servers with FastMCP |
| **uv** | Fast Python package manager — installs dependencies, manages virtual envs |
| **Node.js / npm / npx** | Runs JavaScript-based MCP servers (many official servers are JS) |
| **Claude Desktop** | MCP Host app — connects to your MCP servers and lets you test them |
| **GitHub Account** | Clone MCP server repos, manage your own server code |
| **API Keys** | Optional for now — needed later for OpenAI, Gemini, or Anthropic API |

---

## 3. VS Code

> **Official docs:** https://code.visualstudio.com/docs/setup/setup-overview

VS Code is the recommended editor for MCP development. Lightweight, free, and has excellent Python support.

---

### Windows

1. Go to https://code.visualstudio.com
2. Click **Download for Windows**
3. Run the downloaded `.exe` installer
4. During install, check these options:
   - Add "Open with Code" action to Windows Explorer
   - Register Code as an editor for supported file types
   - Add to PATH
5. Launch VS Code after install

```powershell
# Or install via winget (Windows Package Manager)
winget install Microsoft.VisualStudioCode
```

---

### macOS

```bash
# Option 1: Download from website
# Go to https://code.visualstudio.com → Download for macOS
# Open the .zip → drag "Visual Studio Code.app" to /Applications

# Option 2: Homebrew (recommended if you have it)
brew install --cask visual-studio-code
```

After install, open VS Code, press `Cmd+Shift+P` → type `shell command` → select
**"Shell Command: Install 'code' command in PATH"**
so you can open VS Code from the terminal with `code .`

---

### Linux (Ubuntu/Debian)

```bash
# Option 1: Official .deb package (recommended)
sudo apt update
sudo apt install wget gpg

wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg

echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] \
  https://packages.microsoft.com/repos/code stable main" | \
  sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null

sudo apt update
sudo apt install code

# Option 2: Snap
sudo snap install code --classic
```

### Linux (Fedora/RHEL)

```bash
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc

sudo tee /etc/yum.repos.d/vscode.repo << 'EOF'
[code]
name=Visual Studio Code
baseurl=https://packages.microsoft.com/yumrepos/vscode
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc
EOF

sudo dnf install code
```

### Verify VS Code

```bash
code --version
```

### Recommended VS Code Extensions for MCP

Install these after VS Code is set up:

| Extension | ID | Purpose |
|-----------|----|---------|
| Python | `ms-python.python` | Python language support |
| Pylance | `ms-python.vscode-pylance` | Python type checking |
| Ruff | `charliermarsh.ruff` | Python linter/formatter |

Install via terminal:
```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension charliermarsh.ruff
```

---

## 4. Python

> **Official docs:** https://www.python.org/downloads/
> **MCP requires Python 3.10 or higher**

---

### Windows

```powershell
# Option 1: Official installer
# Go to https://www.python.org/downloads/
# Download latest Python 3.x for Windows (e.g. python-3.12.x-amd64.exe)
# Run installer → CHECK "Add Python to PATH" → Install Now

# Option 2: Microsoft Store (easiest)
# Open Microsoft Store → search "Python 3.12" → Install

# Option 3: winget
winget install Python.Python.3.12
```

> **Important on Windows:** During install, tick **"Add python.exe to PATH"** before clicking Install.

---

### macOS

```bash
# Option 1: Official installer
# Go to https://www.python.org/downloads/
# Download macOS Universal installer → run the .pkg file

# Option 2: Homebrew (recommended)
brew install python@3.12

# Option 3: pyenv (if you need multiple Python versions)
brew install pyenv
pyenv install 3.12
pyenv global 3.12
```

---

### Linux (Ubuntu/Debian)

```bash
# Ubuntu 22.04+ ships with Python 3.10+ already
python3 --version

# If you need a specific version
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev

# Set as default (optional)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
```

### Linux (Fedora/RHEL)

```bash
sudo dnf install python3.12
```

### Verify Python

```bash
python3 --version      # Linux/macOS
python --version       # Windows
```

Expected output: `Python 3.12.x` (anything 3.10+ is fine)

> **Note:** In this roadmap we will mostly use `uv` to manage Python versions and
> virtual environments — so if the system Python is a bit old, `uv` will handle it.

---

## 5. uv — Python Package Manager

> **Official docs:** https://docs.astral.sh/uv/getting-started/installation/

`uv` is a very fast Python package and project manager written in Rust.
For MCP development it replaces `pip`, `venv`, and `pip-tools` in one tool.

Why uv for MCP:
- 10-100x faster than pip
- Creates and manages virtual environments automatically
- Installs Python versions itself — no need for pyenv
- Used in most modern MCP server examples

---

### Windows

```powershell
# Option 1: Standalone installer (recommended)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Option 2: winget
winget install --id=astral-sh.uv -e

# Option 3: Scoop
scoop install main/uv
```

Restart your terminal after install.

---

### macOS

```bash
# Option 1: Standalone installer (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Option 2: Homebrew
brew install uv
```

Restart your terminal, or run:
```bash
source $HOME/.local/bin/env
```

---

### Linux

```bash
# Option 1: Standalone installer (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Option 2: wget (if curl is not available)
wget -qO- https://astral.sh/uv/install.sh | sh
```

Restart your terminal, or run:
```bash
source $HOME/.local/bin/env
```

---

### Verify uv

```bash
uv --version
```

### Keep uv updated

```bash
uv self update
```

### Key uv commands you will use for MCP

```bash
# Create a new MCP server project
uv init my-mcp-server
cd my-mcp-server

# Add MCP dependencies
uv add fastmcp

# Run your server
uv run python server.py

# Create a virtual environment manually (if needed)
uv venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

---

## 6. Node.js, npm, and npx

> **Official docs:** https://nodejs.org/en/download
> **Recommended version:** LTS (Long-Term Support) — currently v22.x

Many official MCP servers (especially Anthropic's reference servers) are written in
JavaScript/TypeScript and run via `npx`. You need Node.js to use them.

- **npm** — Node Package Manager (installs with Node.js automatically)
- **npx** — Node Package Execute (runs packages without installing them globally)

---

### Windows

```powershell
# Option 1: Official installer
# Go to https://nodejs.org/en/download
# Download "Windows Installer (.msi)" — choose LTS
# Run the installer — npm is included automatically

# Option 2: winget
winget install OpenJS.NodeJS.LTS

# Option 3: Chocolatey
choco install nodejs-lts
```

---

### macOS

```bash
# Option 1: Homebrew (recommended)
brew install node@22
brew link node@22

# Option 2: Official installer
# Go to https://nodejs.org/en/download → macOS Installer → run .pkg

# Option 3: nvm (if you need multiple Node versions)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc    # or ~/.zshrc
nvm install --lts
nvm use --lts
```

---

### Linux (Ubuntu/Debian)

```bash
# Option 1: NodeSource repository (recommended — gets latest LTS)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs

# Option 2: nvm (works on any Linux distro)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install --lts
nvm use --lts
```

### Linux (Fedora/RHEL)

```bash
sudo dnf install nodejs npm
```

### Verify Node.js

```bash
node --version    # e.g. v22.14.0
npm --version     # e.g. 10.x.x
npx --version     # same as npm version
```

### Why npx matters for MCP

Many MCP servers can be run directly without installing them:

```bash
# Run the official filesystem MCP server without installing it globally
npx -y @modelcontextprotocol/server-filesystem /path/to/folder

# Run the official memory server
npx -y @modelcontextprotocol/server-memory
```

Claude Desktop config uses `npx` to launch these servers on demand — this is why
Node.js must be installed even if you write Python servers.

---

## 7. Claude Desktop

> **Official download:** https://claude.ai/download
> **Requires:** Claude Pro, Max, Team, or Enterprise subscription

Claude Desktop is your **MCP Host application**. It connects to MCP servers and lets
you talk to Claude while giving it access to your tools.

> **Linux note:** Claude Desktop officially supports **Windows and macOS only**.
> Linux users can use VS Code with the [Cline](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev)
> extension as an alternative MCP host.

---

### Windows

1. Go to https://claude.ai/download
2. Click **Download for Windows**
3. Run `ClaudeSetup.exe`
4. Claude installs and launches automatically
5. Sign in with your Claude account (the same account as your subscription)

```powershell
# Direct download link (x64)
# https://downloads.claude.ai/releases/win32/ClaudeSetup.exe
```

---

### macOS

1. Go to https://claude.ai/download
2. Click **Download for macOS**
3. Open the downloaded `.dmg` file
4. Drag **Claude** to your Applications folder
5. Open Claude from Applications
6. Sign in with your Claude account

---

### Connecting an MCP Server to Claude Desktop

After Claude Desktop is installed, you configure MCP servers by editing its config file:

**Windows config location:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS config location:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Example config** (filesystem server via npx):

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/yourname/Documents"
      ]
    }
  }
}
```

After editing, **restart Claude Desktop** — it will launch the MCP server and connect automatically.

---

## 8. GitHub Account

> **Official docs:** https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github

GitHub is where most MCP servers are published. You need an account to:
- Clone existing MCP server repositories
- Push your own MCP server code
- Contribute to open source MCP projects

---

### Create a GitHub Account (all platforms — web only)

1. Go to https://github.com
2. Click **Sign up**
3. Enter your email address
4. Create a password
5. Choose a username
6. Verify your email (GitHub sends a code)
7. Complete the setup questionnaire (optional)

---

### Install Git (command-line tool)

Git is separate from GitHub. You need it to clone and push repositories.

**Windows:**
```powershell
# Option 1: Official installer
# Download from https://git-scm.com/download/win → run installer

# Option 2: winget
winget install Git.Git
```

**macOS:**
```bash
# macOS ships with git via Xcode Command Line Tools
git --version   # if not installed, macOS will prompt you to install

# Or via Homebrew
brew install git
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install git
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install git
```

### Configure Git after install

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# Verify
git config --list
```

### Clone an MCP server repo (example)

```bash
# Clone the official MCP servers repository
git clone https://github.com/modelcontextprotocol/servers.git
cd servers
```

---

## 9. API Keys

> You do not need these right now if you are using Claude Desktop with your subscription.
> This section is for when you need to call AI models programmatically from your code.

---

### 9.1 Anthropic API Key (Claude)

> **Official console:** https://console.anthropic.com

1. Go to https://console.anthropic.com
2. Sign in (use a different account from claude.ai or same — they are linked)
3. Click **API Keys** in the left sidebar
4. Click **Create Key**
5. Give it a name (e.g. `mcp-dev`)
6. Copy the key — you will not see it again

```bash
# Set as environment variable (Linux/macOS)
export ANTHROPIC_API_KEY="sk-ant-..."

# Add to ~/.bashrc or ~/.zshrc to persist it
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Windows (permanently via System Properties)
setx ANTHROPIC_API_KEY "sk-ant-..."
```

> **Pricing note:** API usage is billed separately from your Claude subscription.
> Even if you have Pro/Max, you need to add a payment method to the Console separately.

---

### 9.2 OpenAI API Key

> **Official console:** https://platform.openai.com/api-keys

1. Go to https://platform.openai.com
2. Sign up or log in
3. Click **API keys** in the left sidebar
4. Click **Create new secret key**
5. Give it a name → click Create
6. Copy the key immediately

```bash
# Linux/macOS
export OPENAI_API_KEY="sk-..."

# Windows (PowerShell)
$env:OPENAI_API_KEY = "sk-..."
```

---

### 9.3 Google Gemini API Key

> **Official console:** https://aistudio.google.com/apikey

1. Go to https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click **Create API key**
4. Select an existing Google Cloud project or create one
5. Copy the generated key

```bash
# Linux/macOS
export GEMINI_API_KEY="AIza..."

# Windows (PowerShell)
$env:GEMINI_API_KEY = "AIza..."
```

---

### Storing API Keys Safely

Never hardcode API keys in your code. Use environment variables or a `.env` file:

```bash
# Create a .env file in your project root
touch .env
```

```ini
# .env  (add this file to .gitignore — never commit it)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
```

```python
# Load in Python using python-dotenv
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
```

```bash
# Install python-dotenv
uv add python-dotenv
```

---

## 10. Verify Everything Works

Run these commands one by one after completing all installations:

```bash
# 1. VS Code
code --version

# 2. Python
python3 --version        # Linux/macOS
python --version         # Windows

# 3. uv
uv --version

# 4. Node.js
node --version

# 5. npm
npm --version

# 6. npx
npx --version

# 7. Git
git --version
```

### Expected output (versions may differ — anything in range is fine)

```
VS Code:   1.9x.x
Python:    3.12.x  (3.10+ required)
uv:        0.5.x or higher
node:      v22.x.x  (v18+ acceptable)
npm:       10.x.x
npx:       10.x.x
git:       2.x.x
```

### Quick MCP smoke test

Once Claude Desktop is installed and running, test that it can connect to an MCP server:

1. Open `claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/tmp"
      ]
    }
  }
}
```

*(On Windows, use `C:\\Users\\YourName\\Documents` instead of `/tmp`)*

2. Restart Claude Desktop
3. In Claude Desktop, ask: **"List the files in /tmp"**
4. If Claude returns a file listing — your MCP setup is working

---

## 11. Quick Reference

### Installation commands — one place

| Tool | Windows | macOS | Linux |
|------|---------|-------|-------|
| **VS Code** | `winget install Microsoft.VisualStudioCode` | `brew install --cask visual-studio-code` | `sudo snap install code --classic` |
| **Python 3.12** | `winget install Python.Python.3.12` | `brew install python@3.12` | `sudo apt install python3.12` |
| **uv** | `powershell -c "irm https://astral.sh/uv/install.ps1 \| iex"` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Node.js LTS** | `winget install OpenJS.NodeJS.LTS` | `brew install node@22` | `curl -fsSL https://deb.nodesource.com/setup_lts.x \| sudo bash - && sudo apt install nodejs` |
| **Git** | `winget install Git.Git` | `brew install git` | `sudo apt install git` |
| **Claude Desktop** | Download `.exe` from claude.ai/download | Download `.dmg` from claude.ai/download | Not officially supported |

---

### Config file locations

| File | Windows | macOS |
|------|---------|-------|
| Claude Desktop config | `%APPDATA%\Claude\claude_desktop_config.json` | `~/Library/Application Support/Claude/claude_desktop_config.json` |

---

### Key decision — subscription vs API key

```
Testing MCP servers with Claude Desktop → use your Claude subscription
Building apps that call Claude in code  → need Anthropic API key (separate billing)
Using OpenAI or Gemini models in code   → need their API keys
```

---

## Official References

| Tool | Official URL |
|------|-------------|
| VS Code Setup | https://code.visualstudio.com/docs/setup/setup-overview |
| Python Downloads | https://www.python.org/downloads/ |
| uv Installation | https://docs.astral.sh/uv/getting-started/installation/ |
| Node.js Download | https://nodejs.org/en/download |
| Claude Desktop | https://claude.ai/download |
| MCP Quickstart (User) | https://modelcontextprotocol.io/quickstart/user |
| Anthropic Console | https://console.anthropic.com |
| OpenAI API Keys | https://platform.openai.com/api-keys |
| Gemini API Keys | https://aistudio.google.com/apikey |
| GitHub Signup | https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github |
| Git Downloads | https://git-scm.com/downloads |

---

*Next topic → `04_MCP_Host_Client_Server` — Deep dive into responsibilities, execution boundaries, and trust model.*
