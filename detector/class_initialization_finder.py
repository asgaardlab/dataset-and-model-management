import ast
from _ast import Assign
from ast import NodeVisitor
from typing import Any


class ClassInitFinder(NodeVisitor):
    def __init__(self, class_names: list[str]) -> None:
        self.class_names: list[str] = class_names
        self.initializations: list[Assign] = []

    def visit_Assign(self, node: Assign) -> Any:
        if isinstance(node.value, ast.Call):
            called_name = ast.unparse(node.value.func)
            called_name_parts = called_name.split('.')

            if called_name_parts[-1] in self.class_names:
                self.initializations.append(node)

        self.generic_visit(node)
