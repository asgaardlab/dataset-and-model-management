import os

import pandas as pd
from packaging.specifiers import Specifier, SpecifierSet
from pandas import DataFrame

from data_processor.library_releases_extractor import get_saved_library_versions
from data_processor.data_type.resolved_version import Specification
from util import helpers, paths, settings


def search_libraries_in_lines(specification_lines: list[str], search_library_names: list[str]) -> list[Specification]:
    library_specifications_in_file = []

    for line in specification_lines:
        req = helpers.get_requirement(line)
        if req and req.name and req.name.lower().replace('_', '-') in search_library_names:
            library_specifications_in_file.append(
                Specification(line, req.name.lower().replace('_', '-'), req.specifier))

    return library_specifications_in_file


def get_library_specifications_from_requirements_files(data_dir, package_names: list[str]) -> list[Specification]:
    requirements_specifications = []
    requirements_files = helpers.get_requirements_file_paths(data_dir)

    for index, row in requirements_files.iterrows():
        print(f'[{index + 1}|{len(requirements_files)}] {row.requirements_file_path}')
        requirements_file_lines = helpers.parse_requirements_file(row.requirements_file_path)
        specifications_in_file = search_libraries_in_lines(requirements_file_lines, package_names)

        for spec in specifications_in_file:
            spec.repository_name = row.repository_name
            spec.requirements_file_path = row.requirements_file_relative_path

        requirements_specifications += specifications_in_file

    return requirements_specifications


def get_resolved_versions(library_versions: list[str], specifiers: SpecifierSet) -> list[str]:
    if len(specifiers) == 1:
        specifier = Specifier(str(specifiers))
        if specifier.operator == '==':
            if specifier.version[0] == 'v':
                return [specifier.version[1:]]
            return [specifier.version]
    return list(specifiers.filter(library_versions, prereleases=True))


def get_latest_version(versions: list[str], sorted_library_versions: DataFrame):
    sorted_resolved_versions = sorted_library_versions[sorted_library_versions['version'].isin(versions)]
    return sorted_resolved_versions['version'].values[0]


def save_specifications(specifications: list[Specification], save_file_path):
    specification_list = [
        [spec.repository_name, spec.requirements_file_path, spec.specification_string, spec.package_name,
         spec.specifier, spec.resolved_versions, spec.resolved_version, spec.resolved_major_revision] for spec in
        specifications]

    pd.DataFrame(specification_list,
                 columns=['repository_name', 'requirements_file_path', 'specification', 'package_name', 'specifier',
                          'resolved_versions', 'resolved_version', 'resolved_major_revision']).to_csv(save_file_path,
                                                                                                      index=False)


def resolve_library_version():
    pypi_package_names = []
    libraries_versions = {}

    for library_short_name, library_detail in settings.LIBRARIES.items():
        for package in library_detail.packages:
            pypi_package_names.append(package.package_name)
            saved_file_path = os.path.join(paths.LIBRARIES_RELEASES_DIRECTORY, package.releases_file_name)
            libraries_versions[package.package_name] = get_saved_library_versions(saved_file_path)

    library_specifications = get_library_specifications_from_requirements_files(paths.REPOSITORIES_DIRECTORY,
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
    resolve_library_version()
