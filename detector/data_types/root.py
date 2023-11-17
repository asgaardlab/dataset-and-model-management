import ast
from _ast import AST

from detector.data_types.call_root_type import CallRootType
from detector.import_finder import get_import_names


class Root:
    def __init__(self, search_name: str, root_node: AST, assignment_root: 'Root' = None):
        self.search_name = search_name
        self.root_node = root_node
        self.assignment_root: Root | None = assignment_root
        self.full_name = None

    def get_node_source(self, code_lines: list[str]) -> str:
        return code_lines[self.root_node.lineno - 1].strip()

    def get_full_name(self) -> str:
        if self.full_name is not None:
            return self.full_name
        if isinstance(self.root_node, (ast.Import, ast.ImportFrom)):
            import_names = get_import_names(self.root_node)
            self.full_name = import_names[self.search_name]
        elif isinstance(self.root_node, ast.arg):
            self.full_name = '.'.join([self.root_node.parent.parent.name, self.search_name])
        elif isinstance(self.root_node, ast.FunctionDef):
            self.full_name = self.root_node.name
        elif isinstance(self.root_node, ast.Assign):
            if self.assignment_root:
                if isinstance(self.assignment_root.root_node, (ast.Import, ast.ImportFrom)):
                    import_names = get_import_names(self.assignment_root.root_node)
                    self.full_name = import_names[self.assignment_root.search_name]
                elif isinstance(self.assignment_root.root_node, ast.ClassDef):
                    self.full_name = self.assignment_root.root_node.name
                elif isinstance(self.assignment_root.root_node, ast.Constant):
                    self.full_name = str(type(self.assignment_root.root_node.value).__name__)
                else:
                    self.full_name = ast.unparse(self.assignment_root.root_node)
        else:
            self.full_name = ''
        return self.full_name

    def get_call_root_type(self) -> str:
        if self.root_node:
            if isinstance(self.root_node, (ast.Import, ast.ImportFrom)):
                return CallRootType.IMPORT.value
            if isinstance(self.root_node, ast.arg):
                return CallRootType.FUNCTION_PARAMETER.value
            elif isinstance(self.root_node, ast.FunctionDef):
                return CallRootType.CUSTOM_FUNCTION.value
            elif isinstance(self.root_node, ast.Assign):
                if self.assignment_root:
                    if isinstance(self.assignment_root.root_node, (ast.Import, ast.ImportFrom)):
                        return CallRootType.ASSIGNMENT_IMPORT.value
                    elif isinstance(self.assignment_root.root_node, ast.ClassDef):
                        return CallRootType.ASSIGNMENT_CLASS.value
                    elif isinstance(self.assignment_root.root_node, ast.Constant):
                        return CallRootType.CONSTANT.value
                    else:
                        return CallRootType.ASSIGNMENT_UNKNOWN.value
                else:
                    return CallRootType.ASSIGNMENT_UNKNOWN.value
        return ''
