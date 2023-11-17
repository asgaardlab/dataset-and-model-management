import argparse
import logging
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))


def collect_library_dependents(
        repo: str,
        package_name: str,
        min_stars: int | None,
        sort_key: str | None,
        verbose: bool,
        save_file_path: str
) -> None:
    if verbose is True:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    if repo is None:
        raise ValueError('repo argument is mandatory')
    if package_name is None:
        raise ValueError('package_name argument is mandatory')
    else:
        if min_stars is None:
            min_stars = 0
        if sort_key is None:
            sort_key = 'name'
        if save_file_path is None:
            save_file_path = f'{package_name}_dependents.csv'
        from data_processor.data_type.ml_library_dependents_info import MlLibraryDependentsInfo
        gh_deps_info = MlLibraryDependentsInfo(
            repo,
            debug=verbose,
            sort_key=sort_key,
            min_stars=min_stars,
            package_name=package_name,
            save_file_path=save_file_path
        )
        gh_deps_info.collect()
        gh_deps_info.save_result()


def main():
    parser = argparse.ArgumentParser(description='Github repository dependents collector',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--repo', help='Github repository full name')
    parser.add_argument('--package_name', help='Name of the package to collect dependents')
    args = parser.parse_args()

    dependents_file_name = f'{args.package_name}_dependents.csv'
    from util import paths

    os.makedirs(paths.ALL_DEPENDENTS_DIRECTORY, exist_ok=True)
    save_file_path = os.path.join(paths.ALL_DEPENDENTS_DIRECTORY, dependents_file_name)

    collect_library_dependents(repo=args.repo, package_name=args.package_name,
                               min_stars=10, sort_key='stars', verbose=True,
                               save_file_path=save_file_path)


if __name__ == '__main__':
    main()
    # python library_dependents_collector.py --repo tensorflow/tensorflow --package_name tensorflow
    # python library_dependents_collector.py --repo pytorch/pytorch --package_name torch
    # python library_dependents_collector.py --repo scikit-learn/scikit-learn --package_name scikit-learn
    # python library_dependents_collector.py --repo scikit-learn/scikit-learn --package_name sklearn
