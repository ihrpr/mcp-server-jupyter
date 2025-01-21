from typing import Dict
from mcp.server.fastmcp import FastMCP

from mcp_server_jupyter.notebook_manager import NotebookManager

mcp = FastMCP("Jupyter notebook manager")


@mcp.tool()
def read_notebook(notebook_path: str) -> int:
    """Read the notebook specified by notebook_path."""
    nb_manager = NotebookManager(notebook_path)
    return nb_manager.get_notebook_details()


@mcp.tool()
def add_cell(
    notebook_path: str, cell_type: str = "code", source: str = "", position: int = -1
) -> str:
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
    return executed_nb_json


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
