import ast
import os
from _ast import AST

import pandas as pd
from tqdm import tqdm

from detector.class_base_definition_finder import ClassBaseDefinitionFinder
from detector.class_call_finder import ClassCallFinder
from detector.class_initialization_finder import ClassInitFinder
from detector.data_types.detected_class_instantiation import DetectedClassCall
from util import helpers, paths, constants, settings


class ClassInstantiationDetector:
    def __init__(self, save_file_name: str):
        self.save_file_name = save_file_name
        self.save_file_header = [
            'call_name', 'line_no',
            'class_instantiation', 'instantiation_line_no',
            'relative_file_path', 'repository_name', 'file_path']

        self.write_header()

    def get_class_extensions_in_file(self, code_ast, class_names: list[str]) -> list[str]:
        class_base_definition_finder = ClassBaseDefinitionFinder(code_ast, class_names)
        class_base_definition_finder.visit(code_ast)

        class_extensions = []
        if len(class_base_definition_finder.base_classes) > 0:
            for base in class_base_definition_finder.base_classes:
                class_extensions.append(base.parent.name)
        return class_extensions

    def search_class_initialization(self, repo_py_files: list[str], class_names: list[str]) -> list[DetectedClassCall]:
        detected_instantiations = []
        for file_path in tqdm(repo_py_files, desc=f'Searching class instantiations...'):
            code_ast = helpers.get_ast(file_path)
            if code_ast:
                helpers.associate_parent_with_nodes(code_ast)
                init_finder = ClassInitFinder(class_names)
                init_finder.visit(code_ast)

                if len(init_finder.initializations) > 0:
                    for init in init_finder.initializations:
                        detected_instantiations += self.search_call_of_the_init(init, code_ast, file_path, class_names)

        return detected_instantiations

    def search_call_of_the_init(self, class_instantiation_node: ast.Assign, code_ast: AST, file_path: str,
                                class_names: list[str]) -> list[DetectedClassCall]:
        instance_name = ast.unparse(class_instantiation_node.targets[0])

        class_call_finder = ClassCallFinder(instance_name, class_instantiation_node.lineno, class_names)
        class_call_finder.visit(code_ast)

        detected_instantiations = []
        if len(class_call_finder.instance_calls) > 0:
            for call_node in class_call_finder.instance_calls:
                detected_instantiations.append(DetectedClassCall(file_path, call_node, class_instantiation_node))

        return detected_instantiations

    def write_header(self) -> None:
        header = [self.save_file_header]

        df = pd.DataFrame(header)
        df.to_csv(self.save_file_name, index=False, header=False)

    def save_result(self, repo_dir_name: str, detected_instantiations: list[DetectedClassCall]):
        rows = [[
            ast.unparse(detected_instantiation.call_node),
            detected_instantiation.call_node.lineno,
            ast.unparse(detected_instantiation.instantiation_node),
            detected_instantiation.instantiation_node.lineno,
            helpers.get_relative_path_from_file_path(detected_instantiation.file_path),
            helpers.get_repo_name_from_dir_name(repo_dir_name),
            detected_instantiation.file_path]
            for detected_instantiation in detected_instantiations]

        df = pd.DataFrame(rows, columns=self.save_file_header)
        df = df.sort_values(['relative_file_path', 'line_no'], ascending=[True, True])
        df.to_csv(self.save_file_name, mode='a', index=False, header=False)

        self.save_result_for_manual_analysis(repo_dir_name, df)

    def save_result_for_manual_analysis(self, repo_dir_name: str, detected_calls: pd.DataFrame) -> None:
        os.makedirs(paths.MANUAL_ANALYSIS_DIRECTORY, exist_ok=True)
        file_for_manual_analysis = os.path.join(paths.MANUAL_ANALYSIS_DIRECTORY,
                                                f'_{repo_dir_name}',
                                                constants.DETECTED_CLASS_INSTANTIATIONS_FILE_NAME)
        detected_calls.to_csv(file_for_manual_analysis, index=False, header=True)


def run_on_single_repo(repos_directory, repo_dir_name):
    class_instantiation_detector = ClassInstantiationDetector(paths.DETECTED_CLASS_INSTANTIATIONS_FILE)

    py_files_per_repos = helpers.get_py_files_per_repository(repos_directory)
    repo_py_files = py_files_per_repos[repo_dir_name]
    detected_classes = settings.CLASS_NAMES
    for file_path in repo_py_files:
        code_ast = helpers.get_ast(file_path)
        if code_ast:
            helpers.associate_parent_with_nodes(code_ast)
            detected_classes += class_instantiation_detector.get_class_extensions_in_file(code_ast,
                                                                                          settings.CLASS_NAMES)

    detected_class_initializations = class_instantiation_detector.search_class_initialization(repo_py_files,
                                                                                              detected_classes)
    class_instantiation_detector.save_result(repo_dir_name, detected_class_initializations)


if __name__ == '__main__':
    run_on_single_repo(paths.WORKING_REPOSITORIES_DIRECTORY, 'awsm-research@VulRepair')
