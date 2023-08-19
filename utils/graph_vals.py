import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.ticker import FormatStrFormatter

def graph_grid(grid_stats, title, save_path, min_max, x_label, y_label):
    """
    Creates a matrix plot of the given grid of values. Will colormap each cell in the matrix on a scale 
    defined by min_max = (min, max)
    """
    #create map: [0,1] -> RGB
    #viridis = mpl.colormaps['viridis'].resampled(nb_cells)

    dispersions = list(grid_stats.keys())
    x, y = zip(*dispersions)
    x, y = list(set(x)), list(set(y))
    x.sort()
    y.sort()
    nb_cells = len(x)
    xy_vals = np.array([[grid_stats[(i, j)] for j in y] for i in x]).transpose()
    fig, ax = plt.subplots()
    fig.set_size_inches(15, 10)
    if min_max is not None: 
        min_val, max_val = min_max
        mat = ax.matshow(xy_vals, cmap=plt.cm.Blues, vmin=min_val, vmax=max_val, origin="lower")
    else:
        mat = ax.matshow(xy_vals, cmap=plt.cm.Blues, origin="lower")

    for i in range(nb_cells):
        for j in range(nb_cells):
            c = xy_vals[j][i]
            ax.text(i, j, str(round(c, 2)), va='center', ha='center')

    plt.xticks(range(nb_cells), [f"{i:.2f}" for i in x])
    plt.yticks(range(nb_cells), [f"{i:.2f}" for i in y])
    #ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    # Set ticks on both sides of axes on
    ax.tick_params(axis="x", bottom=True, top=False, labelbottom=True, labeltop=False)
    plt.colorbar(mat, ax=ax)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    
    plt.savefig(save_path + ".png")
    
    #save to .csv
    header = [x_label, y_label]
    data = [[disp, v] for (disp, v) in list(grid_stats.items())]

    with open(save_path + '.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerows(data)

def graph_plt_plot(grid_stats, save_name, save_path, x_label, y_label):
    """
    graphs out the given stats as a simple 2D plot. Saves the graph and stats to a given output path.
        :param grid_stats: dictionary mapping x to y
        :type grid_stats: dict
    """
    dispersions = list(grid_stats.keys())
    vals = list(grid_stats.values())

    fig = plt.figure(figsize = (40, 20))
    plt.plot(dispersions, vals)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(save_name)

    plt.savefig(save_path + ".png")

    header = [x_label, y_label]
    data = [[disp, v] for (disp, v) in list(grid_stats.items())]

    with open(save_path + '.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerows(data)

def graph_mean_stdev(dispersion_stats, save_name, save_path, x_label, y_label):
    """ graphs out the mean and variance of pdi results over different dispersion values.
            Saves the graph and stats to a given output path.
        :param dispersion_stats: dictionary mapping dispersions to statistics
        :type dispersion_stats: dict
    """
    dispersions = list(dispersion_stats.keys())
    pairs = list(dispersion_stats.values())
    means, stddev = zip(*pairs)

    fig = plt.figure(figsize = (10, 5))
    plt.errorbar(dispersions, means, stddev, linestyle='None', marker='^', capsize=3)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(save_name)

    plt.savefig(save_path + ".png")
    plt.show()

    header = ['dispersion', 'mean', 'stddev']
    data = [[disp, mean, stddev] for (disp, (mean, stddev)) in list(dispersion_stats.items())]

    with open(save_path + '.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerows(data)

def graph_mean_stdev_multiple(dispersion_stats, save_name, save_path, x_label, y_label, names):
    """ graphs out the mean and variance of pdi results over different dispersion values.
            Saves the graph and stats to a given output path.
        :param dispersion_stats: dictionary mapping dispersions to statistics. Supposes they all have same dispersion list;
        :type dispersion_stats: dict
    """
    #dispersion stats = [(dict x => (mean, stdev))]
    dispersions = list(dispersion_stats[0].keys())
    pairs = [list(dictionary.values()) for dictionary in dispersion_stats]
    mean_std = [list(zip(*pair)) for pair in pairs]

    fig = plt.figure(figsize = (10, 5))
    for i in range(len(dispersion_stats)):
        mean, stddev = mean_std[i]
        plt.errorbar(dispersions, mean, stddev, linestyle='None', marker='^', capsize=3)

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(save_name)
    plt.legend(names)
    plt.grid()

    plt.savefig(save_path + ".png")
    #plt.show()

    header = ["dispersion"]
    for n in names:
        header.append(n + "_mean")
        header.append(n + "_stdev")
    data = [[d] for d in dispersions]
    for i, line in enumerate(data):
        for ms_dataset in mean_std:
            m, s = ms_dataset
            line.extend([m[i], s[i]])
    #data = [[disp, mean, stddev] for (disp, (mean, stddev)) in list(dispersion_stats.items())]

    with open(save_path + '.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerows(data)

def graph_mean_stdev_groups(dispersion_stats, save_name, save_path, x_label, y_label, group_names, element_names):
    """Graphs out mean and variance stats, when data is spread into multiple groups of equal size. Each group
        holds the same set of types of time series.
        Saves the graph and stats to a given output path.
        :param dispersion_stats: dict group_id => (dict series_id => (dict key => (mean, stdev)));
        :type dispersion_stats: dict
    """
    num_groups = len(group_names)
    xs = list(dispersion_stats[0][0].keys())
    """ pairs = [list(dictionary.values()) for dictionary in dispersion_stats]
    mean_std = [list(zip(*pair)) for pair in pairs] """

    #format needed: list of dictionaries
    all_pairs = [[dispersion_stats[j][i] for j in range(3)] for i in range(num_groups)]

    for j in range(num_groups):
        plt.subplot(1, num_groups, j + 1)
        current_triplet = all_pairs[j]

        for i in range(len(dispersion_stats)):
            current_pairs = list(current_triplet[i].values())
            mean, stddev = list(zip(*current_pairs))
            plt.errorbar(xs, mean, stddev, linestyle='None', marker='^', capsize=3)

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(group_names[j])
        plt.legend(element_names)

    cs = ["blue", "red"]
    markers = ['^', '*', "x"]
    plt.suptitle(save_name)
    plt.savefig(save_path + ".png")
    plt.show()

    header = [x_label]
    #order of headings: group_name > intra_group names > mean > stdev
    for gn in group_names:
        for n in element_names:
            header.append(n + gn + "_mean")
            header.append(n + gn + "_stdev")
    data = [[d] for d in xs]
    for i, line in enumerate(data):
        for gn in range(len(group_names)):
            for j in range(3):
                m, s = dispersion_stats[j][gn][xs[i]]
                line.extend([m, s])

    with open(save_path + '.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerows(data)

def graph_pairs_and_save(stats, file_name, file_path, x_label, y_label):
    """
    stats: list of (x, y) tuples
    This functions creates a point cloud graph of these tuples and saves it to the given path,
    and saves a csv to the same path.
    """
    xs, ys = list(zip(*stats))
    fig = plt.figure(figsize = (10, 5))
    plt.plot(xs, ys, 'o')

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(file_name)
    plt.savefig(file_path + ".png")
    #plt.show()

    #create and save to csv
    header = [x_label, y_label]
    data = [[d] for d in xs]
    for i, line in enumerate(data):
        line.append(ys[i])

    with open(file_path + '.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerows(data)

def graph_min_max_multiple(dispersion_stats, save_name, save_path, x_label, y_label, names):
    """ 
    Same as the graph_mean_stdev_multiple function, but accepts asymmetrical error bar values (min & max)
    Saves the graph and stats to a given output path.
        :param dispersion_stats: dictionary mapping dispersions to statistics. Supposes they all have same dispersion list;
            format: [(dict x => (mean, max, min))]
        :type dispersion_stats: dict
    """
    dispersions = list(dispersion_stats[0].keys())
    triples = [list(dictionary.values()) for dictionary in dispersion_stats]
    mean_max_min = [list(zip(*triplet)) for triplet in triples]

    plt.figure(figsize = (10, 5))
    for i in range(len(dispersion_stats)):
        mean, max, min = mean_max_min[i]
        min = [mean[i] - m for i, m in enumerate(min)]
        max = [m - mean[i] for i, m in enumerate(max)]
        err_bars = [min, max]
        plt.errorbar(dispersions, mean, err_bars, linestyle='None', marker='^', capsize=3)

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(save_name)
    plt.legend(names)
    plt.grid()

    plt.savefig(save_path + ".png")
    #plt.show()

    header = ["dispersion"]
    for n in names:
        header.append(n + "_mean")
        header.append(n + "_max")
        header.append(n + "_min")
    data = [[d] for d in dispersions]
    for i, line in enumerate(data):
        for ms_dataset in mean_max_min:
            mean, max, min = ms_dataset
            line.extend([mean[i], max[i], min[i]])

    with open(save_path + '.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerows(data)