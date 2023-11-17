from packaging.specifiers import SpecifierSet


class Specification:
    def __init__(self, specification_string: str, package_name: str, specifier: SpecifierSet, repository_name: str = None,
                 requirements_file_path: str = None, resolved_versions: list[str] = None, resolved_version: str = None,
                 resolved_major_revision: str = None):
        self.specification_string: str = specification_string
        self.package_name: str = package_name
        self.specifier: SpecifierSet = specifier
        self.repository_name: str = repository_name
        self.requirements_file_path: str = requirements_file_path
        self.resolved_versions: list[str] = resolved_versions
        self.resolved_version: str = resolved_version
        self.resolved_major_revision: str = resolved_major_revision
