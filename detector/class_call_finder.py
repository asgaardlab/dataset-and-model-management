import ast
from _ast import Call
from ast import NodeVisitor


class ClassCallFinder(NodeVisitor):
    def __init__(self, class_instance_name: str, after_line_no: int, class_names: list[str]):
        self.class_instance_name: str = class_instance_name
        self.after_line_no = after_line_no
        self.nn_types = class_names
        self.instance_calls: list[Call] = []

    def visit_Call(self, node: Call):
        if node.lineno > self.after_line_no:
            call_name = ast.unparse(node.func)

            if call_name == self.class_instance_name and self.is_not_call_inside_nn_type(node):
                self.instance_calls.append(node)
        self.generic_visit(node)

    def is_not_call_inside_nn_type(self, node: Call):
        parent_node = node.parent
        while not isinstance(parent_node, (ast.FunctionDef, ast.Module)) and hasattr(parent_node, 'parent'):
            parent_node = parent_node.parent

        if isinstance(parent_node, ast.FunctionDef) \
                and parent_node.name in ['__init__', 'forward'] and parent_node.args.args[0].arg == 'self':
            parent_node = node.parent
            while not isinstance(parent_node, (ast.ClassDef, ast.Module)) and hasattr(parent_node, 'parent'):
                parent_node = parent_node.parent
            if isinstance(parent_node, ast.ClassDef):
                for base in parent_node.bases:
                    base_class_name = ast.unparse(base)
                    if base_class_name in self.nn_types:
                        return False
        return True
