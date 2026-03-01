# 04 — MCP Quickstart (Hands-On)

> **Phase:** 1 — Foundations + Phase 3 — Running MCP Servers
> **Style:** Hands-on — follow along and build

---

## Table of Contents

1. [Claude Desktop + Airbnb MCP Server](#1-claude-desktop--airbnb-mcp-server)
2. [Task 1 — Build a Basic MCP Server with a Hello World Tool](#2-task-1--build-a-basic-mcp-server-with-a-hello-world-tool)
3. [Task 2 — Weather of Any City Across the Globe](#3-task-2--weather-of-any-city-across-the-globe)

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

## 3. Task 2 — Weather of Any City Across the Globe

> **Goal:** Build an MCP server with a `get_weather` tool that returns live current
> weather for any city in the world — using **no API key**.
> You will run it two ways: via the **MCP Inspector** (browser UI) and via **Claude Desktop**.
>
> **APIs used:** Open-Meteo (free, no signup required)
> **File:** `04_MCP_Quickstart/task_02_weather/server.py`

---

### 3.1 What We're Building

```
YOU (user)
    │
    │  "What's the weather in Tokyo?"
    ▼
┌──────────────────────────────────────────────────┐
│              Claude Desktop (Host)               │
│   Claude decides to call → get_weather tool      │
│                                                  │
│  ┌────────────────────────────────────────────┐  │
│  │         MCP Client (built-in)              │  │
│  └──────────────────┬───────────────────────┘   │
└─────────────────────┼────────────────────────────┘
                      │  STDIO transport
                      ▼
┌──────────────────────────────────────────────────┐
│          server.py  (our MCP server)             │
│                                                  │
│   Tool: get_weather(city: str) -> str            │
│                                                  │
│   Step 1: Geocoding API  ──► city → lat/lon      │
│   Step 2: Weather API    ──► lat/lon → weather   │
└──────────────────────────────────────────────────┘
         │                          │
         ▼                          ▼
  geocoding-api               api.open-meteo.com
  .open-meteo.com             (current weather)
  (city → coordinates)
```

---

### 3.2 Project Setup

All tasks in Topic 04 live inside the same `uv` project.
Each task gets its own subfolder.

```
04_MCP_Quickstart/
├── 04_MCP_Quickstart.md
├── task_01_hello_world/
│   └── server.py
└── task_02_weather/
    └── server.py          ← you write this
```

No new packages needed — `httpx` is already installed as part of `mcp[cli]` from Task 1.

Verify it is available:

```bash
uv run python -c "import httpx; print('httpx ready')"
```

---

### 3.3 Why Open-Meteo?

| Feature | Detail |
|---------|--------|
| Free | No credit card, no quota limits for personal use |
| No API key | No signup required — just call the URL |
| Global coverage | Works for any city in the world |
| Two APIs needed | Geocoding API (city → lat/lon) + Forecast API (lat/lon → weather) |

---

### 3.4 The Two APIs — Explained

#### API 1 — Geocoding (city name → coordinates)

```
GET https://geocoding-api.open-meteo.com/v1/search?name=Tokyo&count=1&language=en&format=json
```

Response (trimmed):
```json
{
  "results": [
    {
      "name": "Tokyo",
      "country": "Japan",
      "latitude": 35.6895,
      "longitude": 139.6917
    }
  ]
}
```

We take `latitude` and `longitude` from the first result and pass them to the weather API.

---

#### API 2 — Current Weather (coordinates → weather data)

```
GET https://api.open-meteo.com/v1/forecast
    ?latitude=35.6895
    &longitude=139.6917
    &current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code
    &wind_speed_unit=kmh
```

Response (trimmed):
```json
{
  "current": {
    "temperature_2m": 18.5,
    "relative_humidity_2m": 65,
    "wind_speed_10m": 12.4,
    "weather_code": 3
  }
}
```

`weather_code` is a **WMO standard code** — we convert it to text using a lookup table
(e.g., code `3` = "Overcast").

---

### 3.5 Write the Server

**File:** `04_MCP_Quickstart/task_02_weather/server.py`

```python
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")


def weather_code_to_description(code: int) -> str:
    """Convert WMO weather code to a human-readable description."""
    codes = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Icy fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        85: "Slight snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
    }
    return codes.get(code, f"Unknown condition (code {code})")


@mcp.tool()
def get_weather(city: str) -> str:
    """Get the current weather for any city in the world."""

    # Step 1: Convert city name to latitude/longitude using Open-Meteo geocoding API
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {"name": city, "count": 1, "language": "en", "format": "json"}

    with httpx.Client() as client:
        geo_response = client.get(geo_url, params=geo_params)
        geo_data = geo_response.json()

    if not geo_data.get("results"):
        return f"City '{city}' not found. Please check the spelling and try again."

    result = geo_data["results"][0]
    lat = result["latitude"]
    lon = result["longitude"]
    name = result["name"]
    country = result.get("country", "")

    # Step 2: Fetch current weather using Open-Meteo weather API
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "wind_speed_unit": "kmh",
    }

    with httpx.Client() as client:
        weather_response = client.get(weather_url, params=weather_params)
        weather_data = weather_response.json()

    current = weather_data["current"]
    temp = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    wind = current["wind_speed_10m"]
    condition = weather_code_to_description(current["weather_code"])

    return (
        f"Weather in {name}, {country}:\n"
        f"  Condition  : {condition}\n"
        f"  Temperature: {temp}°C\n"
        f"  Humidity   : {humidity}%\n"
        f"  Wind Speed : {wind} km/h"
    )


if __name__ == "__main__":
    mcp.run()
```

That is the complete server. Every block is explained in detail in section 3.9.

---

### 3.6 Run with MCP Inspector (Browser UI)

The **MCP Inspector** is a browser-based tool that lets you call your server's
tools manually — without needing Claude Desktop. Use it to test your server first.

Run:

```bash
uv run mcp dev 04_MCP_Quickstart/task_02_weather/server.py
```

Expected output:

```
Starting MCP inspector...
Proxy server listening on port 5173
Open http://localhost:5173 in your browser
```

Open `http://localhost:5173` in your browser.

**What you'll see:**

1. Left panel — **Tools** tab: shows `get_weather` is registered
2. Click `get_weather` → a form appears asking for `city` (string)
3. Enter `Mumbai` → click **Run Tool**
4. Result panel shows:

```
Weather in Mumbai, India:
  Condition  : Clear sky
  Temperature: 32.1°C
  Humidity   : 71%
  Wind Speed : 14.2 km/h
```

Try a few more cities to confirm global coverage:
- `New York`
- `Sydney`
- `Dubai`
- `InvalidCityXYZ` → should return the "not found" message

Press `Ctrl+C` in the terminal when done.

---

### 3.7 Connect to Claude Desktop

To use this server from Claude Desktop, add it to your config file.

**Windows config location:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

Open it and add the `weather` entry alongside the existing `hello-world` server:

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
    },
    "weather": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "D:\\Study\\MCP_Server",
        "mcp",
        "run",
        "04_MCP_Quickstart/task_02_weather/server.py"
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

### 3.8 Test in Claude Desktop

After restarting Claude Desktop:

1. Click the **hammer icon** (🔨) near the chat input
2. You should see `get_weather` listed under `weather` server
3. Type in chat:

```
What is the weather like in Tokyo right now?
```

Claude will call the tool and respond with live data:

```
Weather in Tokyo, Japan:
  Condition  : Partly cloudy
  Temperature: 18.5°C
  Humidity   : 65%
  Wind Speed : 12.4 km/h
```

Try more natural questions:

```
Compare the weather in London and Mumbai.
```

```
Is it raining in Sydney?
```

Claude will call `get_weather` for each city automatically.

---

### 3.9 Code Walkthrough — Line by Line

```python
import httpx
from mcp.server.fastmcp import FastMCP
```

`httpx` is a modern HTTP client for Python — it is what we use to call the
Open-Meteo APIs. It was installed automatically when we ran `uv add "mcp[cli]"` in Task 1.

`FastMCP` is the same high-level MCP server wrapper we used in Task 1 — it handles
JSON-RPC, tool registration, and STDIO transport automatically.

---

```python
mcp = FastMCP("weather")
```

Creates the MCP server instance. The string `"weather"` is the **server name**
announced to the client during the initialization handshake. It's what appears in
Claude Desktop's tool panel header.

---

```python
def weather_code_to_description(code: int) -> str:
    codes = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        ...
    }
    return codes.get(code, f"Unknown condition (code {code})")
```

This is a **plain helper function** — not a tool. It is not decorated with `@mcp.tool()`
so Claude never sees it. It exists only to convert the numeric WMO weather code
(e.g., `63`) returned by the API into a readable string (e.g., `"Moderate rain"`).

The fallback `f"Unknown condition (code {code})"` handles any new codes the API might
introduce in the future without crashing.

---

```python
@mcp.tool()
def get_weather(city: str) -> str:
    """Get the current weather for any city in the world."""
```

The `@mcp.tool()` decorator does four things automatically:

| What it does | How |
|---|---|
| Registers the function as an MCP tool | Adds it to the server's tool list |
| Reads the function name | Tool is named `get_weather` |
| Reads the type hints | Builds a JSON schema: `city` is a required string |
| Reads the docstring | Sends it as the tool description to the LLM |

The LLM sees this tool as:
```json
{
  "name": "get_weather",
  "description": "Get the current weather for any city in the world.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "city": { "type": "string" }
    },
    "required": ["city"]
  }
}
```

The description is what helps Claude decide **when** to call this tool.
Always write clear, specific docstrings.

---

```python
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {"name": city, "count": 1, "language": "en", "format": "json"}

    with httpx.Client() as client:
        geo_response = client.get(geo_url, params=geo_params)
        geo_data = geo_response.json()
```

**Step 1 — Geocoding.** We call the Open-Meteo geocoding API to convert the
city name into latitude and longitude coordinates. `httpx.Client()` is used as
a context manager (`with`) so the connection is always properly closed after the
request, even if something goes wrong.

`params=geo_params` automatically URL-encodes the dictionary into query parameters:
```
?name=Tokyo&count=1&language=en&format=json
```

---

```python
    if not geo_data.get("results"):
        return f"City '{city}' not found. Please check the spelling and try again."
```

If the city name is invalid or not found, the API returns an empty `results` list.
We check for this **before** trying to read coordinates — and return a helpful message
immediately. MCP tools should never raise unhandled exceptions because that breaks
the tool call from the client's perspective. Always return a string.

---

```python
    result = geo_data["results"][0]
    lat = result["latitude"]
    lon = result["longitude"]
    name = result["name"]
    country = result.get("country", "")
```

We take the **first result** (most relevant match) and extract the fields we need.
`result.get("country", "")` uses a default of empty string in case the country
field is missing for some locations.

---

```python
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "wind_speed_unit": "kmh",
    }

    with httpx.Client() as client:
        weather_response = client.get(weather_url, params=weather_params)
        weather_data = weather_response.json()
```

**Step 2 — Weather fetch.** We pass the coordinates we just got to the Open-Meteo
forecast API. The `current` parameter is a comma-separated list telling the API
exactly which fields to return — this keeps the response small and focused.

---

```python
    current = weather_data["current"]
    temp = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    wind = current["wind_speed_10m"]
    condition = weather_code_to_description(current["weather_code"])

    return (
        f"Weather in {name}, {country}:\n"
        f"  Condition  : {condition}\n"
        f"  Temperature: {temp}°C\n"
        f"  Humidity   : {humidity}%\n"
        f"  Wind Speed : {wind} km/h"
    )
```

We extract the four weather fields and call our helper to convert the numeric
`weather_code` to text. The final return is a formatted multi-line string —
this is exactly what Claude will receive and use to answer the user.

---

```python
if __name__ == "__main__":
    mcp.run()
```

Starts the server in **STDIO mode** (the default).
The server reads JSON-RPC messages from `stdin` and writes responses to `stdout`.
When Claude Desktop launches this file as a child process, this is the entry point.

---

### 3.10 What Happens Under the Hood — Full Request Flow

When Claude calls `get_weather(city="Paris")`:

```
1. Claude Desktop sends over STDIO:
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "tools/call",
     "params": {
       "name": "get_weather",
       "arguments": { "city": "Paris" }
     }
   }

2. FastMCP receives this, finds the get_weather function, calls it:
   get_weather(city="Paris")

3. Tool calls Geocoding API:
   GET https://geocoding-api.open-meteo.com/v1/search?name=Paris&count=1...
   → returns: lat=48.85341, lon=2.3488, name="Paris", country="France"

4. Tool calls Weather API:
   GET https://api.open-meteo.com/v1/forecast?latitude=48.85341&longitude=2.3488...
   → returns: temp=14.2, humidity=78, wind=22.1, weather_code=63

5. Function returns:
   "Weather in Paris, France:
     Condition  : Moderate rain
     Temperature: 14.2°C
     Humidity   : 78%
     Wind Speed : 22.1 km/h"

6. FastMCP wraps it and sends back over STDIO:
   {
     "jsonrpc": "2.0",
     "id": 1,
     "result": {
       "content": [
         { "type": "text", "text": "Weather in Paris, France:\n  Condition  : Moderate rain\n ..." }
       ]
     }
   }

7. Claude reads the result and incorporates it into its response to you
```

---

### 3.11 Summary

| | Detail |
|--|--------|
| **What you built** | A Python MCP server that fetches live weather for any city |
| **SDK used** | `mcp[cli]` — already installed from Task 1 |
| **Tool** | `get_weather(city: str) -> str` |
| **Transport** | STDIO |
| **Test method 1** | `uv run mcp dev server.py` → MCP Inspector at `localhost:5173` |
| **Test method 2** | Claude Desktop with `uv run mcp run server.py` config |
| **APIs used** | Open-Meteo Geocoding + Open-Meteo Forecast (both free, no key) |
| **Key concept** | Chain two API calls inside one tool — Claude only sees the final result |
| **Error handling** | City not found → return helpful string instead of crashing |
| **Server file** | `04_MCP_Quickstart/task_02_weather/server.py` |

---

