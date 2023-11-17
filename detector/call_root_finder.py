import ast
from _ast import Call, AST

from detector.assignment_finder import find_assignment_node
from detector.assignment_type_resolver import AssignmentRootResolver
from detector.data_types.call_node import CallNode
from detector.data_types.root import Root
from detector.function_argument_finder import ParameterFinder
from detector.function_definition_finder import FunctionDefinitionFinder
from util import helpers


class CallRootFinder:
    def __init__(self, call_node: CallNode, code_ast: AST) -> None:
        self.method_name = call_node.method_name
        self.call_node = call_node.node
        self.code_ast = code_ast

    def get_call_root(self) -> Root:
        root = None

        if isinstance(self.call_node.func, ast.Name):
            if root is None:
                root = self.find_in_parent_function_parameters(self.method_name, self.call_node)
            if root is None:
                root = self.find_in_custom_functions(self.method_name)
            if root is None:
                root = self.find_in_imports(self.method_name)

        if isinstance(self.call_node.func, ast.Attribute):
            called_full_name = ast.unparse(self.call_node.func)
            called_full_name_parts = called_full_name.split('.')

            if root is None and isinstance(self.call_node.func.value, ast.Call):
                class_name = ast.unparse(self.call_node.func.value.func)
                root = self.find_in_imports(class_name)
            if root is None:
                root = self.find_attribute_in_assignment('.'.join(called_full_name_parts[:-1]), self.call_node)
            if root is None:
                root = self.find_in_parent_function_parameters('.'.join(called_full_name_parts[:-1]), self.call_node)
            if root is None and len(called_full_name_parts) == 2 and called_full_name_parts[0] == 'self':
                root = self.find_in_custom_functions(called_full_name_parts[1])
            if root is None:
                root = self.find_in_imports(called_full_name)
        return root

    def find_in_parent_function_parameters(self, find_name: str, call_node: Call) -> Root | None:
        if find_name.startswith('self'):
            return None
        if hasattr(call_node, 'parent'):
            if isinstance(call_node.parent, ast.FunctionDef):
                fa = ParameterFinder(find_name)
                fa.visit(call_node.parent)

                if len(fa.matched_arguments) > 0:
                    return Root(find_name, fa.matched_arguments[-1])

            return self.find_in_parent_function_parameters(find_name, call_node.parent)

        return None

    def find_in_custom_functions(self, function_name: str) -> Root | None:
        ffd = FunctionDefinitionFinder(function_name)
        ffd.visit(self.code_ast)

        if len(ffd.definitions) > 0:
            return Root(function_name, ffd.definitions[-1])

        return None

    def find_in_imports(self, name: str) -> Root | None:
        import_node, import_name = helpers.get_import_node(name, self.call_node.lineno, self.code_ast)
        if import_node:
            return Root(import_name, import_node)

        return None

    def find_attribute_in_assignment(self, find_name: str, call_node: Call) -> Root | None:
        if find_name:
            assignment_node = find_assignment_node(find_name, call_node)
            if assignment_node:
                assignment_type_resolver = AssignmentRootResolver(assignment_node, self.code_ast)
                assignment_root = assignment_type_resolver.get_assignment_root()
                return Root(find_name, assignment_node, assignment_root)

        return None
