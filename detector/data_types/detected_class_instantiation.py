import ast


class DetectedClassCall:
    def __init__(self, file_path: str, call_node: ast.Call, class_instantiation_node: ast.Assign):
        self.file_path: str = file_path
        self.call_node: ast.Call = call_node
        self.instantiation_node: ast.Assign = class_instantiation_node
