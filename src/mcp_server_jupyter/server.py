from typing import Dict
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from mcp_server_jupyter.notebook_manager import NotebookManager

# Create a server instance
server = Server("mcp-server-jupyter")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="read_notebook_with_outputs",
            description="""
            Read the latest version of the notebook specified by notebook_path including outputs. 
            Should always be used before modifying notebook to better understand what is already there and if modifications are needed or not.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "notebook_path": {"type": "string"},
                },
                "required": ["notebook_path"],
            },
        ),
        types.Tool(
            name="add_cell",
            description="Add a cell to the notebook specified by notebook_path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "notebook_path": {"type": "string"},
                    "cell_type": {"type": "string"},
                    "source": {"type": "string"},
                    "position": {"type": "integer"},
                },
                "required": ["notebook_path"],
            },
        ),
        types.Tool(
            name="edit_cell",
            description="Edit cell source in the notebook specified by notebook_path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "notebook_path": {"type": "string"},
                    "cell_id": {
                        "type": "string",
                        "description": "Unique ID of the cell to edit. It can be obtained from reding the notebook details (read_notebook tool).",
                    },
                    "source": {"type": "string"},
                },
                "required": ["notebook_path", "cell_id"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    if name == "read_notebook_with_outputs":
        notebook_path = arguments["notebook_path"]
        return _read_notebook(notebook_path)
    elif name == "add_cell":
        notebook_path = arguments["notebook_path"]
        cell_type = arguments.get("cell_type", "code")
        source = arguments.get("source", "")
        position = arguments.get("position", -1)
        return _add_cell(notebook_path, cell_type, source, position)
    elif name == "edit_cell":
        notebook_path = arguments["notebook_path"]
        id = arguments["cell_id"]
        source = arguments.get("source", "")
        return _edit_cell(notebook_path, id, source)

    raise ValueError(f"Unknown tool: {name}")


def _add_cell(
    notebook_path: str, cell_type: str, source: str, position: int
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Add a cell to the notebook specified by notebook_path to a specific position."""
    nb_manager = NotebookManager(notebook_path)
    new_cell_index = nb_manager.add_cell(
        cell_type=cell_type,
        source=source,
        position=position,
    )
    # Execute the modified notebook
    parameters: Dict[str, str] = {}
    executed_nb_json = nb_manager.execute_cell_by_index(new_cell_index, parameters)
    nb_manager.save_notebook()
    # flatten all outputs
    all_outputs = []
    for nb in executed_nb_json:
        all_outputs.extend(nb.outputs)

    return all_outputs


def _edit_cell(
    notebook_path: str,
    id: str,
    source: str,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """If there is already an existing cell that doens something similar to what user requested, edit that cell.
    We can check with the user if they want to edit the cell or add a new cell if it's not clear from the context.
    """
    nb_manager = NotebookManager(notebook_path)
    was_updated = nb_manager.update_cell_source(
        id=id,
        new_source=source,
    )
    if not was_updated:
        return [
            "No cell was updated, probably because the cell with the specified ID was not found."
        ]
    # Execute the modified notebook
    parameters: Dict[str, str] = {}
    executed_nb_json = nb_manager.execute_cell_by_id(id, parameters)
    nb_manager.save_notebook()
    # flatten all outputs
    all_outputs = []
    for nb in executed_nb_json:
        all_outputs.extend(nb.outputs)

    return all_outputs


def _read_notebook(
    notebook_path: str,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Read the notebook specified by notebook_path."""
    nb_manager = NotebookManager(notebook_path)

    results = []
    for nb in nb_manager.get_notebook_details():
        results.append(
            types.TextContent(type="text", text=f"Cell with ID: {nb.cell_id}")
        )
        results.append(types.TextContent(type="text", text=nb.content))
        if nb.cell_type == "code":
            results.extend(nb.outputs)
    return results


async def run():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="Jupyter notebook manager",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
