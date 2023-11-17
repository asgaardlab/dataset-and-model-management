import pandas as pd

from data_analyzer.statistics_provider import provide_statistics_on_specifications, provide_statistics_on_dependents, \
    provide_requirements_file_statistics
from data_processor.application_repositories_filterer import filter_application_repositories
from data_processor.dependency_resolver import resolve_dependency
from data_processor.dependent_applications_list_maker import list_application_libraries
from data_processor.dependent_libraries_list_maker import list_dependent_libraries
from data_processor.library_releases_extractor import extract_libraries_releases
from data_processor.repositories_downloader import download_repositories
from data_processor.repositories_for_manual_analysis_selector import select_repositories_for_manual_analysis
from data_processor.repositories_selector import select_repositories
from data_processor.requirements_file_downloader import download_requirements_files
from util import paths

if __name__ == '__main__':
    # python library_dependents_collector.py --repo tensorflow/tensorflow --package_name tensorflow
    # python library_dependents_collector.py --repo pytorch/pytorch --package_name torch
    # python library_dependents_collector.py --repo scikit-learn/scikit-learn --package_name scikit-learn
    # python library_dependents_collector.py --repo scikit-learn/scikit-learn --package_name sklearn
    list_dependent_libraries()
    list_application_libraries()
    filter_application_repositories()
    provide_statistics_on_dependents()

    extract_libraries_releases()

    download_requirements_files()
    provide_requirements_file_statistics()

    resolve_dependency()
    select_repositories()
    provide_statistics_on_specifications()

    select_repositories_for_manual_analysis()

    repos = pd.read_csv(paths.REPOSITORIES_FOR_MANUAL_ANALYSIS_FILE)
    download_repositories(repos, paths.REPOSITORIES_FOR_MANUAL_ANALYSIS_DIRECTORY,
                          paths.REPOSITORIES_FOR_MANUAL_ANALYSIS_FILE)
