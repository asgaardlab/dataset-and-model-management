import ast
from _ast import Call


class CallNode:
    def __init__(self, node: Call, method_name: str):
        self.node = node
        self.method_name = method_name

    def get_node_source(self, code_lines: list[str]) -> str:
        return code_lines[self.node.lineno - 1].strip()

    def get_full_call_name(self) -> str:
        return ast.unparse(self.node.func)
