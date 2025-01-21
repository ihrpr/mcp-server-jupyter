from base64 import b64decode
from dataclasses import asdict
import io
import json
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP, Image as MCPImage
from PIL import Image as PILImage

from mcp_server_jupyter.notebook import ImageContent, NotebookCell, TextContent
from mcp_server_jupyter.notebook_manager import NotebookManager


mcp = FastMCP("Jupyter notebook manager")


@mcp.tool()
def read_notebook(notebook_path: str) -> list[NotebookCell]:
    """Read the notebook specified by notebook_path."""
    nb_manager = NotebookManager(notebook_path)
    return nb_manager.get_notebook_details()


@mcp.tool()
def add_cell(
    notebook_path: str, cell_type: str = "code", source: str = "", position: int = -1
) -> list[str] | MCPImage:
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
    all_images = [
        (output.text if output is TextContent else _get_mcp_image(output))
        for output in all_outputs
    ]
    return all_images[0]


def _get_mcp_image(image_cell: ImageContent) -> MCPImage:
    img_data = b64decode(image_cell.data)
    image = PILImage.open(io.BytesIO(img_data))
    image.thumbnail((100, 100))
    return MCPImage(data=image.tobytes(), format="png")


#     return """
# [
# {
#   "type": "text",
#   "text": "Tool result text"
# },{
#   "type": "text",
#   "text": "Tool result text"
# }]
# """


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
