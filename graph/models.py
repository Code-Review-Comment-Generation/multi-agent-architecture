from typing import List, Optional, Any, ClassVar, Dict
import pydantic
from pydantic import model_validator

class Loc(pydantic.BaseModel):
    """Represents a location in the codebase."""
    file_name: str = pydantic.Field(description="Path to the file containing the node")
    node_name: str = pydantic.Field(description="Fully qualified name of the node (including file path and namespace)")
    start_line: int = pydantic.Field(description="Starting line number of the node in the file (1-indexed)")
    end_line: int = pydantic.Field(description="Ending line number of the node in the file (1-indexed)")

class Node(pydantic.BaseModel):
    """Represents a node in the repository graph."""
    id: str = pydantic.Field(description="Unique identifier for the node, typically same as node_name")
    type: str = pydantic.Field(description="Type of the node (file, directory, class, method, function, global_variable, etc.)")

    docstring: Optional[str] = pydantic.Field(description="Documentation string of the node, if available", default=None)
    signature: Optional[str] = pydantic.Field(description="Signature of the node (e.g., function parameters), if applicable", default=None)

    layer: int = pydantic.Field(description="Hierarchical level in the codebase (0 for directories, 1 for files, 2 for classes, 3 for methods/functions, 4 for global variables)")
    loc: Loc = pydantic.Field(description="Location information of the node in the codebase")
    
class Link(pydantic.BaseModel):
    """Represents an edge in the repository graph connecting two nodes."""
    source: str = pydantic.Field(description="ID of the source node")
    target: str = pydantic.Field(description="ID of the target node")
    edge_type: str = pydantic.Field(description="Type of relationship between nodes (e.g., 'contains', 'references')")
    

class Graph(pydantic.BaseModel):
    """Represents the entire repository graph."""
    directed: bool = pydantic.Field(description="Whether the graph is directed")
    multigraph: bool = pydantic.Field(description="Whether the graph is a multigraph")
    graph: dict = pydantic.Field(description="Metadata about the graph")
    nodes: List[Node] = pydantic.Field(description="List of nodes in the graph")
    links: List[Link] = pydantic.Field(description="List of edges in the graph")
    
    @model_validator(mode='before')
    @classmethod
    def preprocess_loc_fields(cls, data: Dict) -> Dict:
        if isinstance(data, dict) and "nodes" in data and isinstance(data["nodes"], list):
            for node in data["nodes"]:
                if "loc" in node and isinstance(node["loc"], list) and len(node["loc"]) >= 4:
                    node["loc"] = {
                        "file_name": node["loc"][0],
                        "node_name": node["loc"][1],
                        "start_line": node["loc"][2],
                        "end_line": node["loc"][3]
                    }
        return data
