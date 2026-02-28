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
11. [Quick Recap](#11-quick-recap)

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

## 11. Quick Recap

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

