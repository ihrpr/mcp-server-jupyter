import json
from typing import Any, Dict, Optional

import nbformat
from nbclient import NotebookClient
from nbformat import NotebookNode

from mcp_server_jupyter.notebook_cell import NotebookCell


class NotebookManager:
    def __init__(self, notebook_path: str) -> None:
        self.notebook_path: str = notebook_path
        with open(notebook_path) as f:
            self.notebook: NotebookNode = nbformat.read(f, as_version=4)

    def get_notebook_details(self) -> list[NotebookCell]:
        """Get details of the notebook"""
        """Format the notebook"""

        return self.parse_notebook_nodes(self.notebook)

    def get_cell_by_index(self, cell_index: int) -> NotebookNode:
        """Get a cell by its index"""
        if not 0 <= cell_index < len(self.notebook.cells):
            raise ValueError(f"Cell index {cell_index} is out of range")

        # Get the target cell
        return self.notebook.cells[cell_index]

    def get_cell_by_id(self, cell_id: str) -> NotebookNode:
        """Get a cell by its unique ID"""
        try:
            # Find cell by ID
            return next(
                cell for cell in self.notebook.cells if cell.get("id") == cell_id
            )
        except StopIteration:
            raise ValueError(f"No cell found with ID {cell_id}")

    def add_cell(
        self, cell_type: str = "code", source: str = "", position: int = -1
    ) -> int:
        """Add a new cell at specified position (default: end)

        Args:
            cell_type: Type of cell to add ("code", "markdown", or "raw")
            source: Content of the cell
            position: Position to insert the cell (-1 for end)

        Returns:
            Index of the newly added cell

        Raises:
            ValueError: If cell_type is not supported
        """
        # Create new cell using the correct method
        if cell_type == "code":
            new_cell = nbformat.v4.new_code_cell(source=source)
        elif cell_type == "markdown":
            new_cell = nbformat.v4.new_markdown_cell(source=source)
        elif cell_type == "raw":
            new_cell = nbformat.v4.new_raw_cell(source=source)
        else:
            raise ValueError(f"Unsupported cell type: {cell_type}")

        if position == -1 or position >= len(self.notebook.cells):
            self.notebook.cells.append(new_cell)
        else:
            self.notebook.cells.insert(position, new_cell)

        return len(self.notebook.cells) - 1

    def remove_cell(self, id: str) -> bool:
        """Remove cell by a specific id.
        Each cell has a unique ID as per nbformat specification.

        Args:
            id: The unique identifier of the cell to remove

        Returns:
            True if cell was found and removed, False otherwise
        """
        try:
            # Get index by cell ID
            cell = self.get_cell_by_id(id)
            cell_index = self.notebook.cells.index(cell)
            self.notebook.cells.pop(cell_index)
            return True
        except StopIteration:
            return False

    def update_cell_source(self, id: str, new_source: str) -> bool:
        """Update source in a cell specified by its ID.

        Args:
            id: The unique identifier of the cell to update
            new_code: The new source code to put in the cell

        Returns:
            True if cell was found and updated, False if cell wasn't found
        """
        try:
            # Find cell by ID
            cell = self.get_cell_by_id(id)

            cell.source = new_source
            return True

        except StopIteration:
            return False

    def execute_notebook(
        self, parameters: Optional[Dict[str, Any]] = None
    ) -> list[NotebookCell]:
        """Execute the notebook and return results

        Args:
            parameters: Optional dictionary of parameters to update in the notebook

        Returns:
            Tuple containing:
                - Dictionary mapping cell execution counts to their outputs
                - Executed notebook node
        """
        # Update parameters if provided
        if parameters:
            for cell in self.notebook.cells:
                if cell.cell_type == "code" and "parameters" in cell.metadata:
                    cell.source = f"params = {parameters}"

        # Execute the notebook
        client = NotebookClient(self.notebook, timeout=600)
        client.execute()
        return self.get_notebook_details()

    def execute_cell_by_id(
        self, cell_id: str, parameters: Optional[Dict[str, Any]] = None
    ) -> list[NotebookCell]:
        """Execute a single cell in the notebook by its ID and return its results

        Args:
            cell_id: ID of the cell to execute
            parameters: Optional dictionary of parameters to update in the notebook

        Returns:
            Output of the executed cell
        """
        # Find the cell with matching ID
        target_cell = self.get_cell_by_id(cell_id)
        cell_index = self.notebook.cells.index(target_cell)

        # Update parameters if provided and if it's a parameters cell
        if (
            parameters
            and target_cell.cell_type == "code"
            and "parameters" in target_cell.metadata
        ):
            target_cell.source = f"params = {parameters}"

        client = NotebookClient(self.notebook, timeout=600)
        with client.setup_kernel():
            executed_cell = client.execute_cell(target_cell, cell_index)
            return self.parse_notebook_nodes(executed_cell)

    def execute_cell_by_index(
        self, cell_index: int, parameters: Optional[Dict[str, Any]] = None
    ) -> list[NotebookCell]:
        """Execute a single cell in the notebook by its index and return its results

        Args:
            cell_index: Index of the cell to
            parameters: Optional dictionary of parameters to update in the notebook

        Returns:
            Output of the executed cell
        """
        target_cell = self.get_cell_by_index(cell_index)
        return self.execute_cell_by_id(target_cell.get("id", ""), parameters)

    def save_notebook(self, path: Optional[str] = None) -> None:
        """Save the notebook to file

        Args:
            path: Optional path to save the notebook to. If not provided,
                 uses the original path
        """
        save_path: str = path or self.notebook_path
        with open(save_path, "w") as f:
            nbformat.write(self.notebook, f)

    def parse_notebook_nodes(self, notebook: NotebookNode) -> list[NotebookCell]:
        """Parse a Jupyter notebook JSON string into a list of NotebookCell objects."""
        try:
            cells = []
            # NotebookCell is an object that is retured from a single cell execution
            # as well as representing the entire notebook
            if "cells" not in notebook:
                cells.append(NotebookCell.from_dict(notebook))
                return cells

            for cell_data in notebook.cells:
                cells.append(NotebookCell.from_dict(cell_data))
            return cells
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid notebook JSON: {str(e)}")
