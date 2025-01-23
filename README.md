# mcp-server-jupyter

An MCP server for managing and interacting with Jupyter notebooks programmatically.

## Components

### Tools

The server provides five tools for notebook manipulation:

1. `read_notebook_with_outputs`: Read a notebook's content including cell outputs

   - Required: `notebook_path` (string)

2. `read_notebook_source_only`: Read notebook content without outputs

   - Required: `notebook_path` (string)
   - Use when size limitations prevent reading full notebook with outputs

3. `read_output_of_cell`: Read output of a specific cell

   - Required:
     - `notebook_path` (string)
     - `cell_id` (string)

4. `add_cell`: Add new cell to notebook

   - Required:
     - `notebook_path` (string)
     - `source` (string)
   - Optional:
     - `cell_type` (string): "code" or "markdown"
     - `position` (integer): insertion index (-1 to append)

5. `edit_cell`: Modify existing cell content
   - Required:
     - `notebook_path` (string)
     - `cell_id` (string)
     - `source` (string)

## Usage with Claude Desktop

Add this configuration to your Claude Desktop config file:

### MacOS

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "Jupyter-notebook-manager": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/mcp-server-jupyter/src/mcp_server_jupyter",
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

Customize `--with` libraries based on your project requirements.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
