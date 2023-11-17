from detector.data_types.call_node import CallNode
from detector.data_types.root import Root
from util import helpers


class DetectedCall:
    def __init__(self, file_path: str, call_node: CallNode, call_root: Root):
        self.file_path: str = file_path
        self.call_node: CallNode = call_node
        self.call_root: Root = call_root
        self.code_lines: list[str] = helpers.get_code_lines(file_path)

    def get_qualifying_name(self) -> str:
        if self.call_root:
            call_root_name = self.call_root.get_full_name()

            call_name = self.call_node.get_full_call_name()
            call_name = call_name.replace(self.call_root.search_name, '')

            if call_name:
                call_name = call_name[1:] if call_name[0] == '.' else call_name
            if call_name:
                call_name = call_name[:-1] if call_name[-1] == '.' else call_name
            if call_name:
                return '.'.join([call_root_name, call_name])
            else:
                return call_root_name

        return self.call_node.get_full_call_name()
