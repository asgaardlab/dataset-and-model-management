import os

from data_processor.library_releases_extractor import get_saved_library_versions
from data_processor.library_version_resolver import get_resolved_versions, search_libraries_in_lines, \
    save_specifications
from data_processor.data_type.resolved_version import Specification
from util import helpers, paths, settings


def get_library_specifications_from_requirements_files(data_dir, package_names: list[str]) -> list[Specification]:
    requirements_specifications = []

    for repo_index, repo_directory in enumerate(os.scandir(data_dir)):
        for req_file_index, req_file in enumerate(os.scandir(repo_directory)):
            print(f'[{repo_index}.{req_file_index}] {req_file.path}')

            requirements_file_lines = helpers.parse_requirements_file(req_file.path)
            specifications_in_file = search_libraries_in_lines(requirements_file_lines, package_names)

            for spec in specifications_in_file:
                spec.repository_name = helpers.get_repo_name_from_dir_name(repo_directory.name)
                spec.requirements_file_path = req_file.name

            requirements_specifications += specifications_in_file

    return requirements_specifications


def resolve_dependency():
    pypi_package_names = []
    libraries_versions = {}

    for library_short_name, library_detail in settings.LIBRARIES.items():
        for package in library_detail.packages:
            pypi_package_names.append(package.package_name)
            saved_file_path = os.path.join(paths.LIBRARIES_RELEASES_DIRECTORY, package.releases_file_name)
            libraries_versions[package.package_name] = get_saved_library_versions(saved_file_path)

    library_specifications = get_library_specifications_from_requirements_files(paths.REQUIREMENTS_FILES_DIRECTORY,
                                                                                pypi_package_names)

    print(f'Found {len(library_specifications)} specifications of the libraries')

    for specification in library_specifications:
        specification.resolved_versions = get_resolved_versions(libraries_versions[specification.package_name],
                                                                specification.specifier)
        if len(specification.resolved_versions) > 0:
            specification.resolved_version = specification.resolved_versions[0]
            specification.resolved_major_revision = specification.resolved_version.split('.')[0]

    save_specifications(library_specifications, paths.SAVED_SPECIFICATIONS_FILE)


if __name__ == '__main__':
    resolve_dependency()
