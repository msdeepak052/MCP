from mcp.server.fastmcp import FastMCP

# Create the MCP server — the string is the server's display name
mcp = FastMCP("hello-world")


@mcp.tool()
def hello_world(name: str) -> str:
    """Say hello to someone by name."""
    return f"Hello, {name}! Welcome to MCP."


if __name__ == "__main__":
    mcp.run()
