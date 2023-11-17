import os.path

import pandas as pd

from result_analyzer.common_plots import plot_groups_and_save
from util import paths


def visualize_model_file_extension():
    file_extension_frequencies = pd.read_csv(os.path.join(paths.DATA_DIRECTORY, 'model_file_extensions.csv'))
    file_extension_frequencies = file_extension_frequencies.sort_values('data', ascending=False)

    graph_save_root = os.path.join(paths.DATA_DIRECTORY, 'graphs', 'plots_on_model')
    plot_groups_and_save(file_extension_frequencies, '# of pre-trained model files',
                         'Model file extensions', os.path.join(graph_save_root, 'model_file_extensions.pdf'),
                         show_percentage=False, figure_height=6)


if __name__ == '__main__':
    visualize_model_file_extension()
