import ast
import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta
from unidecode import unidecode

from data_processor.data_type.repository_type import Tutorial
from util import constants, helpers, paths


def is_tutorial_repository_by_topic(repository_topic_list):
    if repository_topic_list and isinstance(repository_topic_list, str):
        repository_topics = ast.literal_eval(repository_topic_list)
        is_tutorial = any(repository_topic in constants.EXCLUDING_TOPICS for repository_topic in repository_topics)
        return Tutorial.BY_TOPIC.value if is_tutorial else Tutorial.NOT_TUTORIAL.value
    return Tutorial.NOT_TUTORIAL.value


def remove_non_ascii(text):
    return unidecode(text)


def is_tutorial_repository_by_description(repository_description):
    if repository_description and isinstance(repository_description, str):
        if not repository_description.isascii():
            repository_description = remove_non_ascii(repository_description)

        description_words = helpers.preprocess_text(repository_description)
        lemmatized_description = ' '.join(description_words)
        is_tutorial_by_keyword = any(
            description_word in constants.EXCLUDING_KEYWORDS_FOR_TEXT for description_word in description_words)
        is_tutorial_by_substring = any(excluding_substring for excluding_substring
                                       in constants.EXCLUDING_SUBSTRINGS_FOR_DESCRIPTION
                                       if lemmatized_description.find(excluding_substring) > -1)
        return Tutorial.BY_DESCRIPTION.value if (is_tutorial_by_keyword or is_tutorial_by_substring) \
            else Tutorial.NOT_TUTORIAL.value

    return Tutorial.NOT_TUTORIAL.value


def is_tutorial_repository_by_name(repository_full_name):
    repository_name = repository_full_name.split('/')[1]
    if isinstance(repository_name, str):
        name_parts = helpers.preprocess_repo_name(repository_name)
        is_tutorial_by_keyword = any(name_part in constants.EXCLUDING_KEYWORDS_FOR_TEXT for name_part in name_parts)

        lemmatized_name = ' '.join(name_parts)
        is_tutorial_by_substring = any(excluding_substring for excluding_substring
                                       in constants.EXCLUDING_SUBSTRINGS_FOR_DESCRIPTION
                                       if lemmatized_name.find(excluding_substring) > -1)

        return Tutorial.BY_NAME.value if (is_tutorial_by_keyword or is_tutorial_by_substring) \
            else Tutorial.NOT_TUTORIAL.value
    return Tutorial.NOT_TUTORIAL.value


def is_tutorial_repository(repository):
    is_tutorial = is_tutorial_repository_by_topic(repository.topics)
    if is_tutorial == Tutorial.NOT_TUTORIAL.value:
        is_tutorial = is_tutorial_repository_by_name(repository.full_name)
    if is_tutorial == Tutorial.NOT_TUTORIAL.value:
        is_tutorial = is_tutorial_repository_by_description(repository.description)

    return is_tutorial


def filter_by_number_of_commits(repositories):
    return repositories[repositories['# of commits'] >= 100]


def filter_by_last_commit_date(repositories):
    six_months_early_date = datetime.date(2023, 2, 20) + relativedelta(months=-6)
    return repositories[pd.to_datetime(repositories['pushed_at']).dt.date >= six_months_early_date]


def filter_tutorial_repositories(repositories):
    return repositories[repositories['is_tutorial'] == Tutorial.NOT_TUTORIAL.value]


def filter_application_repositories():
    repositories = pd.read_csv(paths.DEPENDENT_APPLICATION_FILE)
    print(f'{len(repositories)} repositories before filtering')

    repositories['is_tutorial'] = repositories.apply(lambda repository: is_tutorial_repository(repository), axis=1)

    filtered_repositories = filter_by_number_of_commits(repositories)
    print(f'{len(filtered_repositories)} repositories after filtering by number of commits')

    filtered_repositories = filter_by_last_commit_date(filtered_repositories)
    print(f'{len(filtered_repositories)} repositories after filtering by last commit date')

    filtered_repositories = filter_tutorial_repositories(filtered_repositories)
    print(f'{len(filtered_repositories)} repositories after removing tutorials')

    repositories.to_csv(paths.DEPENDENT_APPLICATION_FILE, index=False)

    filtered_repositories = filtered_repositories.drop('is_tutorial', axis=1)
    filtered_repositories.to_csv(paths.FILTERED_DEPENDENT_APPLICATION_FILE, index=False)


if __name__ == '__main__':
    filter_application_repositories()

    # description = 'Code for http://lic2019.ccf.org.cn/kg 信息抽取。使用基于 BERT 的实体抽取和关系抽取的端到端的联合模型。'
    # is_tutorial = is_tutorial_repository_by_description(description)
    # print(is_tutorial)

    # repo_name = 'sarguido/hands-on-analysis-python'
    # is_tutorial = is_tutorial_repository_by_name(repo_name)
    # print(is_tutorial)
