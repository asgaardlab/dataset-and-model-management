import ast
from _ast import AST, Call, Assign


def is_different_context(node1: AST, node2: AST):
    return isinstance(node1, (ast.FunctionDef, ast.ClassDef, ast.Lambda)) and type(node2) == type(node1)


def is_same_node(node1: AST, node2: AST):
    return id(node1) == id(node2)


def find_assignment_nodes(parent_node: AST, assignment_object_name, last_contextual_parent_node, origin_line_no, is_self):
    assignment_nodes: list[Assign] = []
    for child_node in ast.iter_child_nodes(parent_node):
        if isinstance(child_node, ast.FunctionDef) and child_node.name == '__init__' and is_self:
            assignment_nodes += find_assignment_nodes(child_node, assignment_object_name, last_contextual_parent_node,
                                                      origin_line_no,
                                                      is_self)
        if is_different_context(last_contextual_parent_node, child_node):
            continue
        if is_same_node(last_contextual_parent_node, child_node):
            continue
        if isinstance(child_node, ast.Assign):
            if child_node.lineno < origin_line_no:
                for target in child_node.targets:
                    target_initialization_name = ast.unparse(target)
                    if target_initialization_name == assignment_object_name:
                        assignment_nodes += [child_node]
        assignment_nodes += find_assignment_nodes(child_node, assignment_object_name, last_contextual_parent_node,
                                                  origin_line_no, is_self)

    return assignment_nodes


def find_assignment_node(object_name: str, call_node: Call) -> Assign | None:
    find_node = call_node
    assignment_nodes = []
    is_self = (object_name.split('.')[0] == 'self')
    while not assignment_nodes and hasattr(find_node, 'parent'):
        assignment_nodes = find_assignment_nodes(find_node.parent, object_name, find_node, call_node.lineno, is_self)
        find_node = find_node.parent

    if assignment_nodes:
        return assignment_nodes[-1]
    return None
