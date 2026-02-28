# 04 — MCP Quickstart (Hands-On)

> **Phase:** 1 — Foundations + Phase 3 — Running MCP Servers
> **Style:** Hands-on — follow along and build

---

## Table of Contents

1. [Claude Desktop + Airbnb MCP Server](#1-claude-desktop--airbnb-mcp-server)
2. [Task 1 — Build a Basic MCP Server with a Hello World Tool](#2-task-1--build-a-basic-mcp-server-with-a-hello-world-tool)

---

## 1. Claude Desktop + Airbnb MCP Server

> **Goal:** Connect Claude Desktop to the Airbnb MCP server so Claude can search
> Airbnb listings and get property details — without writing a single line of code.
>
> **Repo:** https://github.com/openbnb-org/mcp-server-airbnb
> **npm package:** `@openbnb/mcp-server-airbnb`

---

### 1.1 What This Integration Does

The Airbnb MCP server exposes **two tools** to Claude:

| Tool | What it does |
|------|-------------|
| `airbnb_search` | Search listings by location, dates, guests, price range |
| `airbnb_listing_details` | Get full details of a listing — amenities, rules, coordinates, description |

Once connected, you can ask Claude things like:
- *"Find me a 2-bedroom Airbnb in Lisbon for 4 guests next weekend under $150/night"*
- *"Get the details of this Airbnb listing: [listing ID]"*

Claude will call the right tool, get the data, and respond — all automatically.

---

### 1.2 Architecture — How It All Fits Together

```
YOU (user)
    │
    │  Type a question in natural language
    ▼
┌─────────────────────────────────────────────────────┐
│              CLAUDE DESKTOP (Host)                  │
│                                                     │
│   Claude AI model reads your question and           │
│   decides which MCP tool to call                    │
│                                                     │
│   ┌──────────────────────────────────────────────┐  │
│   │         MCP Client (built into Desktop)      │  │
│   │  Sends tool call → receives result           │  │
│   └──────────────────┬───────────────────────────┘  │
└──────────────────────┼──────────────────────────────┘
                       │  STDIO transport
                       │  (Claude Desktop launches this as a child process)
                       ▼
┌─────────────────────────────────────────────────────┐
│         @openbnb/mcp-server-airbnb  (Server)        │
│         launched by: npx -y @openbnb/mcp-server-airbnb │
│                                                     │
│   Tool: airbnb_search         ──────────────────┐   │
│   Tool: airbnb_listing_details ─────────────────┤   │
└─────────────────────────────────────────────────┼───┘
                                                  │  HTTPS
                                                  ▼
                                        ┌──────────────────┐
                                        │  Airbnb Website  │
                                        │  (scrapes data)  │
                                        └──────────────────┘
```

**Key things to notice:**
- Claude Desktop talks to the MCP server over **STDIO** — it launches it as a background process using `npx`
- The MCP server talks to **Airbnb's website** over HTTPS to fetch listing data
- You never touch the Airbnb API directly — the MCP server handles everything
- When you close Claude Desktop, the MCP server process also closes

---

### 1.3 Prerequisites

Before starting, make sure these are installed (from Topic 03):

```bash
node --version    # v18+ required
npx --version     # comes with Node
```

Claude Desktop must also be installed and you must be signed in with your Claude account.

---

### 1.4 Step-by-Step Setup

#### Step 1 — Find the Claude Desktop config file

This is the JSON file where Claude Desktop reads its MCP server list.

**Windows:**
```
Press Win + R → type: %APPDATA%\Claude → press Enter
Open: claude_desktop_config.json
```
Or open it in VS Code directly:
```powershell
code $env:APPDATA\Claude\claude_desktop_config.json
```

**macOS:**
```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

> If the file does not exist yet, create it — Claude Desktop creates it on first launch.

---

#### Step 2 — Add the Airbnb MCP server config

Open `claude_desktop_config.json` and paste this:

```json
{
  "mcpServers": {
    "airbnb": {
      "command": "npx",
      "args": [
        "-y",
        "@openbnb/mcp-server-airbnb",
        "--ignore-robots-txt"
      ]
    }
  }
}
```

If you already have other servers in the file, add `airbnb` inside the existing
`mcpServers` block:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    },
    "airbnb": {
      "command": "npx",
      "args": [
        "-y",
        "@openbnb/mcp-server-airbnb",
        "--ignore-robots-txt"
      ]
    }
  }
}
```

Save the file.

---

#### Step 3 — Restart Claude Desktop

Fully quit Claude Desktop and reopen it.

**Windows:** Right-click the Claude icon in the system tray → Quit → Reopen
**macOS:** `Cmd+Q` to quit → reopen from Applications

Claude Desktop reads the config file **only on startup** — changes don't apply until you restart.

---

#### Step 4 — Verify the server is connected

In Claude Desktop, look for the **hammer icon** (🔨) near the chat input box.
Click it — you should see the Airbnb tools listed:

```
airbnb_search
airbnb_listing_details
```

If the tools appear, the server is connected and ready.

---

#### Step 5 — Test it

Type this in Claude Desktop:

```
Search for Airbnb listings in Barcelona for 2 guests, check-in July 10, check-out July 15
```

Claude will automatically call `airbnb_search` with those parameters and return matching listings.

---

### 1.5 The Config Block — Explained Line by Line

This is the config you pasted:

```json
{
  "mcpServers": {
    "airbnb": {
      "command": "npx",
      "args": [
        "-y",
        "@openbnb/mcp-server-airbnb",
        "--ignore-robots-txt"
      ]
    }
  }
}
```

Here is exactly what every part means:

---

#### `"mcpServers"` — the top-level key

```json
"mcpServers": { ... }
```

This tells Claude Desktop: *"here is the list of MCP servers you should connect to on startup."*
Each key inside is one server. You can have as many as you need.

---

#### `"airbnb"` — the server name (alias)

```json
"airbnb": { ... }
```

This is just a **label you choose** — it is how Claude Desktop identifies this server internally.
It does not have to match the package name. You could name it `"my-airbnb"` and it would still work.
This name also appears in Claude Desktop's UI when it shows connected tools.

---

#### `"command": "npx"` — how to launch the server

```json
"command": "npx"
```

This tells Claude Desktop **what program to run** to start the MCP server.
Claude Desktop will execute this command as a child process using STDIO transport.

`npx` is Node's package runner — it downloads and runs an npm package **without you having
to install it globally first**. So you never had to run `npm install` manually.

---

#### `"args"` — arguments passed to the command

```json
"args": [
  "-y",
  "@openbnb/mcp-server-airbnb",
  "--ignore-robots-txt"
]
```

These are the arguments Claude Desktop passes to `npx`. Let's break each one:

| Argument | What it does |
|----------|-------------|
| `"-y"` | Tells npx: *"yes, auto-install the package if not cached — do not prompt me"* |
| `"@openbnb/mcp-server-airbnb"` | The exact npm package name to run — this IS the MCP server |
| `"--ignore-robots-txt"` | A flag passed to the server itself (explained below) |

The full command Claude Desktop runs under the hood is:
```bash
npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt
```

---

#### `"--ignore-robots-txt"` — the most important flag to understand

Websites publish a file called `robots.txt` that tells bots and scrapers:
*"you are not allowed to access these URLs automatically."*

Airbnb's `robots.txt` restricts automated scraping of listing data.

```
Without this flag:   server respects robots.txt → may refuse to fetch some data
With this flag:      server bypasses robots.txt → fetches all listing data freely
```

**When to use it:**
- Learning and personal testing → `--ignore-robots-txt` is fine
- Production or commercial use → remove this flag and respect the restrictions

> This flag is the reason the server can actually return search results during testing.
> Without it, many requests would be blocked by the server's own compliance checks.

---

### 1.6 What Happens Behind the Scenes

When you type *"Find Airbnbs in Tokyo"* in Claude Desktop, here is the exact sequence:

```
1. You type the message and press Enter

2. Claude Desktop sends your message to the Claude AI model

3. Claude reads the message and checks its available tools:
   - airbnb_search   ← this matches the request
   - airbnb_listing_details

4. Claude decides to call airbnb_search with:
   {
     "location": "Tokyo",
     ... other params it infers from your message
   }

5. Claude Desktop's MCP Client sends the tool call to the running
   @openbnb/mcp-server-airbnb process via STDIO:
   { "method": "tools/call", "params": { "name": "airbnb_search", ... } }

6. The MCP server makes an HTTPS request to Airbnb's website,
   scrapes the search results

7. Server formats the results as JSON and sends back via STDIO

8. Claude Desktop receives the result and passes it to Claude

9. Claude reads the listing data and writes a natural language response to you

10. You see the results — without ever writing a line of code
```

---

### 1.7 Troubleshooting

| Problem | Likely cause | Fix |
|---------|-------------|-----|
| Hammer icon (🔨) not visible | Server didn't start | Check JSON syntax in config file — one missing comma breaks it |
| Tools not listed | Wrong package name | Make sure `@openbnb/mcp-server-airbnb` is spelled exactly right |
| "No results found" | robots.txt blocking | Add `--ignore-robots-txt` to args |
| `npx: command not found` | Node.js not installed | Install Node.js (see Topic 03, Section 6) |
| Config changes not applied | Didn't restart Claude | Fully quit and reopen Claude Desktop |
| JSON parse error in logs | Invalid JSON | Validate your config at https://jsonlint.com |

**Where to find Claude Desktop logs:**

```
Windows: %APPDATA%\Claude\logs\
macOS:   ~/Library/Logs/Claude/
```

---

### 1.8 Summary

| | Detail |
|--|--------|
| **What you built** | Claude Desktop connected to Airbnb MCP server |
| **Transport used** | STDIO — server runs as a local child process |
| **Tools available** | `airbnb_search`, `airbnb_listing_details` |
| **How server starts** | `npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt` |
| **Config location (Win)** | `%APPDATA%\Claude\claude_desktop_config.json` |
| **Config location (Mac)** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Code written** | None — config only |

---

## 2. Task 1 — Build a Basic MCP Server with a Hello World Tool

> **Goal:** Write your first MCP server in Python from scratch.
> It exposes one tool — `hello_world` — that Claude can call.
> You will run it two ways: via the **MCP Inspector** (browser UI) and via **Claude Desktop**.
>
> **File:** `04_MCP_Quickstart/task_01_hello_world/server.py`

---

### 2.1 What We're Building

```
YOU (user)
    │
    │  "Say hello to Deepak"
    ▼
┌─────────────────────────────────────────────┐
│           Claude Desktop (Host)             │
│  Claude decides to call → hello_world tool  │
│                                             │
│  ┌──────────────────────────────────────┐   │
│  │       MCP Client (built-in)          │   │
│  └──────────────┬───────────────────────┘   │
└─────────────────┼───────────────────────────┘
                  │  STDIO transport
                  ▼
┌─────────────────────────────────────────────┐
│        server.py  (our MCP server)          │
│                                             │
│   Tool: hello_world(name: str) -> str       │
└─────────────────────────────────────────────┘
```

---

### 2.2 Project Setup

All tasks in Topic 04 live inside the same `uv` project you already initialized.
Each task gets its own subfolder.

```
04_MCP_Quickstart/
├── 04_MCP_Quickstart.md
└── task_01_hello_world/
    └── server.py          ← you write this
```

---

### 2.3 Install the MCP Python SDK

From the project root (`D:\Study\MCP_Server`), run:

```bash
uv add "mcp[cli]"
```

**What this does:**

| Part | Meaning |
|------|---------|
| `mcp` | The core MCP Python SDK |
| `[cli]` | Adds CLI extras — includes `mcp dev` command and MCP Inspector support |

After this, `pyproject.toml` will show `mcp[cli]` in dependencies and
`.venv` will have the package installed.

Verify:

```bash
uv run mcp --version
```

---

### 2.4 Write the Server

**File:** `04_MCP_Quickstart/task_01_hello_world/server.py`

```python
from mcp.server.fastmcp import FastMCP

# Create the MCP server — the string is the server's display name
mcp = FastMCP("hello-world")


@mcp.tool()
def hello_world(name: str) -> str:
    """Say hello to someone by name."""
    return f"Hello, {name}! Welcome to MCP."


if __name__ == "__main__":
    mcp.run()
```

That is the complete server. Three things are happening here — explained in detail in section 2.8.

---

### 2.5 Run with MCP Inspector (Browser UI)

The **MCP Inspector** is a browser-based tool that lets you call your server's
tools manually — without needing Claude Desktop. Use it to test your server first.

Run:

```bash
uv run mcp dev 04_MCP_Quickstart/task_01_hello_world/server.py
```

Expected output:

```
Starting MCP inspector...
Proxy server listening on port 5173
Open http://localhost:5173 in your browser
```

Open `http://localhost:5173` in your browser.

**What you'll see:**

1. Left panel — **Tools** tab: shows `hello_world` is registered
2. Click `hello_world` → a form appears asking for `name` (string)
3. Enter `Deepak` → click **Run Tool**
4. Result panel shows:

```
Hello, Deepak! Welcome to MCP.
```

Press `Ctrl+C` in the terminal when done.

---

### 2.6 Connect to Claude Desktop

To use this server from Claude Desktop, add it to your config file.

**Windows config location:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

Open it (or create it if missing) and add the `hello-world` entry:

```json
{
  "mcpServers": {
    "hello-world": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "D:\\Study\\MCP_Server",
        "mcp",
        "run",
        "04_MCP_Quickstart/task_01_hello_world/server.py"
      ]
    }
  }
}
```

**Line-by-line explanation:**

| Key | Value | Why |
|-----|-------|-----|
| `"command"` | `"uv"` | Claude Desktop runs `uv` to launch the server |
| `"--directory"` | `D:\\Study\\MCP_Server` | Sets the working directory so uv finds the project's `.venv` |
| `"mcp"` | MCP CLI | The `mcp` command from our installed SDK |
| `"run"` | subcommand | Tells `mcp` to run a server file in STDIO mode |
| last arg | `server.py` path | Relative to `--directory` |

> **Why `uv run` instead of `python`?**
> `uv run` automatically uses the `.venv` inside your project — no need to
> manually activate it. Claude Desktop runs in its own context and doesn't
> inherit your terminal's activated environment.

Save the file, then **fully quit and reopen Claude Desktop**.

---

### 2.7 Test in Claude Desktop

After restarting Claude Desktop:

1. Click the **hammer icon** (🔨) near the chat input
2. You should see `hello_world` listed under `hello-world` server
3. Type in chat:

```
Say hello to Deepak using the hello_world tool
```

Claude will call the tool and respond:

```
Hello, Deepak! Welcome to MCP.
```

---

### 2.8 Code Walkthrough — Line by Line

```python
from mcp.server.fastmcp import FastMCP
```

Imports `FastMCP` — a high-level wrapper around the raw MCP server SDK.
It handles the JSON-RPC protocol, tool registration, and STDIO transport
for you so you don't have to write any of that manually.

---

```python
mcp = FastMCP("hello-world")
```

Creates the MCP server instance. The string `"hello-world"` is the **server name**
announced to the client during the initialization handshake. It's what appears in
Claude Desktop's tool panel header.

---

```python
@mcp.tool()
def hello_world(name: str) -> str:
    """Say hello to someone by name."""
    return f"Hello, {name}! Welcome to MCP."
```

The `@mcp.tool()` decorator does four things automatically:

| What it does | How |
|---|---|
| Registers the function as an MCP tool | Adds it to the server's tool list |
| Reads the function name | Tool is named `hello_world` |
| Reads the type hints | Builds a JSON schema: `name` is a required string |
| Reads the docstring | Sends it as the tool description to the LLM |

The LLM sees this tool as:
```json
{
  "name": "hello_world",
  "description": "Say hello to someone by name.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "name": { "type": "string" }
    },
    "required": ["name"]
  }
}
```

The description is what helps Claude decide **when** to call this tool.
Always write clear, specific docstrings.

---

```python
if __name__ == "__main__":
    mcp.run()
```

Starts the server in **STDIO mode** (the default).
The server reads JSON-RPC messages from `stdin` and writes responses to `stdout`.
When Claude Desktop launches this file as a child process, this is the entry point.

---

### 2.9 What Happens Under the Hood — Full Request Flow

When Claude calls `hello_world(name="Deepak")`:

```
1. Claude Desktop sends over STDIO:
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "tools/call",
     "params": {
       "name": "hello_world",
       "arguments": { "name": "Deepak" }
     }
   }

2. FastMCP receives this, finds the hello_world function, calls it:
   hello_world(name="Deepak")

3. Function returns:
   "Hello, Deepak! Welcome to MCP."

4. FastMCP wraps it and sends back over STDIO:
   {
     "jsonrpc": "2.0",
     "id": 1,
     "result": {
       "content": [
         { "type": "text", "text": "Hello, Deepak! Welcome to MCP." }
       ]
     }
   }

5. Claude reads the result and incorporates it into its response to you
```

---

### 2.10 Summary

| | Detail |
|--|--------|
| **What you built** | A Python MCP server with one tool |
| **SDK used** | `mcp[cli]` — installed via `uv add "mcp[cli]"` |
| **Tool** | `hello_world(name: str) -> str` |
| **Transport** | STDIO |
| **Test method 1** | `uv run mcp dev server.py` → MCP Inspector at `localhost:5173` |
| **Test method 2** | Claude Desktop with `uv run mcp run server.py` config |
| **Key concept** | `@mcp.tool()` reads type hints + docstring to auto-build tool schema |
| **Server file** | `04_MCP_Quickstart/task_01_hello_world/server.py` |

---

