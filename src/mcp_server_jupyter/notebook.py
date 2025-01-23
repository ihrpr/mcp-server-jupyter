from dataclasses import dataclass
import json
from typing import Any
import mcp.types as types


@dataclass
class CellOutput:
    output: types.TextContent | types.ImageContent | types.EmbeddedResource

    @classmethod
    def from_dict(cls, output_data: dict[str, Any]) -> "CellOutput":
        """Create CellOutput from notebook output dictionary."""
        output_type = output_data.get("output_type")

        # Handle different output types
        if output_type == "display_data" or output_type == "execute_result":
            data = output_data.get("data", {})

            # Handle image output
            if "image/png" in data:
                return types.ImageContent(
                    type="image",
                    data=data["image/png"],
                    mimeType="image/png",
                )

            # Handle text/plain output
            elif "text/plain" in data:
                return types.TextContent(
                    type="text",
                    text=data["text/plain"],
                )

            return types.TextContent(
                type="text",
                text=str(data),
            )

        elif output_type == "stream":
            return types.TextContent(
                type="text",
                text=output_data.get("text", ""),
            )

        elif output_type == "error":
            return types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "ename": output_data.get("ename", ""),
                        "evalue": output_data.get("evalue", ""),
                        "traceback": output_data.get("traceback", []),
                    }
                ),
            )

        return types.TextContent(
            type="text",
            text=str(output_data),
        )


@dataclass
class NotebookCell:
    cell_id: str
    cell_type: str
    content: str
    outputs: list[CellOutput]
    execution_count: int | None = None
    metadata: dict[str, Any] = None

    @classmethod
    def from_dict(cls, cell_data: dict[str, Any]) -> "NotebookCell":
        """Create NotebookCell from notebook cell dictionary."""
        outputs = []
        if cell_data.get("cell_type") == "code":
            for output in cell_data.get("outputs", []):
                outputs.append(CellOutput.from_dict(output))

        return cls(
            cell_id=cell_data.get("id"),
            cell_type=cell_data.get("cell_type", ""),
            content="".join(cell_data.get("source", [])),
            outputs=outputs,
            execution_count=cell_data.get("execution_count"),
            metadata=cell_data.get("metadata"),
        )
