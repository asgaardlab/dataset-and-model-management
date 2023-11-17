import os.path

import pandas as pd
import requests

from util import helpers, settings, paths


def get_saved_library_versions(saved_file_path):
    df = pd.read_csv(saved_file_path)
    return df['version'].values.tolist()


def get_library_releases_from_pypi(package_name):
    url = helpers.get_pypi_api_url(package_name)
    response = requests.get(url)
    if response.status_code == 200:
        releases = []
        package_releases = response.json()['releases']
        for version, uploads in package_releases.items():
            earliest_upload = uploads[0]
            releases.append([version, earliest_upload['upload_time'], earliest_upload['url'],
                             earliest_upload['yanked'], earliest_upload['yanked_reason']])
        return releases
    else:
        return []


def save_library_releases(releases, save_file_path):
    columns = ['version', 'published_at', 'file_url', 'is_yanked', 'yanked_reason']

    df = pd.DataFrame(releases, columns=columns)
    df = df.sort_values('published_at', ascending=False)
    df.to_csv(save_file_path, index=False)


def extract_libraries_releases():
    for library_short_name, library_detail in settings.LIBRARIES.items():
        for package in library_detail.packages:
            print(f'Getting {library_detail.title} versions from PyPI')
            library_releases = get_library_releases_from_pypi(package.release_name)
            os.makedirs(paths.LIBRARIES_RELEASES_DIRECTORY, exist_ok=True)
            save_file_path = os.path.join(paths.LIBRARIES_RELEASES_DIRECTORY, package.releases_file_name)
            save_library_releases(library_releases, save_file_path)


if __name__ == '__main__':
    extract_libraries_releases()
