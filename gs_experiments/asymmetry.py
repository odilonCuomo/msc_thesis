import random
import statistics
import os
import sys
cwd = os.getcwd()
sys.path.append(cwd)
from diversity.stable_marriage import gale_shapley, players, borda_vals
from diversity.distributions import mallows
from utils.graph_vals import graph_mean_stdev
from utils.args import Args
import utils.args
import gs_utils

"""
#2 for a given n:
x = phi
y = mean and stddev Borda of both sides
"""

def asym_nb_prop(n, nb_runs, phi, noiseless_phi, noisy_side="suitors"):
    """
    Returns stats on the number of proposals for a given number of runs of the GS algorithm.
    One side has unanimous prefs, other has mallows
    """
    assert(noisy_side.lower() in {"suitors", "reviewers"})
    #create players & run GS nb_runs times
    nb_props = []
    for _ in range(nb_runs):
        #create players
        ref_sui = tuple(sorted([i for i in range(n)], key=lambda k: random.random()))
        ref_rev = tuple(sorted([i for i in range(n)], key=lambda k: random.random()))
        if noisy_side.lower() == "reviewers":
            suitors = gs_utils.create_mallows_players(n, noiseless_phi, ref_sui)
            reviewers = gs_utils.create_mallows_players(n, phi, ref=ref_rev)
        else:
            suitors = gs_utils.create_mallows_players(n, phi, ref_sui)
            reviewers = gs_utils.create_mallows_players(n, noiseless_phi, ref=ref_rev)
        rev_dict = {}
        for i, p in enumerate(reviewers):
            rev_dict[p.id] = i

        props, _, _ = gs_utils.run_gs(suitors, reviewers, rev_dict)
        nb_props.append(sum(props))

    return statistics.mean(nb_props), statistics.stdev(nb_props)

args = Args()
args.n = 15
args.ticks = 20
args.noisy_side = "suitors"
tick_range = range(args.ticks + 1)
dispersion_range = [i / args.ticks for i in tick_range]
args.num_runs = 1000
args.noiseless_phi = 1.0

stats = dict()

for phi in dispersion_range:
    #get stats
    (mean, stdev) = asym_nb_prop(args.n, args.num_runs, phi, args.noiseless_phi, noisy_side=args.noisy_side)
    #add to dictionary
    stats[phi] = (mean, stdev)

path = "asymmetry/one_sided/n15"
path = utils.args.get_path_name(path, args)

graph_mean_stdev(stats, path, "phi", "E[T_n]")