class PackageDetail:
    def __init__(self, package_name: str, release_name: str):
        self.package_name = package_name
        self.release_name = release_name
        self.releases_file_name = f'{package_name}_releases.csv'
        self.dependents_file_name = f'{package_name}_dependents.csv'
