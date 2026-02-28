# 01 — MCP and Its Architecture

> **Phase:** 1 — Foundations
> **Covers syllabus topics:** 1 (What is MCP), 2 (Core Components), 3 (Architecture End-to-End Flow)

---

## Table of Contents

1. [What is MCP?](#1-what-is-mcp)
2. [The Problem MCP Solves](#2-the-problem-mcp-solves)
3. [Core Components](#3-core-components)
4. [Architecture — End-to-End Flow](#4-architecture--end-to-end-flow)
5. [How a Request Actually Works](#5-how-a-request-actually-works)
6. [Quick Recap](#6-quick-recap)

---

## 1. What is MCP?

**MCP stands for Model Context Protocol.**

It is an **open standard** (created by Anthropic in November 2024) that defines how an AI model can talk to external tools, files, databases, and services — in a structured and consistent way.

### Think of it like this:

Before MCP existed, imagine you wanted to connect different devices to your laptop. You'd need a different cable for each one — one for your phone, one for your hard drive, one for your monitor. It was messy.

Then USB-C came along. **One port. Works with everything.**

**MCP is the USB-C of AI.**
Instead of writing custom code to connect every AI app to every tool, MCP gives you one standard way to connect them all.

```
Without MCP:           With MCP:

AI App  --custom-->  File Tool        AI App
AI App  --custom-->  Database            |
AI App  --custom-->  Web API           MCP (one standard)
AI App  --custom-->  Slack               |
                                 File | DB | API | Slack
```

---

## 2. The Problem MCP Solves

### The Problem: AI was isolated

When you use an AI model like Claude or GPT, it knows a lot — but only from its training data. It cannot:

- Read a file on your computer
- Query your database
- Search the web in real time
- Send a message on Slack
- Check your Kubernetes pods

To make AI actually useful in real work, you need to connect it to external systems.

### The Old Way (Before MCP)

Every team wrote their own custom code to connect the AI to each tool. This meant:

| Problem | What It Meant |
|---------|---------------|
| **No standard** | Every integration was different |
| **Not reusable** | Code written for one AI app couldn't be used in another |
| **Hard to maintain** | N tools × M AI apps = N×M custom integrations |
| **Slow to build** | Rebuilding the same things over and over |

### The MCP Way

Write a tool as an **MCP Server** once → any MCP-compatible AI app can use it.

```
Before MCP:  5 AI apps × 10 tools = 50 custom integrations

With MCP:    5 AI apps + 10 MCP servers = 15 things to build
```

---

## 3. Core Components

MCP has **3 main components** and **3 capability types** you need to know.

---

### 3.1 The 3 Main Components

#### HOST

The application the **user directly interacts with**.

- Examples: Claude Desktop, Cursor, VS Code with an AI plugin
- It holds and runs one or more MCP Clients
- It is responsible for user interface, security, and approvals

> Think of the Host as the **browser** — the thing you open and use.

---

#### CLIENT

Lives **inside the Host**. Manages the connection to one MCP Server.

- One Client ↔ One Server (always a 1-to-1 relationship)
- Sends requests to the server (tool calls, resource reads)
- Receives and passes results back to the AI

> Think of the Client as a **tab in the browser** — it's the thing that actually communicates with a website (server).

---

#### SERVER

A **separate, lightweight program** that provides capabilities to the AI.

- You can build your own or use community-built ones
- It exposes: Tools, Resources, and/or Prompts
- It runs either locally (on your machine) or remotely (on a server)
- It does NOT know anything about the user — it just handles requests

> Think of the Server as the **website** (or backend API) that the browser tab talks to.

---

### 3.2 The 3 Capability Types

These are the three things an MCP Server can expose:

#### TOOLS — Things the AI can DO

Functions the AI can call to perform actions.

```
Examples:
  - read_file(path)           → reads a file
  - run_sql_query(query)      → queries a database
  - search_web(query)         → searches the internet
  - create_github_issue(...)  → opens a GitHub issue
  - send_email(to, body)      → sends an email
```

- The **AI decides** when to call a tool
- User must approve before the tool actually runs
- Returns a result the AI uses to form its answer

---

#### RESOURCES — Data the AI can READ

Static or dynamic data the AI can access for context.

```
Examples:
  - file:///home/user/notes.txt     → a local file
  - db://mydb/users                 → a database table
  - https://api.example.com/config  → a remote API response
```

- The **Host/App decides** what to expose as a resource
- Read-only (AI reads, doesn't modify)
- Gives the AI real-world context to answer better

---

#### PROMPTS — Pre-built Templates

Reusable prompt templates for common tasks.

```
Examples:
  - "code_review"      → template to review code
  - "summarise_doc"    → template to summarise a document
  - "debug_error"      → template to help debug an error
```

- The **User selects** which prompt to use
- Fills in parameters (like a form)
- Ensures consistent, high-quality AI outputs every time

---

## 4. Architecture — End-to-End Flow

Here is the full picture of how MCP is structured:

```
┌─────────────────────────────────────────────────────────────┐
│                    HOST APPLICATION                          │
│            (Claude Desktop / Cursor / VS Code)               │
│                                                              │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│   │  MCP Client  │  │  MCP Client  │  │  MCP Client  │     │
│   │      1       │  │      2       │  │      3       │     │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└──────────┼─────────────────┼─────────────────┼─────────────┘
           │                 │                 │
      Transport         Transport         Transport
    (stdio / HTTP)    (stdio / HTTP)    (stdio / HTTP)
           │                 │                 │
           ▼                 ▼                 ▼
   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
   │  MCP Server A │ │  MCP Server B │ │  MCP Server C │
   │               │ │               │ │               │
   │ [Tools]       │ │ [Tools]       │ │ [Tools]       │
   │ [Resources]   │ │ [Resources]   │ │ [Resources]   │
   │ [Prompts]     │ │ [Prompts]     │ │ [Prompts]     │
   └───────────────┘ └───────────────┘ └───────────────┘
    e.g. Filesystem    e.g. Database     e.g. GitHub API
```

---

### 4.1 Transport Layer

The transport is how the Client and Server talk to each other. There are two options:

#### stdio (Standard Input/Output)

- Client launches the Server as a **child process** on the same machine
- They communicate through stdin and stdout (text pipes)
- Simple, fast, no networking needed
- Best for: local tools (reading files, querying local DBs, running scripts)

```
[Client]  ──stdin/stdout──>  [Server Process]
           same machine
```

#### HTTP + SSE (Server-Sent Events)

- Server runs as a **separate process**, possibly on another machine
- Client sends requests via **HTTP POST**
- Server pushes responses back via **SSE** (a one-way stream over HTTP)
- Best for: remote tools, cloud services, tools shared across teams

```
[Client]  ──HTTP POST──>  [Remote Server]
          <──SSE stream──
```

---

## 5. How a Request Actually Works

Let's trace what happens when you ask:
**"Read my notes.txt file and summarise it"**

```
Step 1: User types the question in the Host app (e.g. Claude Desktop)
           │
           ▼
Step 2: AI reads the question and thinks:
        "I need to read a file. I have a tool for that: read_file()"
           │
           ▼
Step 3: MCP Client sends a tool call request to MCP Server:
        {
          "method": "tools/call",
          "params": {
            "name": "read_file",
            "arguments": { "path": "notes.txt" }
          }
        }
           │
           ▼
Step 4: MCP Server executes the function — reads notes.txt
           │
           ▼
Step 5: Server returns the result to the Client:
        {
          "content": "Meeting at 3pm. Buy milk. Call mom."
        }
           │
           ▼
Step 6: AI receives the file content and responds to the user:
        "Your notes say: Meeting at 3pm, buy milk, and call mom."
```

---

### 5.1 Tool Discovery

Before any of the above can happen, the Client needs to know **what tools the Server has**.

This is called **Tool Discovery** and happens right after the connection is established:

```
Client  →  Server: "What tools do you have?"
Server  →  Client: [
    { name: "read_file",   description: "...", parameters: {...} },
    { name: "write_file",  description: "...", parameters: {...} },
    { name: "list_files",  description: "...", parameters: {...} }
]
```

The AI then knows which tools are available and can choose the right one.

---

### 5.2 Full Lifecycle of a Session

```
1. INITIALIZE
   Client connects to Server
   They agree on protocol version and capabilities
   (Like a handshake at the start of a phone call)

2. DISCOVER
   Client asks: "What tools / resources / prompts do you have?"
   Server lists everything it can offer

3. OPERATE (repeated as many times as needed)
   AI calls tools → Server executes → Result returned
   AI reads resources → Server provides data

4. SHUTDOWN
   Client sends a close signal
   Server cleans up and closes connection
```

---

## 6. Quick Recap

| Concept | What it is | One-line summary |
|---------|-----------|-----------------|
| **MCP** | Open standard protocol | Lets AI talk to external tools in a standard way |
| **Host** | The AI app you use | Claude Desktop, Cursor, VS Code |
| **Client** | Lives inside Host | Manages 1-to-1 connection with a Server |
| **Server** | Tool provider | Exposes tools/resources/prompts to the AI |
| **Tools** | Functions AI can call | Do things: read file, query DB, send email |
| **Resources** | Data AI can read | Context: file contents, DB rows, API data |
| **Prompts** | Reusable templates | Consistent workflows: code review, summary |
| **stdio** | Local transport | Client and Server on same machine via pipes |
| **HTTP+SSE** | Remote transport | Client and Server over a network |

---

### The one analogy to remember everything:

> **MCP is like a USB-C port for AI.**
> Just as USB-C lets you plug any device into any laptop with one standard connector,
> MCP lets any AI app connect to any tool with one standard protocol.

---

*Next topic → `02_MCP_Host_Client_Server` — Deep dive into responsibilities, execution boundaries, and trust boundaries.*
