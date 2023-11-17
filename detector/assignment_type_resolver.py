import ast
from _ast import AST

from detector.class_definition_finder import ClassDefinitionFinder
from detector.data_types.root import Root
from util import helpers


class AssignmentRootResolver:
    def __init__(self, assignment_node: ast.Assign, code_ast: AST):
        self.assignment_node = assignment_node
        self.code_ast = code_ast

    def get_assignment_root(self) -> Root | None:
        if isinstance(self.assignment_node.value, ast.Call):
            called_name = ast.unparse(self.assignment_node.value.func)
            called_name_parts = called_name.split('.')
            assignment_root = None
            if assignment_root is None:
                assignment_root = self.get_type_from_class_definition(called_name_parts[-1])
            if assignment_root is None:
                assignment_root = self.get_type_from_import(called_name)
            if assignment_root is None:
                assignment_root = Root(called_name, self.assignment_node.value.func)
            return assignment_root
        elif isinstance(self.assignment_node.value, ast.Attribute):
            called_name = ast.unparse(self.assignment_node.value.value)
            assignment_root = None
            if assignment_root is None:
                assignment_root = self.get_type_from_import(called_name)
            if assignment_root is None:
                assignment_root = Root(called_name, self.assignment_node.value.value)
            return assignment_root
        else:
            return Root(ast.unparse(self.assignment_node.value), self.assignment_node.value)

    def get_type_from_class_definition(self, find_name) -> Root | None:
        cdf = ClassDefinitionFinder(find_name)
        cdf.visit(self.code_ast)

        if cdf.class_definitions:
            class_definition = cdf.class_definitions[-1]
            if class_definition.bases:
                for base_class in class_definition.bases:
                    base_class_name = ast.unparse(base_class)
                    import_node, import_name = helpers.get_import_node(base_class_name, class_definition.lineno,
                                                                       self.code_ast)

                    if import_node:
                        return Root(import_name, import_node)
                return Root(find_name, class_definition.bases[0])
            return Root(find_name, class_definition)

        return None

    def get_type_from_import(self, name) -> Root | None:
        import_node, import_name = helpers.get_import_node(name, self.assignment_node.lineno, self.code_ast)
        if import_node:
            return Root(import_name, import_node)

        return None
