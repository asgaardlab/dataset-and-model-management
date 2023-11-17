# An Exploratory Study of Dataset and Model Management in Open Source Machine Learning Applications
The 1st analysis of the management of dataset and model in ML applications

## Directory structure
```
├── data: all the data generated after running the scripts are saved in this directory
│   ├── all_dependents: list of ml repositories (dependents of the three libraries) per library
│   │   ├── *.csv
│   ├── candidate_code_lines: candidate code lines per repository
│   │   ├── **/*.csv
│   ├── dependent_libraries: list of libraries (dependent libraries of the libraries) per library
│   │   ├── *.csv
│   ├── library_releases: list of versions per libraries
│   │   ├── *.csv
│   ├── manual_analysis_result: manual analysis result
│   │   ├── supporting_files
│   │   │   ├── *.csv: files generated after result export
│   │   │   ├── *.yaml: helper files to generate manual analysis template for each repository 
│   │   ├── *.yaml
│   ├── all_dependents.csv: merged list of ml repositories from all_dependents/*.csv  
│   ├── data_files.csv: list of all data files found after manual analysis of the repositories
│   ├── data_files.xlsx: list of data files including after analysis result
│   ├── dependent_applications.csv: list of ml repositories after removing the libraries
│   ├── dependent_libraries.csv: merged list of libraries from dependent_libraries/*.csv
│   ├── file_path_with_#_of_commits.csv: list of data and model files saved in repositories including their number of commits in application repository history
│   ├── filtered_dependent_applications.csv: list of ml repositories after filtering
│   ├── model_files.csv: list of model files found after manual analysis of the repositories
│   ├── model_files.xlsx: list of model files including after analysis result
│   ├── repositories_for_manual_analysis.csv: list of repositories selected for manual analysis
│   ├── selected_repositories.csv: list of ml repositories after removing repositories using infrequent library versions
├── data_analyzer: scripts to analyze the data after collection
│   ├── *.py
├── data processor: scripts to collect and process data
│   ├── **/*.py
├── detector: scripts to generate candidate code lines
│   ├── **/*.py
├── result_analyzer: scripts to export result and visualize data
│   ├── *.py
├── util: common utility functions
│   ├── *.py
├── .gitignore
├── README.md 
└── requirements.txt
```

## Environment setup
```commandline
pip install -r requirements.txt
```

## Data preparation
From the repository root, run the following commands:

| Step | Command(s)                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Purpose                                                                                                       | Output                                      |
|------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|---------------------------------------------|
| 1    | <pre>python data_processor/library_dependents_collector.py --repo tensorflow/tensorflow --package_name tensorflow<br>python data_processor/library_dependents_collector.py --repo pytorch/pytorch --package_name torch<br>python data_processor/library_dependents_collector.py --repo scikit-learn/scikit-learn --package_name scikit-learn<br>python data_processor/library_dependents_collector.py --repo scikit-learn/scikit-learn --package_name sklearn<br></pre> | Collect the ML repositories (dependents of TensorFlow, PyTorch and Scikit-learn) from GitHub dependency graph | `data/all_dependents/*.csv`                 |
| 2    | `python data_processor/dependent_libraries_list_maker.py`                                                                                                                                                                                                                                                                                                                                                                                                               | Get the dependent libraries of TensorFlow, PyTorch and Scikit-learn from Libraries.io                         | `data/dependent_libraries/*.csv`            |
| 3    | `python data_processor/dependent_applications_list_maker.py`                                                                                                                                                                                                                                                                                                                                                                                                            | Remove the libraries from the ML repositories we get after step 1                                             | `data/dependent_applications.csv`           |
| 4    | `python data_processor/application_repositories_filterer.py`                                                                                                                                                                                                                                                                                                                                                                                                            | Filter the list by repository metadata (# of commits, last commit date and repository purpose)                | `data/filtered_dependent_applications.csv`  |
| 5    | `python data_processor/library_releases_extractor.py`                                                                                                                                                                                                                                                                                                                                                                                                                   | Get the list of available versions of TensorFlow, PyTorch and Scikit-learn                                    | `data/library_releases/*.csv`               |
| 6    | `python data_processor/requirements_file_downloader.py`                                                                                                                                                                                                                                                                                                                                                                                                                 | Get the requirements files of the repositories                                                                | `data/requirements_files/*`                 |
| 7    | `python data_processor/dependency_resolver.py`                                                                                                                                                                                                                                                                                                                                                                                                                          | Resolve the dependencies in the requirements files                                                            | `data/all_specifications.csv`               |
| 8    | `python data_processor/repositories_selector.py`                                                                                                                                                                                                                                                                                                                                                                                                                        | Select the repositories based on their used library version                                                   | `data/selected_repositories.csv`            |
| 9    | `python data_processor/repositories_for_manual_analysis_selector.py`                                                                                                                                                                                                                                                                                                                                                                                                    | Randomly select 93 repositories for manual analysis                                                           | `data/repositories_for_manual_analysis.csv` |
| 10   | `python data_processor/repositories_downloader.py`                                                                                                                                                                                                                                                                                                                                                                                                                      | Clone the selected repositories from GitHub                                                                   | `data/repositories_for_manual_analysis/*`   |
| 11   | `python detector/training_and_loading_detector.py`                                                                                                                                                                                                                                                                                                                                                                                                                      | Generate the candidate code lines                                                                             | `data/manual_analysis/*`                    |

## Result generation
### Manual analysis result
The result of the manual analysis is available in the `data/manual_analysis_result` directory. Each `yaml` file contains the analysis result of one repository. The `yaml` file name is the repository's name just replaced the `/` in the name with `@`. Run `python result_analyzer/manual_analysis_result_summary.py` to see the analysis summary.
### Result visualization
* Run `python result_analyzer/result_exporter.py` to export the manual analysis result in `csv` files and generate further results.
  * `model_train_analysis_result.csv`: List of model training code segments from all the repositories
  * `dataset_analysis_result.csv`: List of dataset loading code segments from all the repositories
  * `data_files`: Set of data files from all the repositories
  * `model_load_analysis_result.csv`: List of model loading code segments from all the repositories 
  * `model_files`: Set of model files from all the repositories
* Run the following commands to visualize the results:
  * `python result_analyzer/dataset_visualizer.oy`: results related to dataset loading code segments and data files 
  * `python result_analyzer/model_visualizer.py`: results related to model loading code segments and model files
  * `python result_analyzer/commit_visualizer.py`: results related to number of commits of data and model files saved in repositories
  * `python result_analyzer/file_path_ignore_analyzer.py`: results related to files saved in file system, ignored in repository
