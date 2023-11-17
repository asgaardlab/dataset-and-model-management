import os

from tqdm import tqdm

from detector.class_instantiation_detector import ClassInstantiationDetector
from detector.method_call_detector import MethodCallDetector
from util import helpers, paths, settings


def create_dir_for_manual_analysis(repo_dir_name):
    dir_name = os.path.join(paths.MANUAL_ANALYSIS_DIRECTORY, f'_{repo_dir_name}')
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)


class TrainingAndLoadingDetector:
    def __init__(self, repo_directory: str) -> None:
        self.py_files_per_repos = helpers.get_py_files_per_repository(repo_directory)
        self.total_repos = len(self.py_files_per_repos)

        self.method_call_detector = MethodCallDetector(settings.METHOD_NAMES, paths.DETECTED_METHOD_CALLS_FILE)
        self.class_instantiation_detector = ClassInstantiationDetector(paths.DETECTED_CLASS_INSTANTIATIONS_FILE)

    def detect(self):
        for index, repo_dir_name in enumerate(self.py_files_per_repos):
            detected_method_calls = []
            detected_classes = settings.CLASS_NAMES
            repo_py_files = self.py_files_per_repos[repo_dir_name]

            create_dir_for_manual_analysis(repo_dir_name)

            for file_path in tqdm(repo_py_files, desc=f'[{index + 1}|{self.total_repos}] {repo_dir_name}'):
                code_ast = helpers.get_ast(file_path)
                if code_ast:
                    helpers.associate_parent_with_nodes(code_ast)

                    detected_method_calls += self.method_call_detector.detect_method_calls_in_file(code_ast, file_path)
                    detected_classes += self.class_instantiation_detector.get_class_extensions_in_file(
                        code_ast,
                        settings.CLASS_NAMES)

            self.method_call_detector.save_result(repo_dir_name, detected_method_calls)
            detected_class_initializations = self.class_instantiation_detector.search_class_initialization(
                repo_py_files,
                detected_classes)
            self.class_instantiation_detector.save_result(repo_dir_name, detected_class_initializations)


if __name__ == '__main__':
    detector = TrainingAndLoadingDetector(paths.WORKING_REPOSITORIES_DIRECTORY)
    detector.detect()
