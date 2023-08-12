import csv
import numpy as np
import matplotlib.pyplot as plt

def graph_grid(grid_stats, save_name, save_path, x_label, y_label):
    """
    """
    dispersions = list(grid_stats.keys())
    vals = list(grid_stats.values())

    fig = plt.figure(figsize = (10, 5))
    plt.plot(dispersions, vals)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(save_name)

    plt.savefig(save_path + ".png")
    plt.show()

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