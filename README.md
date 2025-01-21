# mcp-server-jupyter

MCP server for Jupyter noteboks and JupyterLab

## How to configure to use with Claude Desktop

```
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

Update directory and add/remove --with libraries that are usually used in your projects

```
{
  "mcpServers": {
    "Jupyter-notebook-manager": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/inna/mcp-server-jupyter/src/mcp_server_jupyter",
        "--with",
        "numpy",
        "--with",
        "matplotlib",
        "server.py"
      ]
    }
  }
}
```
