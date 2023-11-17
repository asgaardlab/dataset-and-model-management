import ast
from _ast import Call, AST
from ast import NodeVisitor

from detector.data_types.call_node import CallNode
from util import helpers


class MethodCallFinder(NodeVisitor):
    def __init__(self, code_ast: AST, method_names: list[str]):
        self.code_ast: AST = code_ast
        self.method_names: list[str] = method_names
        self.method_calls: list[CallNode] = []
        self.found_1st_call: bool = False

    def visit_Call(self, node: Call):
        call_name = node.func.attr if isinstance(node.func, ast.Attribute) else \
            node.func.id if isinstance(node.func, ast.Name) else ''

        if call_name in self.method_names:
            if not self.found_1st_call:
                helpers.associate_parent_with_nodes(self.code_ast)
                self.found_1st_call = True
            self.method_calls.append(CallNode(node, call_name))
        self.generic_visit(node)
