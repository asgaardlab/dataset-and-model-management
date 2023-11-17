import os.path

import pandas as pd
from pybraries import search_helpers

from util import settings, paths


def list_dependent_libraries_for_package(package_name):
    dependent_libraries_json = []

    page = 1
    while True:
        print(f'getting list from page {page}')
        dependent_libraries_in_page = search_helpers.search_api('project_dependents', 'pypi', package_name,
                                                                per_page=100, page=page)
        dependent_libraries_json += dependent_libraries_in_page

        if len(dependent_libraries_in_page) < 100:
            break
        page += 1

    return [
        [library['name'], library['description'], library['stars'], library['forks'], library['language'],
         ', '.join(library['keywords']), library['platform'], library['package_manager_url'], library['homepage'],
         library['repository_url'], library['status'], library['rank']] for library in dependent_libraries_json]


def save_result(data, save_path):
    pd.DataFrame(data, columns=['name', 'description', 'stars', 'forks', 'language', 'keywords', 'platform',
                                'package_manager_url', 'homepage', 'repository_url', 'status', 'rank']).to_csv(
        save_path, index=False)


def list_dependent_libraries():
    print('Listing dependent libraries...')
    for library_short_name, library_detail in settings.LIBRARIES.items():
        for package in library_detail.packages:
            print(f'{package.package_name}...')
            dependent_libraries = list_dependent_libraries_for_package(package.package_name)
            print(f'{len(dependent_libraries)} dependent libraries of {package.package_name}')
            os.makedirs(paths.DEPENDENT_LIBRARIES_DIRECTORY, exist_ok=True)
            save_file_path = os.path.join(paths.DEPENDENT_LIBRARIES_DIRECTORY, package.dependents_file_name)
            save_result(dependent_libraries, save_file_path)


if __name__ == '__main__':
    list_dependent_libraries()
