# 02 — MCP Server

> **Phase:** 1 — Foundations + Phase 3 — Running MCP Servers
> **Covers syllabus topics:** 2 (Core Components → Server), 4 (Host vs Client vs Server), 9 (STDIO), 10 (Local HTTP), 11 (Remote HTTP), 12 (WebSocket)

---

## Table of Contents

1. [What is an MCP Server?](#1-what-is-an-mcp-server)
2. [The Problem It Solves](#2-the-problem-it-solves)
3. [What a Server Exposes](#3-what-a-server-exposes)
4. [Server Responsibilities](#4-server-responsibilities)
5. [Local vs Remote — The Big Picture](#5-local-vs-remote--the-big-picture)
6. [Transport 1 — STDIO (Local)](#6-transport-1--stdio-local)
7. [Transport 2 — HTTP + SSE (Remote)](#7-transport-2--http--sse-remote)
8. [Transport 3 — WebSocket (Real-Time Remote)](#8-transport-3--websocket-real-time-remote)
9. [Choosing the Right Transport](#9-choosing-the-right-transport)
10. [FastMCP vs Low-Level Server](#10-fastmcp-vs-low-level-server)
11. [MCP Server Primitives — Deep Dive](#11-mcp-server-primitives--deep-dive)
12. [Quick Recap](#12-quick-recap)

---

## 1. What is an MCP Server?

An **MCP Server** is a program that gives an AI model access to the outside world.

By itself, an AI model only knows what it was trained on. It cannot read your files, check your database, or call your APIs. An MCP Server bridges that gap — it sits between the AI and your systems, and provides specific capabilities the AI can use.

### Simple analogy

Think of an AI model as a very smart person locked in a room with no internet and no phone.

An **MCP Server is the assistant standing outside the door** — the AI slides a note under the door asking for something ("get me the contents of file X"), the assistant goes and fetches it, and slides the answer back.

```
  AI Model                MCP Server           Your System
  ─────────               ──────────           ───────────
  "Read file notes.txt"  →  reads the file  →  notes.txt
                         ←  returns content ←
  uses content to answer user
```

---

## 2. The Problem It Solves

### Without an MCP Server

If you wanted to give an AI access to your filesystem, database, or API, you had to:

1. Write custom code inside your AI app
2. Handle the API calls yourself
3. Format the results for the AI yourself
4. Repeat this for every new tool you needed

Every AI application did this differently. Nothing was reusable.

```
App A  has its own filesystem code
App B  has its own filesystem code   ← same thing, built 3 times
App C  has its own filesystem code
```

### With an MCP Server

Write one **Filesystem MCP Server** → every MCP-compatible AI app can use it.

```
App A  ──┐
App B  ──┼──>  Filesystem MCP Server  ──>  your files
App C  ──┘
```

**One server. Reusable everywhere. No duplication.**

---

## 3. What a Server Exposes

An MCP Server can expose up to **three types of capabilities**:

---

### 3.1 Tools — Actions the AI can perform

A tool is a **function the AI calls to do something**.

```
Tool: read_file
  Input:  path (string)
  Action: reads the file at that path
  Output: file contents as text

Tool: run_sql
  Input:  query (string)
  Action: runs the SQL against your database
  Output: rows as JSON
```

- The **AI decides** when to call a tool
- The user sees a confirmation before the tool runs
- Tools are the most commonly used capability

---

### 3.2 Resources — Data the AI can read

A resource is **structured data the AI can access**, identified by a URI.

```
file:///home/user/config.yaml     → a config file
db://mydb/customers               → a database table
https://api.internal/status       → a live API response
```

- Read-only (AI reads, does not change)
- Useful for giving the AI background context
- The **Host app** controls what resources to expose

---

### 3.3 Prompts — Reusable templates

Pre-built prompt templates for repeated workflows.

```
Prompt: code_review
  Parameters: language, code
  Result: a structured review prompt sent to the AI

Prompt: summarise
  Parameters: document_text
  Result: a summarisation prompt
```

- The **user selects** which prompt to run
- Saves writing the same complex prompts every time

---

## 4. Server Responsibilities

An MCP Server is responsible for exactly these things — nothing more, nothing less:

| Responsibility | Description |
|---------------|-------------|
| **Register capabilities** | Tell the Client what tools, resources, and prompts it has |
| **Execute tool calls** | Run the requested function when called by the Client |
| **Serve resources** | Return data when the Client asks for a resource URI |
| **Return results** | Send back structured responses the AI can understand |
| **Handle errors** | Return clean error messages, not crashes |

### What the Server does NOT do

- It does **not** know who the user is
- It does **not** store conversation history
- It does **not** directly talk to the AI model
- It does **not** decide when to run a tool — that is the AI's job

> A good MCP Server does one job well and stays out of everything else.

---

## 5. Local vs Remote — The Big Picture

This is one of the most important things to understand about MCP Servers.

A server can run in two places:

```
LOCAL SERVER                          REMOTE SERVER
─────────────────────────             ──────────────────────────────
Runs on your own machine              Runs on a cloud server or VM
Only you can use it                   Multiple users can connect
Fast (no network delay)               Accessible from anywhere
Uses STDIO transport                  Uses HTTP+SSE or WebSocket
Examples: read files, run scripts     Examples: cloud APIs, shared DBs
```

The **transport** is the communication method the Client uses to talk to the Server. There are three:

| Transport | Where Server Runs | Best For |
|-----------|------------------|----------|
| **STDIO** | Local (same machine) | Simple local tools |
| **HTTP + SSE** | Remote (any machine) | Cloud services, shared tools |
| **WebSocket** | Remote (real-time) | Streaming, live updates |

---

## 6. Transport 1 — STDIO (Local)

### What is STDIO?

STDIO stands for **Standard Input / Output**. It is the simplest way for two programs on the same machine to communicate — by passing text through stdin and stdout pipes.

### How it works

1. The MCP Client (inside the Host app) **launches the Server as a child process**
2. Client sends messages by writing to the Server's **stdin**
3. Server sends messages back by writing to **stdout**
4. When the Client closes, the Server process also closes

```
HOST MACHINE
┌─────────────────────────────────────────────┐
│                                             │
│  ┌──────────┐   stdin    ┌──────────────┐  │
│  │  Client  │ ─────────> │  MCP Server  │  │
│  │          │ <───────── │  (Process)   │  │
│  └──────────┘   stdout   └──────────────┘  │
│                                             │
└─────────────────────────────────────────────┘
```

### Practical example

When you configure Claude Desktop to use a filesystem server, the config looks like this:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/docs"]
    }
  }
}
```

Claude Desktop runs that `npx` command, launching the Server as a child process, and communicates with it over STDIO.

### Pros and Cons

| Pros | Cons |
|------|------|
| Dead simple to set up | Only works on the same machine |
| Fast — no network overhead | Not shareable across users |
| No ports, no firewall rules | Server dies when Client closes |
| Great for local dev and testing | One Client per Server instance |

### When to use STDIO

- Reading/writing local files
- Running local scripts or CLI tools
- Querying a local database (SQLite)
- Development and testing of new MCP Servers

---

## 7. Transport 2 — HTTP + SSE (Remote)

### What is HTTP + SSE?

- **HTTP POST** — the Client sends requests to the Server over normal HTTP
- **SSE (Server-Sent Events)** — the Server streams responses back to the Client over a persistent HTTP connection

This is a **one-direction stream** from server to client (SSE), combined with normal HTTP for client-to-server messages.

### How it works

```
CLIENT MACHINE                          REMOTE SERVER
┌─────────────┐                        ┌──────────────────────┐
│             │  HTTP POST /message    │                      │
│   Client    │ ──────────────────────>│   MCP Server         │
│             │                        │   (always running)   │
│             │ <──────────────────────│                      │
│             │  SSE stream /events    │                      │
└─────────────┘                        └──────────────────────┘
     any machine                            cloud / VM / server
```

### Step-by-step flow

```
1. Client connects to the Server's SSE endpoint
   GET https://myserver.com/events

2. Server keeps that connection open — this is the response channel

3. When Client wants to call a tool:
   POST https://myserver.com/message
   Body: { "method": "tools/call", "params": { ... } }

4. Server processes it and sends the result back via the SSE stream
   data: { "result": "file contents here" }
```

### Practical example

A team deploys a shared Postgres MCP Server on a VM. Any developer with Claude Desktop can connect to it:

```json
{
  "mcpServers": {
    "postgres": {
      "url": "https://mcp.mycompany.com/postgres"
    }
  }
}
```

No installation needed on the developer's machine — the Server is already running remotely.

### Pros and Cons

| Pros | Cons |
|------|------|
| Accessible from any machine | More setup (server, domain, TLS) |
| Multiple Clients can share one Server | SSE is one-directional (Client can't push data back easily) |
| Server runs independently and persistently | Slightly more latency than STDIO |
| Works through firewalls and proxies | Need to handle auth, security |

### When to use HTTP + SSE

- Connecting to cloud services (Slack, GitHub, Notion)
- Sharing a tool with your team (shared DB server)
- Deploying MCP Servers on VMs or Kubernetes
- Any tool that needs to be accessible remotely

---

## 8. Transport 3 — WebSocket (Real-Time Remote)

### What is WebSocket?

WebSocket is a **full-duplex** (two-way) communication channel over a single persistent connection. Unlike HTTP+SSE where the Client sends HTTP POST and Server streams back via SSE, with WebSocket **both sides can send messages at any time**.

```
CLIENT                              SERVER
  │                                   │
  │──── WebSocket Handshake ─────────>│
  │<─── Connection Established ───────│
  │                                   │
  │──── tool call ──────────────────> │  ← Client can send anytime
  │<─── result ──────────────────────│  ← Server can send anytime
  │<─── progress update ─────────────│  ← Server can push mid-stream
  │──── another request ────────────> │
  │                                   │
  (connection stays open)
```

### How it differs from HTTP + SSE

| Feature | HTTP + SSE | WebSocket |
|---------|-----------|-----------|
| Communication | Client POST → Server SSE stream | Fully two-way |
| Connection | New HTTP request per call | One persistent connection |
| Server can push anytime | Yes (via SSE) | Yes (natively) |
| Streaming mid-response | Limited | Natural |
| Complexity | Simpler | Slightly more complex |

### When to use WebSocket

- **Long-running tools** — e.g., "run this build and stream logs back"
- **Real-time tools** — e.g., "watch this file and notify when it changes"
- **Streaming responses** — e.g., "run kubectl logs -f and stream output"
- Any tool where the Server needs to push **multiple updates** over time

### Practical example

```
User: "Stream logs from the production pod"

Client ──WebSocket──> MCP Server

Server starts kubectl logs -f and pushes each log line
as it arrives back to the Client:

  data: "[10:01:01] Request received"
  data: "[10:01:02] Processing..."
  data: "[10:01:03] Done"
  data: "[10:01:05] New request received"
  ...
```

This is impossible with normal HTTP (which closes after one response) and awkward with SSE. WebSocket makes it natural.

---

## 9. Choosing the Right Transport

Use this decision tree when setting up an MCP Server:

```
Is the server running on the same machine as the Client?
│
├── YES → Use STDIO
│         Simple. Fast. No networking needed.
│         Best for: local files, scripts, SQLite
│
└── NO → Does the tool need real-time streaming or push updates?
          │
          ├── YES → Use WebSocket
          │         Best for: log streaming, live monitoring,
          │         long-running commands
          │
          └── NO → Use HTTP + SSE
                    Best for: cloud APIs, shared team tools,
                    REST-based integrations
```

### Summary table

| I want to... | Use |
|-------------|-----|
| Read files from my own machine | STDIO |
| Query a local SQLite DB | STDIO |
| Run a local Python script | STDIO |
| Connect to a company-shared Postgres server | HTTP + SSE |
| Access a cloud API (Slack, GitHub) | HTTP + SSE |
| Stream Kubernetes logs live | WebSocket |
| Watch a file for changes in real time | WebSocket |
| Build and share a team tool on a VM | HTTP + SSE |

---

## 10. FastMCP vs Low-Level Server

When you actually **build** an MCP Server in Python, you have two ways to do it:

| Approach | What it is |
|----------|-----------|
| **FastMCP** | A high-level framework — simple decorators, minimal boilerplate |
| **Low-Level SDK** | Direct use of the MCP SDK — full control, more code |

---

### 10.1 The Problem FastMCP Solves

Building a server with the raw MCP SDK means you have to manually:

- Register every tool with its full JSON schema
- Write handlers for `list_tools`, `call_tool`, `list_resources`, etc.
- Handle async streams and protocol details yourself

It works, but it is verbose. For every tool, you write a lot of plumbing code.

**FastMCP wraps all of that away.** You write a Python function, slap a decorator on it, and it is a tool. Done.

> FastMCP is to MCP what FastAPI is to building HTTP APIs — same power, far less ceremony.

---

### 10.2 Building the Same Tool — Side by Side

Let's build one tool: `read_file(path)` — reads a file and returns its content.

---

#### With FastMCP (High-Level)

```python
from fastmcp import FastMCP

mcp = FastMCP("file-server")

@mcp.tool()
def read_file(path: str) -> str:
    """Read a file and return its contents."""
    with open(path) as f:
        return f.read()

if __name__ == "__main__":
    mcp.run()   # defaults to STDIO transport
```

That is the entire server. FastMCP handles:
- Generating the JSON schema from the type hints (`path: str`)
- Using the docstring as the tool description
- Registering the tool with the protocol
- Running the event loop and transport

---

#### With Low-Level SDK (Low-Level)

```python
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

server = Server("file-server")

# Step 1: tell the Client what tools exist
@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="read_file",
            description="Read a file and return its contents.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to read"
                    }
                },
                "required": ["path"]
            }
        )
    ]

# Step 2: handle when the AI actually calls the tool
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "read_file":
        with open(arguments["path"]) as f:
            content = f.read()
        return [types.TextContent(type="text", text=content)]
    raise ValueError(f"Unknown tool: {name}")

# Step 3: wire up the transport and run
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

Same result. Much more code. You are writing the plumbing yourself.

---

### 10.3 What FastMCP Does Automatically

| Thing you need | FastMCP | Low-Level SDK |
|----------------|---------|---------------|
| Tool JSON schema | Auto-generated from type hints | You write it manually |
| Tool description | Taken from docstring | You write it manually |
| `list_tools` handler | Built-in | You write it |
| `call_tool` router | Built-in | You write the if/else |
| Async event loop | `mcp.run()` handles it | You wire it yourself |
| Transport setup | `mcp.run()` handles it | You set up streams manually |
| Error handling | Sensible defaults | You implement it |

---

### 10.4 FastMCP — More Features

FastMCP supports all three capability types using simple decorators:

```python
from fastmcp import FastMCP

mcp = FastMCP("my-server")

# --- Tool ---
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

# --- Resource ---
@mcp.resource("file://config")
def get_config() -> str:
    """Return the app config."""
    return open("config.yaml").read()

# --- Prompt ---
@mcp.prompt()
def code_review(language: str, code: str) -> str:
    """Generate a code review prompt."""
    return f"Review this {language} code for bugs:\n\n{code}"

if __name__ == "__main__":
    mcp.run()
```

Three decorators. Three capabilities. No protocol knowledge needed.

---

### 10.5 Running FastMCP on Different Transports

FastMCP makes switching transport trivial:

```python
# STDIO — default, for local tools
mcp.run()
mcp.run(transport="stdio")

# HTTP + SSE — for remote / shared tools
mcp.run(transport="sse", host="0.0.0.0", port=8000)
```

With the low-level SDK you would need to import a different transport module,
set up the Starlette/ASGI app, configure the SSE handler — several more steps.

---

### 10.6 When to Use Which

```
Are you building a new server for a standard use case?
│
└── YES → Use FastMCP
          Fast, clean, readable code
          Handles 95% of real-world MCP servers

Are you building something with custom protocol behaviour?
(custom capability negotiation, non-standard message routing,
 building a framework on top of MCP itself)
│
└── YES → Use the Low-Level SDK
          Full control over every message
          More code, but nothing is hidden from you
```

| Use FastMCP when... | Use Low-Level SDK when... |
|--------------------|--------------------------|
| Building tools for files, DBs, APIs | Building a framework on top of MCP |
| You want to ship quickly | You need custom protocol handling |
| Your team needs readable code | You are implementing MCP itself |
| Learning MCP — start here | You need behaviour FastMCP does not support |

---

### 10.7 Summary

```
FastMCP
  What:    High-level Python framework for building MCP Servers
  How:     Decorators (@mcp.tool, @mcp.resource, @mcp.prompt)
  Hides:   JSON schema generation, transport setup, protocol plumbing
  Use for: Almost everything — tools, resources, prompts

Low-Level SDK
  What:    Direct MCP SDK — you control every layer
  How:     Implement list_tools, call_tool, run handlers manually
  Exposes: Full protocol — nothing is hidden
  Use for: Custom protocol behaviour, framework authors
```

> **Start with FastMCP.** Move to the low-level SDK only when you hit a wall.

---

## 11. MCP Server Primitives — Deep Dive

A **primitive** is a building block — the smallest unit of capability a server can expose.
There are exactly **three primitives** in MCP:

```
┌─────────────────────────────────────────────────────────┐
│                   MCP SERVER                            │
│                                                         │
│   TOOLS          RESOURCES          PROMPTS             │
│   ──────         ─────────          ───────             │
│   AI calls       AI reads           User selects        │
│   to DO things   for CONTEXT        for TEMPLATES       │
└─────────────────────────────────────────────────────────┘
```

Each primitive has a different **controller** — the entity that decides when it is used:

| Primitive | Controlled by | Purpose |
|-----------|--------------|---------|
| **Tools** | The AI model | Execute actions, call functions |
| **Resources** | The Host application | Provide read-only data/context |
| **Prompts** | The User | Run reusable workflow templates |

---

### 11.1 Primitive 1 — Tools

#### What is a Tool?

A Tool is a **named function** with a defined input schema that the AI model can call to perform an action and get a result back.

Think of it like a remote function call:
- You define the function on the server
- The AI calls it by name, passing arguments
- The server runs it and returns the output

#### Anatomy of a Tool

Every tool has exactly three parts:

```
Tool
├── name         → identifier the AI uses to call it  (e.g. "read_file")
├── description  → plain English, tells the AI what this tool does
└── inputSchema  → JSON Schema describing the parameters
```

#### Tool Input Schema (JSON Schema)

The input schema is how the server tells the AI **what arguments to pass**.
It uses the JSON Schema standard:

```json
{
  "name": "read_file",
  "description": "Read the contents of a file from the filesystem.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Absolute or relative path to the file"
      },
      "encoding": {
        "type": "string",
        "description": "File encoding (default: utf-8)",
        "default": "utf-8"
      }
    },
    "required": ["path"]
  }
}
```

The AI reads this schema and knows:
- It must pass `path` (required, string)
- It can optionally pass `encoding` (string)

#### Tool Result Types

A tool can return different content types:

```
TextContent   → plain text string
              { "type": "text", "text": "file contents here" }

ImageContent  → base64-encoded image
              { "type": "image", "data": "...", "mimeType": "image/png" }

EmbeddedResource → a resource URI embedded in the result
              { "type": "resource", "resource": { "uri": "file:///..." } }
```

Most tools return `TextContent`. Image and embedded resources are for richer responses.

#### Tool Annotations

Annotations are **optional hints** that tell the Host how to handle a tool safely.
They do not change what the tool does — they just describe its behavior:

```json
{
  "name": "delete_file",
  "description": "Delete a file permanently.",
  "inputSchema": { ... },
  "annotations": {
    "title": "Delete File",
    "readOnlyHint": false,
    "destructiveHint": true,
    "idempotentHint": false,
    "openWorldHint": false
  }
}
```

| Annotation | Type | What it means |
|-----------|------|---------------|
| `title` | string | Human-friendly display name in the UI |
| `readOnlyHint` | bool | `true` = tool only reads, never writes (safe) |
| `destructiveHint` | bool | `true` = tool may delete or overwrite data |
| `idempotentHint` | bool | `true` = calling it multiple times is safe (same result) |
| `openWorldHint` | bool | `true` = tool talks to the external internet |

> These are **hints**, not enforced rules. The Host uses them to warn the user or ask for confirmation.

#### How the AI Decides to Call a Tool

The AI reads **the tool name + description** and matches it to the user's request.
This is why a good description matters more than the code itself:

```
BAD description:
  name: "rf"
  description: "runs the operation"
  → AI has no idea when to use this

GOOD description:
  name: "read_file"
  description: "Read the contents of a local file given its path.
                Use this when the user asks about a file on their computer."
  → AI knows exactly when to call this
```

#### Defining a Tool — FastMCP vs Low-Level

```python
# FastMCP — schema auto-generated from type hints + docstring
@mcp.tool()
def search_web(query: str, max_results: int = 5) -> str:
    """Search the web and return top results for a query."""
    return do_search(query, max_results)


# Low-Level SDK — everything written manually
@server.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="search_web",
            description="Search the web and return top results for a query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        )
    ]
```

#### Tool Error Handling

When a tool fails, it should return a structured error — not crash:

```python
# FastMCP handles this — raise an exception, it becomes a clean error response
@mcp.tool()
def read_file(path: str) -> str:
    """Read a file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path) as f:
        return f.read()
```

The Client receives a proper error message the AI can understand and report back to the user.

---

### 11.2 Primitive 2 — Resources

#### What is a Resource?

A Resource is a **piece of data** a server exposes that the AI (or Host) can read to gain context.

Unlike Tools (which DO things), Resources only PROVIDE data. They are read-only.

Think of resources as **files on a shared drive** — the AI can open and read them, but cannot edit them through the resource interface.

#### Resource URI

Every resource is identified by a **URI** — a unique address, just like a URL for a webpage:

```
file:///home/user/notes.txt          → a local file
db://myapp/users                     → a database table
config://app/settings                → app configuration
screen://current                     → current screen content
git://repo/main/README.md            → a file in a git repo
https://api.internal/health          → a live API response
```

The URI scheme (`file://`, `db://`, etc.) is defined by the server — there is no enforced standard beyond being a valid URI.

#### Anatomy of a Resource

```
Resource
├── uri          → unique address  (e.g. "file:///notes.txt")
├── name         → human-friendly label  (e.g. "My Notes")
├── description  → what this resource contains
├── mimeType     → content type  (e.g. "text/plain", "application/json")
└── content      → the actual data (text or binary)
```

#### Resource Content Types

```
TextResourceContents   → plain text, markdown, JSON, code, etc.
BinaryResourceContents → images, PDFs, audio — returned as base64
```

#### Static vs Dynamic Resources

```
STATIC RESOURCE
  Content is fixed / rarely changes
  Example: a config file, a README
  Listed directly by the server

  file:///app/config.yaml  →  always the same file


DYNAMIC RESOURCE
  Content changes based on real-time state
  Example: live database rows, current system status
  Server generates the content on each read

  db://myapp/orders  →  different rows every time you read it
```

#### Resource Templates

A Resource Template lets you expose a **pattern** of resources instead of listing each one:

```python
# Without template — you'd have to list every file individually:
file:///docs/intro.md
file:///docs/setup.md
file:///docs/api.md
...

# With template — one pattern covers all files:
file:///docs/{filename}   ← {filename} is the variable part
```

In FastMCP:

```python
@mcp.resource("file:///{path}")
def read_any_file(path: str) -> str:
    """Read any file by path."""
    with open(path) as f:
        return f.read()
```

Now the AI can read `file:///notes.txt`, `file:///config.yaml`, `file:///logs/app.log` — all from one template.

#### Resource Subscriptions

Resources support **subscriptions** — the server can notify the Client when a resource changes:

```
1. Client subscribes to:  file:///logs/app.log
2. Log file gets new entries
3. Server sends notification: "resource updated"
4. Client re-reads the resource to get fresh content
```

This is useful for live dashboards, file watchers, or real-time monitoring tools.

#### Defining a Resource — FastMCP vs Low-Level

```python
# FastMCP
@mcp.resource("db://users/all")
def get_all_users() -> str:
    """Return all users from the database as JSON."""
    users = db.query("SELECT * FROM users")
    return json.dumps(users)


# Low-Level SDK
@server.list_resources()
async def list_resources():
    return [
        types.Resource(
            uri="db://users/all",
            name="All Users",
            description="Return all users from the database as JSON.",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri: str):
    if uri == "db://users/all":
        users = db.query("SELECT * FROM users")
        return json.dumps(users)
```

---

### 11.3 Primitive 3 — Prompts

#### What is a Prompt?

A Prompt is a **pre-built, reusable template** that generates a structured message to send to the AI.

Instead of the user typing a complex prompt from scratch every time, they select a named prompt, fill in the parameters (like a form), and the server assembles the final message.

#### Anatomy of a Prompt

```
Prompt
├── name         → identifier  (e.g. "code_review")
├── description  → what this prompt does
└── arguments    → list of parameters the user fills in
    ├── name
    ├── description
    └── required (true/false)
```

#### How a Prompt Works — Step by Step

```
1. Server exposes a prompt called "code_review"

2. Client calls: prompts/list
   Server returns: [{ name: "code_review", description: "...", arguments: [...] }]

3. User sees "code_review" in the Host UI and selects it
   Fills in: language = "Python", code = "def foo(): ..."

4. Client calls: prompts/get  with those arguments

5. Server returns a fully assembled message:
   "Review this Python code for bugs and improvements:
    def foo(): ..."

6. This message is sent directly to the AI as the user's prompt
```

#### Prompt Messages

A prompt returns one or more **messages** — each message is either from the user or from the assistant:

```python
# FastMCP
@mcp.prompt()
def code_review(language: str, code: str) -> str:
    """Review code for bugs and style issues."""
    return f"Review this {language} code for bugs and style issues:\n\n{code}"


# Multi-message prompt (conversation-style)
@mcp.prompt()
def debug_session(error: str, code: str) -> list[dict]:
    return [
        {"role": "user",      "content": f"I have this error:\n{error}"},
        {"role": "assistant", "content": "Let me look at that. Can you share the code?"},
        {"role": "user",      "content": f"Here is the code:\n\n{code}"}
    ]
```

Multi-message prompts are useful for setting up a **conversation context** before the AI responds.

#### Embedded Resources in Prompts

A prompt can embed resource content directly into its message:

```python
@mcp.prompt()
def summarise_file(path: str) -> list[dict]:
    """Summarise the contents of a file."""
    return [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Please summarise this file:"},
                {"type": "resource", "resource": {"uri": f"file:///{path}"}}
            ]
        }
    ]
```

The Host automatically reads the resource and embeds its content into the prompt — so the AI gets both the instruction and the file content in one shot.

#### Defining a Prompt — FastMCP vs Low-Level

```python
# FastMCP — return a string or list of messages
@mcp.prompt()
def summarise(text: str, style: str = "bullet points") -> str:
    """Summarise text in the given style."""
    return f"Summarise the following as {style}:\n\n{text}"


# Low-Level SDK
@server.list_prompts()
async def list_prompts():
    return [
        types.Prompt(
            name="summarise",
            description="Summarise text in the given style.",
            arguments=[
                types.PromptArgument(name="text",  description="Text to summarise", required=True),
                types.PromptArgument(name="style", description="Output style",      required=False)
            ]
        )
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict):
    if name == "summarise":
        style = arguments.get("style", "bullet points")
        text  = arguments["text"]
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Summarise the following as {style}:\n\n{text}"
                    )
                )
            ]
        )
```

---

### 11.4 The Three Primitives Side by Side

```
                TOOLS              RESOURCES           PROMPTS
                ─────              ─────────           ───────
What it is      Function to call   Data to read        Template to run

Controlled by   AI model           Host application    User

When used       AI decides it      App decides what    User picks from
                needs to act       context to load     a list

Direction       Client → Server    Client → Server     Client → Server
                (request/response) (read)              (get assembled msg)

Can write?      YES                NO (read-only)      NO (generates prompt)

Return type     Text / Image /     Text / Binary       Messages (user/
                Embedded resource  resource content    assistant roles)

FastMCP         @mcp.tool()        @mcp.resource()     @mcp.prompt()
decorator
```

---

### 11.5 Primitives in a Real Server — Full Example

Here is a small but complete FastMCP server that uses all three primitives:

```python
from fastmcp import FastMCP
import json, os

mcp = FastMCP("notes-server")

NOTES_FILE = "notes.json"

# ── TOOL: add a note ──────────────────────────────────────
@mcp.tool()
def add_note(title: str, content: str) -> str:
    """Add a new note with a title and content."""
    notes = _load_notes()
    notes[title] = content
    _save_notes(notes)
    return f"Note '{title}' saved."

# ── TOOL: delete a note ───────────────────────────────────
@mcp.tool()
def delete_note(title: str) -> str:
    """Delete a note by title."""
    notes = _load_notes()
    if title not in notes:
        raise KeyError(f"Note '{title}' not found.")
    del notes[title]
    _save_notes(notes)
    return f"Note '{title}' deleted."

# ── RESOURCE: read all notes ──────────────────────────────
@mcp.resource("notes://all")
def get_all_notes() -> str:
    """Return all saved notes as JSON."""
    return json.dumps(_load_notes(), indent=2)

# ── RESOURCE TEMPLATE: read one note by title ─────────────
@mcp.resource("notes://{title}")
def get_note(title: str) -> str:
    """Return a single note by its title."""
    notes = _load_notes()
    if title not in notes:
        raise KeyError(f"Note '{title}' not found.")
    return notes[title]

# ── PROMPT: summarise all notes ───────────────────────────
@mcp.prompt()
def summarise_notes(style: str = "bullet points") -> str:
    """Generate a prompt to summarise all notes."""
    notes = _load_notes()
    notes_text = "\n\n".join(f"## {t}\n{c}" for t, c in notes.items())
    return f"Summarise these notes as {style}:\n\n{notes_text}"

# ── Helpers ───────────────────────────────────────────────
def _load_notes():
    if not os.path.exists(NOTES_FILE):
        return {}
    with open(NOTES_FILE) as f:
        return json.load(f)

def _save_notes(notes):
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=2)

if __name__ == "__main__":
    mcp.run()
```

What this server provides:

```
TOOLS      add_note(title, content)   → saves a note
           delete_note(title)         → removes a note

RESOURCES  notes://all                → all notes as JSON
           notes://{title}            → one note by title (template)

PROMPTS    summarise_notes(style)     → prompt to summarise all notes
```

---

### 11.6 Summary of Primitives

| | Tools | Resources | Prompts |
|--|-------|-----------|---------|
| **Do / Read / Template** | Do | Read | Template |
| **Who triggers it** | AI model | Host app | User |
| **Modifies data?** | Yes | No | No |
| **MCP method** | `tools/call` | `resources/read` | `prompts/get` |
| **FastMCP decorator** | `@mcp.tool()` | `@mcp.resource()` | `@mcp.prompt()` |
| **Key thing to write** | Good description | Clear URI | Useful template |

---

## 12. Quick Recap

### What is an MCP Server?

A program that **gives the AI access to your systems** by exposing Tools, Resources, and Prompts through a standard protocol.

### Why does it exist?

To replace **custom one-off integrations** with a **reusable, standard capability provider** that any MCP-compatible AI app can use.

### The three transports at a glance

```
STDIO
  Where:  Same machine as Client
  How:    stdin / stdout pipes
  Use:    Local files, scripts, dev/testing

HTTP + SSE
  Where:  Remote machine / cloud
  How:    HTTP POST (request) + SSE stream (response)
  Use:    Shared tools, cloud services, team deployments

WebSocket
  Where:  Remote machine / cloud
  How:    Persistent two-way connection
  Use:    Real-time streaming, long-running commands, live updates
```

### The one-liner

> An MCP Server is the plug you build once so the AI can work with your systems — regardless of whether those systems live on your laptop or in the cloud.

---

*Next topic → `03_JSON_RPC_in_MCP` — How Client and Server actually format their messages under the hood.*

