from _ast import FunctionDef
from ast import NodeVisitor
from typing import Any


class FunctionDefinitionFinder(NodeVisitor):
    def __init__(self, function_name: str):
        self.function_name = function_name
        self.definitions: list[FunctionDef] = []

    def visit_FunctionDef(self, node: FunctionDef) -> Any:
        if node.name == self.function_name:
            self.definitions.append(node)

        self.generic_visit(node)
