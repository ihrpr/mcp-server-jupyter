# mcp-server-jupyter

An MCP server for managing and interacting with Jupyter notebooks programmatically.

![Demo](demo/mcp_server-jupyter.gif)

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
        "mcp-server-jupyter"
      ],
      "env": {
        "UV_PROJECT_ENVIRONMENT": "/path/to/venv_for_jupyter/.venv"
      }
    }
  }
}
```

## How to Use

1. Start JupyterLab or Jupyter Notebook

When using uv to run Jupyter notebooks it's much easier to manage venv and package installations.

Please follow [uv jupyter docummentation](https://docs.astral.sh/uv/guides/integration/jupyter/) for more details.

```bash
uv venv --seed
uv run --with jupyter jupyter lab

```

NOTE: this environment should be used as UV_PROJECT_ENVIRONMENT env variable in MCP server.

2. Open or create a notebook in JupyterLab/Jupyter Notebook

3. Get the full path to your notebook:

   - In JupyterLab: Right-click on the notebook in the file browser → "Copy Path"
   - In Jupyter Notebook: Copy the path from the URL (modify to full system path)

4. In Claude Desktop chat:

   - Always use the full path to the notebook when calling tools
   - Example: `/Users/username/projects/my_notebook.ipynb`

5. Important Notes:
   - After any modifications through Claude (add_cell, edit_cell):
     - Reload the notebook page in JupyterLab/Jupyter Notebook
     - Current version does not support automatic reload
   - Keep JupyterLab/Jupyter Notebook instance running while working with Claude

## License

This project is licensed under the MIT License. See the LICENSE file for details.
