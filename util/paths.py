import os

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

DATA_DIRECTORY = os.path.join(ROOT_DIR, 'data')

ALL_DEPENDENTS_DIRECTORY = os.path.join(DATA_DIRECTORY, 'all_dependents')
ALL_DEPENDENTS_FILE = os.path.join(DATA_DIRECTORY, 'all_dependents.csv')
DEPENDENT_LIBRARIES_DIRECTORY = os.path.join(DATA_DIRECTORY, 'dependent_libraries')
DEPENDENT_LIBRARIES_FILE = os.path.join(DATA_DIRECTORY, 'dependent_libraries.csv')
DEPENDENT_APPLICATION_FILE = os.path.join(DATA_DIRECTORY, 'dependent_applications.csv')
FILTERED_DEPENDENT_APPLICATION_FILE = os.path.join(DATA_DIRECTORY, 'filtered_dependent_applications.csv')

LIBRARIES_RELEASES_DIRECTORY = os.path.join(DATA_DIRECTORY, 'library_releases')
REPOSITORIES_DIRECTORY = os.path.join(DATA_DIRECTORY, 'repositories')
MANUAL_ANALYSIS_DIRECTORY = os.path.join(DATA_DIRECTORY, 'manual_analysis')
MANUAL_ANALYSIS_RESULT_DIRECTORY = os.path.join(DATA_DIRECTORY, 'manual_analysis_result')
REPOSITORIES_FOR_MANUAL_ANALYSIS_DIRECTORY = os.path.join(DATA_DIRECTORY, 'repositories_for_manual_analysis')
REQUIREMENTS_FILES_DIRECTORY = os.path.join(DATA_DIRECTORY, 'requirements_files')
SAMPLE_REPOSITORIES_DIRECTORY = os.path.join(DATA_DIRECTORY, 'sample_repositories')
SELECTED_REPOSITORIES_DIRECTORY = os.path.join(DATA_DIRECTORY, 'selected_repositories')

SAVED_PY_FILE = os.path.join(DATA_DIRECTORY, 'all_py_file_path.csv')
SAVED_REQUIREMENTS_FILE = os.path.join(DATA_DIRECTORY, 'all_requirements_file_path.csv')
SAVED_SETUP_FILE = os.path.join(DATA_DIRECTORY, 'all_setup_file_path.csv')
SAVED_SPECIFICATIONS_FILE = os.path.join(DATA_DIRECTORY, 'all_specifications.csv')
DETECTED_METHOD_CALLS_FILE = os.path.join(DATA_DIRECTORY, 'detected_method_calls.csv')
DETECTED_CLASS_INSTANTIATIONS_FILE = os.path.join(DATA_DIRECTORY, 'detected_class_instantiations.csv')
REPOSITORIES_FOR_MANUAL_ANALYSIS_FILE = os.path.join(DATA_DIRECTORY, 'repositories_for_manual_analysis.csv')
REPOSITORIES_METADATA_FILE = os.path.join(DATA_DIRECTORY, 'repositories_metadata.csv')
SELECTED_REPOSITORIES_FILE = os.path.join(DATA_DIRECTORY, 'selected_repositories.csv')

DATASET_FILES_FILE = os.path.join(DATA_DIRECTORY, 'dataset_files.csv')
MODEL_FILES_FILE = os.path.join(DATA_DIRECTORY, 'model_files.csv')

WORKING_REPOSITORIES_DIRECTORY = REPOSITORIES_FOR_MANUAL_ANALYSIS_DIRECTORY
