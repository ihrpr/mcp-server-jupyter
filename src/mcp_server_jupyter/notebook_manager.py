import json
from typing import Dict, List, Optional, Tuple, Any
import nbformat
from nbformat import NotebookNode
from nbclient import NotebookClient


class NotebookManager:
    def __init__(self, notebook_path: str) -> None:
        self.notebook_path: str = notebook_path
        with open(notebook_path) as f:
            self.notebook: NotebookNode = nbformat.read(f, as_version=4)

    def get_notebook_details(self) -> str:
        """Get details of the notebook"""
        """Format the notebook"""
        # for now let's return the executed notebook as a JSON string
        # later this will be changed to return the results in a more structured way, inlcuding images etc
        return json.dumps(self.notebook.dict())

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
            cell_index: int = next(
                index
                for index, cell in enumerate(self.notebook.cells)
                if cell.get("id") == id
            )
            self.notebook.cells.pop(cell_index)
            return True
        except StopIteration:
            return False

    def update_cell_code(self, id: str, new_code: str) -> bool:
        """Update code in a cell specified by its ID.

        Args:
            id: The unique identifier of the cell to update
            new_code: The new source code to put in the cell

        Returns:
            True if cell was found and updated, False if cell wasn't found
            or wasn't a code cell
        """
        try:
            # Find cell by ID
            cell: NotebookNode = next(
                cell for cell in self.notebook.cells if cell.get("id") == id
            )

            # Update only if it's a code cell
            if cell.cell_type == "code":
                cell.source = new_code
                return True
            return False

        except StopIteration:
            return False

    def execute_notebook(self, parameters: Optional[Dict[str, Any]] = None) -> str:
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

    def save_notebook(self, path: Optional[str] = None) -> None:
        """Save the notebook to file

        Args:
            path: Optional path to save the notebook to. If not provided,
                 uses the original path
        """
        save_path: str = path or self.notebook_path
        with open(save_path, "w") as f:
            nbformat.write(self.notebook, f)
