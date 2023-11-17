import ast
from _ast import ClassDef, AST
from ast import NodeVisitor
from typing import Any

from detector.import_finder import get_import_names
from util import helpers


class ClassBaseDefinitionFinder(NodeVisitor):
    def __init__(self, code_ast: AST, search_names: list[str]):
        self.code_ast: AST = code_ast
        self.search_names: list[str] = search_names
        self.base_classes: list[ClassDef] = []

    def visit_ClassDef(self, node: ClassDef) -> Any:
        if node.bases:
            for base in node.bases:
                base_class_name = ast.unparse(base)
                if base_class_name in self.search_names and self.is_base_imported_from_torch(base_class_name, node):
                    base.parent = node
                    self.base_classes.append(base)
        self.generic_visit(node)

    def is_base_imported_from_torch(self, base_class_name, node):
        import_node, import_name = helpers.get_import_node(base_class_name, node.lineno, self.code_ast)
        if import_node:
            import_names = get_import_names(import_node)
            if import_names[import_name].startswith('torch.'):
                return True
        return False
