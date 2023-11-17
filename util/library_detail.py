from util.api_detail import ApiDetail
from util.package_detail import PackageDetail


class LibraryDetail:
    def __init__(self, title: str, github_repository_full_name: str, packages: list[PackageDetail],
                 working_major_revisions: list[str], training_api: list[ApiDetail],
                 model_loading_api: list[ApiDetail]):
        self.title = title
        self.github_repository_full_name = github_repository_full_name
        self.packages = packages
        self.working_major_revisions = working_major_revisions
        self.training_apis: list[ApiDetail] = training_api
        self.model_loading_apis: list[ApiDetail] = model_loading_api
