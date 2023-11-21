import seaborn as sns
from matplotlib import pyplot as plt, rcParams


def plot_groups_and_save(plot_data, x_label, y_label, save_file_path, show_percentage=True, figure_width=6,
                         figure_height=3):
    with sns.axes_style('white'):
        fig = plt.figure(figsize=(figure_width, figure_height))
        ax = sns.barplot(data=plot_data, x='data', y='label', orient='h', color='C0')
        sns.despine(ax=ax, top=True, left=False, bottom=False, right=True)

    ax.bar_label(ax.containers[0])

    if show_percentage:
        for patch in ax.patches:
            if patch.get_width() == 0:
                continue

            percentage = round((patch.get_width() * 100.0) / plot_data['data'].sum())
            if percentage >= 13:
                x, y = patch.get_xy()
                x += (patch.get_width() - 1)
                y += patch.get_height() / 2
                ax.annotate(str(percentage) + '%', (x, y), ha='right', va='center', color='white')

    plt.xlabel(x_label)
    plt.ylabel(y_label)

    rcParams.update({'figure.autolayout': True})
    plt.autoscale()
    fig.tight_layout()

    fig.savefig(save_file_path, bbox_inches="tight")
    fig.show()


def plot_file_sizes_per_location_group(data, line_value, x_label, y_label, save_file_path):
    fig = plt.figure(figsize=(6, 3))
    with sns.axes_style('white'):
        fig.add_subplot()
        ax = sns.violinplot(data, x='data', y='label', cut=0, color='C0')
        sns.despine(ax=ax, top=True, right=True, left=False)

        line = ax.axvline(x=line_value, ymax=0.9, linewidth=2, linestyle='--')
        ax.text((line_value - 28), -0.35, f'{line_value} MB', color=line.get_color())
        plt.xscale('log')

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    fig.tight_layout()
    fig.savefig(save_file_path)
    plt.show()


def plot_stacked_bar(plot_data, x_label, y_label, legend_title, save_file_path):
    fig = plt.figure(figsize=(6.5, 3))

    with sns.axes_style('white'):
        ax = fig.add_subplot()
        ax = plot_data.plot.barh(stacked=True, width=0.8, color=['C0', sns.xkcd_rgb['cool grey']], ax=ax)
        sns.despine(ax=ax, top=True, left=False, bottom=False, right=True)

    total = 0
    for patch in ax.patches:
        total += patch.get_width()
        if patch.get_width() == 0:
            continue

        x, y = patch.get_xy()
        x += patch.get_width() - 1
        y += patch.get_height() / 2
        ax.annotate(str(int(patch.get_width())), (x, y), ha='right', va='center', color='white')

    for index in range(0, len(ax.containers[1].patches)):
        bar_total = 0
        for container in ax.containers:
            bar_total += container.patches[index].get_width()
        total_percentage = round((bar_total * 100.0) / total)

        if total_percentage >= 13:
            patch = ax.containers[1].patches[index]
            x, y = patch.get_xy()
            x += patch.get_width() + 1
            y += patch.get_height() / 2
            ax.annotate(str(total_percentage) + '%', (x, y), ha='left', va='center', color='black')

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend(title=legend_title)

    plt.tight_layout()

    plt.savefig(save_file_path)
    plt.show()


def plot_multi_bar_and_save(plot_data, x_label, y_label, legend_title, save_file_path):

    with sns.axes_style('white'):
        plt.figure(figsize=(6, 4))
        ax = sns.barplot(data=plot_data, x='data', y='label', hue='categories', orient='h', palette='Blues')
        sns.move_legend(
            ax, "lower center",
            bbox_to_anchor=(.5, 1), ncol=2, title=legend_title, frameon=False,
        )
        sns.despine(ax=ax, top=True, left=False, bottom=False, right=True)

    ax.bar_label(ax.containers[0])
    ax.bar_label(ax.containers[1])

    # total = 0
    # for patch in ax.patches:
    #     total += patch.get_width()
    #     if patch.get_width() == 0:
    #         continue
    #
    #     x, y = patch.get_xy()
    #     x += patch.get_width() - 1
    #     y += patch.get_height() / 2
    #     ax.annotate(str(int(patch.get_width())), (x, y), ha='right', va='center', color='white')
    #
    # for index in range(0, len(ax.containers[1].patches)):
    #     bar_total = 0
    #     for container in ax.containers:
    #         bar_total += container.patches[index].get_width()
    #     total_percentage = round((bar_total * 100.0) / total)
    #
    #     if total_percentage >= 13:
    #         patch = ax.containers[1].patches[index]
    #         x, y = patch.get_xy()
    #         x += patch.get_width() + 1
    #         y += patch.get_height() / 2
    #         ax.annotate(str(total_percentage) + '%', (x, y), ha='left', va='center', color='black')
    #
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    plt.tight_layout()

    plt.savefig(save_file_path)
    plt.show()


def plot_one_violin(data, x_label, save_file_path):
    sns.set_style('white')
    plt.figure(figsize=(6, 3))
    ax = sns.violinplot(x=data, cut=0)
    sns.despine(ax=ax, top=True, right=True, left=False)

    ax.set_xlabel(x_label)

    plt.tight_layout()

    plt.savefig(save_file_path)
    plt.show()

