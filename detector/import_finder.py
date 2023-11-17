import ast
from _ast import Import, ImportFrom
from ast import NodeVisitor
from typing import Any


def get_import_names(node: ast.Import | ast.ImportFrom) -> dict[str, str]:
    import_names = {}
    items = [nn.__dict__ for nn in node.names]
    if isinstance(node, ast.Import):
        for d in items:
            if d['asname'] is None:  # alias name not found, use its imported name
                import_names[d['name']] = d['name']
            else:
                import_names[d['asname']] = d['name']  # otherwise , use alias name
    elif isinstance(node, ast.ImportFrom):
        for d in items:
            if d['asname'] is None:
                import_names[d['name']] = node.module + '.' + d['name']
            else:
                import_names[d['asname']] = node.module + '.' + d['name']
    return import_names


class ImportFinder(NodeVisitor):
    def __init__(self, find_name: str, before_lineno: int) -> None:
        self.find_name: str = find_name
        self.before_lineno: int = before_lineno
        self.import_nodes: list[Import | ImportFrom] = []

    def visit_Import(self, node: Import) -> Any:
        if node.lineno < self.before_lineno:
            imports = get_import_names(node)
            if self.find_name in imports:
                self.import_nodes.append(node)
            else:
                self.generic_visit(node)

    def visit_ImportFrom(self, node: ImportFrom) -> Any:
        if node.lineno < self.before_lineno:
            if node.module is None and node.level == 1:
                node.module = '.'
            if node.module is None and node.level == 2:
                node.module = '..'
            if node.module is None and node.level == 3:
                node.module = '...'
            if node.module is None and node.level == 4:
                node.module = '....'
            if node.module is None and node.level == 5:
                node.module = '.....'

            imports = get_import_names(node)
            if self.find_name in imports:
                self.import_nodes.append(node)
            else:
                self.generic_visit(node)
