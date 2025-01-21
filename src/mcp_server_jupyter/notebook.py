from dataclasses import dataclass
import json
from typing import Any, Literal


from enum import Enum


@dataclass
class TextContent:
    type: Literal["text"]
    text: str


@dataclass
class ImageContent:
    type: Literal["image"]
    data: str  # base64 encoded data
    mime_type: str


@dataclass
class CellOutput:
    output: TextContent | ImageContent

    @classmethod
    def from_dict(cls, output_data: dict[str, Any]) -> "CellOutput":
        """Create CellOutput from notebook output dictionary."""
        output_type = output_data.get("output_type")

        # Handle different output types
        if output_type == "display_data" or output_type == "execute_result":
            data = output_data.get("data", {})

            # Handle image output
            if "image/png" in data:
                return ImageContent(
                    type="image",
                    data=data["image/png"],
                    mime_type="image/png",
                )

            # Handle text/plain output
            elif "text/plain" in data:
                return TextContent(
                    type="text",
                    text=data["text/plain"],
                )

            return TextContent(
                type="text",
                text=str(data),
            )

        elif output_type == "stream":
            return TextContent(
                type="text",
                text=output_data.get("text", ""),
            )

        elif output_type == "error":
            return TextContent(
                type="text",
                text=json.dumps(
                    {
                        "ename": output_data.get("ename", ""),
                        "evalue": output_data.get("evalue", ""),
                        "traceback": output_data.get("traceback", []),
                    }
                ),
            )

        return TextContent(
            type="text",
            text=str(output_data),
        )


@dataclass
class NotebookCell:
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
            cell_type=cell_data.get("cell_type", ""),
            content="".join(cell_data.get("source", [])),
            outputs=outputs,
            execution_count=cell_data.get("execution_count"),
            metadata=cell_data.get("metadata"),
        )
