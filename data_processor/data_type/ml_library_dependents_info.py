import logging

import pandas as pd
from bs4 import BeautifulSoup
from github_dependents_info import GithubDependentsInfo


def get_repository_url(repository_name):
    return 'https://github.com/' + repository_name


class MlLibraryDependentsInfo(GithubDependentsInfo):
    def __init__(self, repo, **options) -> None:
        super().__init__(repo, **options)
        self.package_name = options['package_name'] if 'package_name' in options else None
        self.save_file_path = options['save_file_path']

    def compute_packages(self):
        r = self.requests_retry_session().get(self.url_init)
        soup = BeautifulSoup(r.content, "html.parser")
        for a in soup.find_all("a", href=True):
            if a["href"].startswith(self.url_starts_with):
                package_id = a["href"].rsplit("=", 1)[1]
                package_name = a.find("span").text.strip()
                if "{{" in package_name:
                    continue
                if self.debug is True:
                    logging.info(package_name)
                if self.package_name and package_name == self.package_name:
                    self.packages += [{"id": package_id, "name": package_name}]
        if len(self.packages) == 0:
            self.packages = [{"id": None, "name": self.repo}]

    def save_result(self):
        data = self.result['packages'][0][0]['public_dependents']
        df = pd.json_normalize(data)
        df['repository_url'] = df.apply(lambda repo: get_repository_url(repo['name']), axis=1)
        df.to_csv(self.save_file_path, index=False, encoding='utf-8',
                  columns=['name', 'repository_url', 'stars'], header=['repository_name', 'repository_url', 'stars'])
