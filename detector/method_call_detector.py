import os.path
from _ast import AST

import pandas as pd

from detector.call_root_finder import CallRootFinder
from detector.data_types.call_node import CallNode
from detector.data_types.detected_call import DetectedCall
from method_call_finder import MethodCallFinder
from util import helpers, paths, settings, constants


class MethodCallDetector:
    def __init__(self, method_names: list[str], save_file_name: str) -> None:
        self.method_names = method_names
        self.save_file_name = save_file_name
        self.save_file_header = [
            'call_root_type', 'method_name',
            'method_call', 'line_no',
            'call_root', 'call_root_line_no',
            'qualifying_name',
            'call_root_package',
            'relative_file_path', 'repository_name', 'file_path']

        self.write_header()

    def detect_method_calls_in_file(self, code_ast: AST, file_path: str) -> list[DetectedCall]:
        call_nodes = self.get_call_nodes(code_ast)

        detected_calls = []
        for call_node in call_nodes:
            detected_call = self.get_call_trace(call_node, file_path, code_ast)
            detected_calls.append(detected_call)
        return detected_calls

    def get_call_trace(self, call_node: CallNode, file_path: str, code_ast: AST) -> DetectedCall:
        call_root_finder = CallRootFinder(call_node, code_ast)
        call_root = call_root_finder.get_call_root()

        return DetectedCall(file_path, call_node, call_root)

    def get_call_nodes(self, code_ast) -> list[CallNode]:
        if code_ast:
            method_call_finder = MethodCallFinder(code_ast, self.method_names)
            method_call_finder.visit(code_ast)
            return method_call_finder.method_calls
        return []

    def write_header(self) -> None:
        header = [self.save_file_header]
        df = pd.DataFrame(header)
        df.to_csv(self.save_file_name, index=False, header=False)

    def save_result(self, repo_dir_name: str, detected_calls: list[DetectedCall]) -> None:
        rows = [[
            detected_call.call_root.get_call_root_type() if detected_call.call_root else None,
            detected_call.call_node.method_name,
            detected_call.call_node.get_node_source(detected_call.code_lines),
            detected_call.call_node.node.lineno,
            detected_call.call_root.get_node_source(detected_call.code_lines) if detected_call.call_root else None,
            detected_call.call_root.root_node.lineno if detected_call.call_root else None,
            detected_call.get_qualifying_name(),
            detected_call.get_qualifying_name().split('.')[0],
            helpers.get_relative_path_from_file_path(detected_call.file_path),
            helpers.get_repo_name_from_dir_name(repo_dir_name),
            detected_call.file_path]
            for detected_call in detected_calls]

        df = pd.DataFrame(rows, columns=self.save_file_header)
        df.to_csv(self.save_file_name, mode='a', index=False, header=False)

        self.save_result_for_manual_analysis(repo_dir_name, df)

    def save_result_for_manual_analysis(self, repo_dir_name: str, detected_calls: pd.DataFrame) -> None:
        os.makedirs(paths.MANUAL_ANALYSIS_DIRECTORY, exist_ok=True)
        file_for_manual_analysis = os.path.join(paths.MANUAL_ANALYSIS_DIRECTORY,
                                                f'_{repo_dir_name}',
                                                constants.DETECTED_METHOD_CALLS_FILE_NAME)
        detected_calls.to_csv(file_for_manual_analysis, index=False, header=True)


if __name__ == '__main__':
    detector = MethodCallDetector(settings.METHOD_NAMES, paths.DETECTED_METHOD_CALLS_FILE)

    # detected_calls = detector.detect_method_calls_in_file('C:\\Users\\tajki\\OneDrive\\Documents\\GitHub\\dataset-model-source_code-integration-analyzer\\data\\selected_repositories\\alexandre01@UltimateLabeling\\ultimatelabeling\\models\\track_info.py')
    # detector.save_result(detected_calls)

    # detected_calls = detector.detect_method_calls_in_repository('A3Data@hermione', 0)
    # detector.save_result(detected_calls)
