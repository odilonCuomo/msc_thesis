import csv
import matplotlib.pyplot as plt

def graph_mean_stdev(dispersion_stats, save_name, save_path, x_label, y_label):
    """ graphs out the mean and variance of pdi results over different dispersion values.
            Saves the graph and stats to a given output path.
        :param dispersion_stats: dictionary mapping dispersions to statistics
        :type dispersion_stats: dict
    """
    dispersions = list(dispersion_stats.keys())
    pairs = list(dispersion_stats.values())
    means, stddev = zip(*pairs)

    fig = plt.figure(figsize = (15, 5))
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
#    [list(dictionary.keys()) for dictionary in dispersion_stats]
    pairs = [list(dictionary.values()) for dictionary in dispersion_stats]
    mean_std = [list(zip(*pair)) for pair in pairs]


    fig = plt.figure(figsize = (15, 5))
    for i in range(len(dispersion_stats)):
        mean, stddev = mean_std[i]
        plt.errorbar(dispersions, mean, stddev, linestyle='None', marker='^', capsize=3)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(save_name)
    plt.legend(names)


    plt.savefig(save_path + ".png")
    plt.show()

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
""" 
x = [1, 2, 3]
m1 = [2.2, 3.3, 4.4]
std1 = [0.5, 0.4, 0.34]
m2 = [3.2, 5.3, 6.4]
std2 = [0.2, 0.1, 0.3]
stat1 = {x[i]: (m1[i], std1[i]) for i in range(3)}
stat2 = {x[i]: (m2[i], std2[i]) for i in range(3)}
stats = [stat1, stat2]

graph_mean_stdev_multiple(stats, "yessaie", "phi", "muscle", ["d1", "d2"]) """