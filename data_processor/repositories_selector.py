import pandas as pd

from util import settings, paths


def get_selected_repository_names():
    specifications = pd.read_csv(paths.SAVED_SPECIFICATIONS_FILE, dtype=str)

    repository_names = pd.Series(dtype=pd.StringDtype())
    for library_short_name, library_detail in settings.LIBRARIES.items():
        package_names = [package.package_name for package in library_detail.packages]
        repositories_with_library_specifications = specifications[
            specifications['package_name'].isin(package_names)]
        repositories_use_latest_major_revision = repositories_with_library_specifications[
            repositories_with_library_specifications['resolved_major_revision'].isin(
                library_detail.working_major_revisions)]
        repository_names = pd.concat([repository_names, repositories_use_latest_major_revision['repository_name']],
                                     ignore_index=True)
    return repository_names.drop_duplicates().values


def select_repositories():
    selected_repository_names = get_selected_repository_names()

    repositories = pd.read_csv(paths.FILTERED_DEPENDENT_APPLICATION_FILE)
    repositories = repositories[repositories['full_name'].isin(selected_repository_names)]
    print(f'{len(repositories)} repositories selected')

    repositories.to_csv(paths.SELECTED_REPOSITORIES_FILE, index=False)


if __name__ == '__main__':
    select_repositories()
