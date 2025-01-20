from typing import Dict
from mcp.server.fastmcp import FastMCP
from notebook_manager import NotebookManager

mcp = FastMCP("Jupyter notebook manager")


@mcp.tool()
def add_cell(
    notebook_path: str, cell_type: str = "code", source: str = "", position: int = -1
) -> int:
    """Add a cell to the notebook specified by notebook_path to a specific position."""
    nb_manager = NotebookManager(notebook_path)
    nb_manager.add_cell(
        cell_type=cell_type,
        source=source,
        position=position,
    )
    # Execute the modified notebook
    parameters: Dict[str, str] = {}
    executed_nb_json = nb_manager.execute_notebook(parameters)

    nb_manager.save_notebook()
    return executed_nb_json


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
