import csv
import matplotlib.pyplot as plt

def graph_mean_stdev(dispersion_stats, save_name, x_label, y_label):
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

    plt.savefig('results/' + save_name + ".png")
    plt.show()

    header = ['dispersion', 'mean', 'stddev']
    data = [[disp, mean, stddev] for (disp, (mean, stddev)) in list(dispersion_stats.items())]

    with open('results/' + save_name + '.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerows(data)