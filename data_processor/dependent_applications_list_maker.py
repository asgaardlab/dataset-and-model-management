import os.path

import pandas as pd

from util import helpers, paths, settings


def get_all_dependents():
    all_dependents = pd.DataFrame()
    for library_short_name, library_detail in settings.LIBRARIES.items():
        for package in library_detail.packages:
            all_dependents = pd.concat([all_dependents, pd.read_csv(
                os.path.join(paths.ALL_DEPENDENTS_DIRECTORY, package.dependents_file_name))])

    all_dependents = all_dependents.drop_duplicates()
    all_dependents.to_csv(paths.ALL_DEPENDENTS_FILE, index=False)

    return all_dependents


def get_github_url(dependent_row):
    if isinstance(dependent_row['repository_url'], str) and helpers.is_github_url(dependent_row['repository_url']):
        return dependent_row['repository_url']
    elif isinstance(dependent_row['homepage'], str) and helpers.is_github_url(dependent_row['homepage']):
        return dependent_row['homepage']
    elif isinstance(dependent_row['package_manager_url'], str) and helpers.is_github_url(
            dependent_row['package_manager_url']):
        return dependent_row['package_manager_url']
    else:
        return None


def get_dependent_libraries():
    dependent_libraries = pd.DataFrame()
    for library_short_name, library_detail in settings.LIBRARIES.items():
        for package in library_detail.packages:
            dependent_libraries = pd.concat([dependent_libraries, pd.read_csv(
                os.path.join(paths.DEPENDENT_LIBRARIES_DIRECTORY, package.dependents_file_name))])

    dependent_libraries = dependent_libraries.drop_duplicates()
    dependent_libraries['github_url'] = dependent_libraries.apply(lambda lib: get_github_url(lib), axis=1)
    dependent_libraries.to_csv(paths.DEPENDENT_LIBRARIES_FILE, index=False)

    return dependent_libraries


def get_dependent_applications():
    all_dependents = get_all_dependents()
    dependent_libraries = get_dependent_libraries()

    print(f'{len(all_dependents)} dependents and {len(dependent_libraries)} dependent libraries')

    dependent_github_urls = dependent_libraries['github_url'].values

    dependent_applications = all_dependents[~all_dependents['repository_url'].isin(dependent_github_urls)]
    return dependent_applications.drop_duplicates(subset=['repository_name', 'repository_url']).reset_index()


def get_application_detail(repository_name, index, total):
    print(f'{index + 1}|{total}')
    application_detail = helpers.get_repository_detail(repository_name)
    if application_detail:
        return [application_detail.full_name, application_detail.description, application_detail.topics,
                application_detail.clone_url, application_detail.created_at, application_detail.updated_at,
                application_detail.pushed_at, application_detail.language, application_detail.stargazers_count,
                application_detail.forks_count, application_detail.size]
    return [repository_name, None, None, None, None, None, None, None, None, None, None]


def list_application_libraries():
    print('Listing dependent applications...')
    dependent_applications = get_dependent_applications()
    print(f'{len(dependent_applications)} applications')

    apps = pd.DataFrame()
    apps['full_name'], apps['description'], apps['topics'], apps['clone_url'], apps['created_at'], apps['updated_at'], \
    apps['pushed_at'], apps['language'], apps['stars_count'], apps['forks_count'], apps['size'] = zip(
        *dependent_applications.apply(lambda d: get_application_detail(d['repository_name'], d.name,
                                                                       len(dependent_applications)), axis=1))

    apps.to_csv(paths.DEPENDENT_APPLICATION_FILE, index=False)


if __name__ == '__main__':
    list_application_libraries()
