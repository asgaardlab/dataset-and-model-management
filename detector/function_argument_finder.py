import ast
from _ast import arguments, arg
from ast import NodeVisitor
from typing import Any


class ParameterFinder(NodeVisitor):
    def __init__(self, parameter_name):
        self.parameter_name = parameter_name
        self.matched_arguments: list[arg] = []

    def visit_arguments(self, node: arguments) -> Any:
        if isinstance(node.parent, ast.FunctionDef):
            for argument in node.args:
                if argument.arg == self.parameter_name:
                    self.matched_arguments.append(argument)
