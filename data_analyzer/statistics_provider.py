import collections
import datetime

import pandas as pd

from dateutil.relativedelta import relativedelta

from data_processor.data_type.repository_type import Tutorial
from util import helpers, settings, paths


def provide_list_of_dependents_statistics():
    all_dependents = pd.read_csv(paths.ALL_DEPENDENTS_FILE)
    print(f'{len(all_dependents)} dependents of the libraries')


def provide_list_of_dependent_applications_statistics():
    dependent_applications = pd.read_csv(paths.DEPENDENT_APPLICATION_FILE)
    print(f'{len(dependent_applications)} dependent applications')

    filter_by_commit_number = dependent_applications[dependent_applications['# of commits'] >= 100]
    print(f'{len(filter_by_commit_number)} repositories after filter by number of commits')

    six_months_early_date = datetime.date(2023, 2, 20) + relativedelta(months=-6)
    filter_by_last_commit_date = filter_by_commit_number[
        pd.to_datetime(filter_by_commit_number['pushed_at']).dt.date >= six_months_early_date]
    print(f'{len(filter_by_last_commit_date)} repositories after filter by last commit date')

    filter_by_tutorial = filter_by_last_commit_date[
        filter_by_last_commit_date['is_tutorial'] == Tutorial.NOT_TUTORIAL.value]
    print(f'{len(filter_by_tutorial)} repositories after removing tutorials')


def provide_list_of_filtered_dependent_applications_statistics():
    filtered_dependent_applications = pd.read_csv(paths.FILTERED_DEPENDENT_APPLICATION_FILE)
    filtered_dependent_applications_with_stars = filtered_dependent_applications[
        filtered_dependent_applications['stars_count'] >= 100]

    print(f'{len(filtered_dependent_applications)} filtered dependent applications and '
          f'{len(filtered_dependent_applications_with_stars)} have 100 or more stars')


def provide_requirements_file_statistics():
    filtered_repositories = pd.read_csv(paths.FILTERED_DEPENDENT_APPLICATION_FILE)
    repos_having_req_files = filtered_repositories[filtered_repositories['has_requirements_files'] == True]
    print(f'{len(repos_having_req_files)} repositories have requirements files')


def provide_setup_file_statistics():
    setup_files = helpers.get_setup_file_paths(paths.REPOSITORIES_DIRECTORY)
    print(f'{setup_files["repository_name"].nunique()} repositories have setup files')


def provide_dependency_management_file_statistics():
    requirements_files = helpers.get_requirements_file_paths(paths.REPOSITORIES_DIRECTORY)
    setup_files = helpers.get_setup_file_paths(paths.REPOSITORIES_DIRECTORY)

    repository_names = pd.concat([requirements_files["repository_name"], setup_files["repository_name"]])
    print(f'{repository_names.nunique()} repositories have dependency management files')


def provide_library_version_use_statistics():
    specifications = pd.read_csv(paths.SAVED_SPECIFICATIONS_FILE, dtype=str)

    for library_short_name, library_detail in settings.LIBRARIES.items():
        for package in library_detail.packages:
            major_revisions = specifications[specifications['package_name'] == package.package_name][
                'resolved_major_revision'].values
            counter = collections.Counter(major_revisions)
            print(package.package_name, counter.most_common())


def provide_library_use_statistics():
    specifications = pd.read_csv(paths.SAVED_SPECIFICATIONS_FILE)
    print(f'{specifications["repository_name"].nunique()} repositories use any of the libraries')


def provide_selected_version_use_statistics():
    specifications = pd.read_csv(paths.SAVED_SPECIFICATIONS_FILE, dtype=str)

    repository_names = pd.Series(dtype=pd.StringDtype())
    for library_short_name, library_detail in settings.LIBRARIES.items():
        package_names = [package.package_name for package in library_detail.packages]
        repositories_with_library_specifications = specifications[
            specifications['package_name'].isin(package_names)]
        repositories_use_latest_major_revision = repositories_with_library_specifications[
            repositories_with_library_specifications[
                'resolved_major_revision'].isin(library_detail.working_major_revisions)]
        repository_names = pd.concat([repository_names, repositories_use_latest_major_revision['repository_name']],
                                     ignore_index=True)

    print(f'{repository_names.nunique()} repositories use selected major revisions of the libraries')


def provide_repositories_detected_method_calls_statistics():
    detected_method_calls = pd.read_csv(paths.DETECTED_METHOD_CALLS_FILE)

    repository_names = pd.Series(dtype=pd.StringDtype())
    for library_short_name, library_detail in settings.LIBRARIES.items():
        package_names = [package.package_name for package in library_detail.packages]
        repositories_with_method_calls_from_package = detected_method_calls[
            detected_method_calls['call_root_package'].isin(package_names)]
        repository_names = pd.concat([repository_names, repositories_with_method_calls_from_package['repository_name']])

    print(
        f'{repository_names.nunique()} repositories have {len(repository_names)} predefined method calls from the libraries')


def provide_statistics_on_specifications():
    provide_library_use_statistics()
    provide_library_version_use_statistics()
    provide_selected_version_use_statistics()


def provide_statistics_on_dependents():
    provide_list_of_dependents_statistics()
    provide_list_of_dependent_applications_statistics()
    provide_list_of_filtered_dependent_applications_statistics()


def provide_statistics_after_data_process():
    provide_statistics_on_dependents()

    provide_requirements_file_statistics()

    provide_statistics_on_specifications()


if __name__ == '__main__':
    provide_statistics_after_data_process()
    provide_repositories_detected_method_calls_statistics()
