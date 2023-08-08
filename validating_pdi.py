import statistics
from preflibtools.instances.sampling import *
from diversity.pdi import *
import csv
import matplotlib.pyplot as plt

def pdi_on_mallows(num_voters, num_alternatives, pdi, dispersion_range, n_runs):
    """ return a dictionary of the mean+variance of pdis for each dispersion. All runs will use the same parameters, only the dispersion will vary
            the reference order used for mallows is the same for all runs and dispersions: increasing in id of alternatives
        :param num_voters: says on the tin. 
        :type num_voters: int
        :param num_alternatives: those that voters order
        :type num_alternatives: int
        :param pdi: pdi function
        :type pdi: function
        :param dispersion_range: list of values (floats) to be used in the mallows model generation
        :type pdi: list
        :param n_runs: number of times pdi will be measured for each dispersion value
        :type n_runs: int
        :return: dictionary of the mean and variance of pdis for each dispersion value in the range
        :rtype: dict
    """
    res = dict()
    for dispersion in dispersion_range:
        pdi_values = [] #stores pdis for this 
        for r in range(n_runs):
            #generate mallows model distribution
            reference_order = tuple((i) for i in range(num_alternatives)) #order expressed as tuple of ints
            profile = generate_mallows(num_voters, num_alternatives, [1], [dispersion], [reference_order])
            #compute pdi
            diversity = pdi.of(profile)
            pdi_values.append(diversity)
        #compute statistics
        mean = statistics.mean(pdi_values)
        variance = statistics.stdev(pdi_values)
        res[dispersion] = (mean, variance)
    return res
            
def graph_vals(dispersion_stats, save_name, x_label, y_label):
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