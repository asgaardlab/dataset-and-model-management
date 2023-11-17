from _ast import ClassDef
from ast import NodeVisitor
from typing import Any


class ClassDefinitionFinder(NodeVisitor):
    def __init__(self, class_name: str):
        self.class_name = class_name
        self.class_definitions: list[ClassDef] = []

    def visit_ClassDef(self, node: ClassDef) -> Any:
        if node.name == self.class_name:
            self.class_definitions.append(node)
        else:
            self.generic_visit(node)
