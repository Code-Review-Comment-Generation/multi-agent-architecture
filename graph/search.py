import json
from typing import List, Optional
from .models import Graph, Node, Link

class SearchTools:
    def __init__(self, graph_path: str):
        self.graph = Graph.model_validate_json(open(graph_path).read())

    def search_by_class_name(self, class_name: str) -> List[Node]:
        nodes = []
        for node in self.graph.nodes:
            if node.type == "class" and node.signature == class_name:
                nodes.append(node)
        return nodes
    
    def search_by_function_name(self, function_name: str) -> List[Node]:
        nodes = []
        for node in self.graph.nodes:
            if node.type == "function" and node.signature == function_name:
                nodes.append(node)
        return nodes
    
    def get_code_snippet(self, file_path: str, start: int, end: int) -> str:
        with open(file_path, "r") as f:
            lines = f.readlines()
            return "".join(lines[start - 1 : end])
        
    def get_file_skeleton(self, file_path: str) -> str:
        with open(file_path, "r") as f:
            lines = f.readlines()
            return "".join(lines)
        
    def get_node_references(self, node_id: str) -> List[Link]:
        links = []
        for edge in self.graph.links:
            if edge.source.startswith(node_id) and not edge.target.startswith(node_id) and edge.edge_type == "references":
                links.append(edge)
        return links
    
    def get_node_by_id(self, id: str) -> Node:
        for node in self.graph.nodes:
            if node.id == id:
                return node
        return None
    
    def get_node_references_recursive(self, node_id: str, max_depth: int = 3) -> List[dict]:
        if max_depth == 0:
            return {
                "node_id": node_id,
            }
        print(node_id)
        references = []

        for edge in self.graph.links:
            if edge.source.startswith(node_id) and not edge.target.startswith(node_id) and edge.edge_type == "references":
                print("Target: ", edge.target)
                references.append(self.get_node_references_recursive(edge.target, max_depth - 1))
        
        res = {
            "node_id": node_id,
            "references": references
        }

        print(res)
        return res
    
    def get_node_reference(self, file_path: str, name: str) -> Optional[Node]:
        print("Searching for node reference: ", file_path, name)
        for edge in self.graph.links:
            if edge.source.startswith(file_path) and edge.target.endswith("::" + name):
                return edge
        return None
    
    def get_node_reference_from_fqn(self, full_qualified_name: str) -> Optional[Node]:
        for node in self.graph.nodes:
            if node.id.endswith(full_qualified_name):
                return node
        return None
    
if __name__ == "__main__":
    search_tools = SearchTools("./logs/repo_graph.json")
    # print(search_tools.search_by_class_name("Tool"))
    # print(search_tools.search_by_function_name("from_row"))
    # print(search_tools.get_class_code("Tool"))

    node_id = "llm/default_plugins/openai_models.py"

    references = search_tools.get_node_references(node_id)
    
    # print("references:")
    # for reference in references:
    #     node = search_tools.get_node_by_id(reference.target)
    #     code = search_tools.get_code_snippet("../sample_repo/" + node.loc.file_name, node.loc.start_line, node.loc.end_line)
    #     print("--------------------------------")
    #     print(node.id)
    #     print(code)
    #     print("--------------------------------")
    
    # recursive_references = search_tools.get_node_references_recursive(node_id, 2)
    # print(json.dumps(recursive_references, indent=4))
    
    link = search_tools.get_node_reference("llm/default_plugins/openai_models.py", "simplify_usage_dict")
    node = search_tools.get_node_by_id(link.target)
    code = search_tools.get_code_snippet("../sample_repo/" + node.loc.file_name, node.loc.start_line, node.loc.end_line)

    print(code)