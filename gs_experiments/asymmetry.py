import random
from statistics import mean, stdev
import os
import sys
cwd = os.getcwd()
sys.path.append(cwd)
from diversity.stable_marriage import gale_shapley, players, borda_vals
from diversity.distributions import mallows
from utils.graph_vals import graph_mean_stdev, graph_mean_stdev_multiple
from utils.args import Args
import utils.args
import argparse
import gs_utils

def asymmetry_prop_borda(n, nb_runs, dispersion_range, noiseless_phi, noisy_side="suitors", borda=False):
    """
    Returns stats on the number of proposals and borda scores for suitors and reviewers for a given number of runs of the GS algorithm.
    One side has unanimous prefs, other has mallows
    """
    assert(noisy_side.lower() in {"suitors", "reviewers"})
    #create players & run GS nb_runs times
    stats = dict()
    borda_stats_sui = dict()
    borda_stats_rev = dict()

    for phi in dispersion_range:
        nb_props = []
        b_sui = []
        b_rev = []
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

            props, b_suitors, b_reviewers = gs_utils.run_gs(suitors, reviewers, rev_dict)
            nb_props.append(sum(props))
            b_sui.append(mean(b_suitors))
            b_rev.append((mean(b_reviewers)))
        stats[phi] = (mean(nb_props), stdev(nb_props))
        borda_stats_sui[phi] = (mean(b_sui), stdev(b_sui))
        borda_stats_rev[phi] = (mean(b_rev), stdev(b_rev))
    return stats, borda_stats_sui, borda_stats_rev

if __name__ == "__main__":
    args = Args()
    args.n = 15
    args.ticks = 20
    args.noisy_side = "reviewers"
    tick_range = range(args.ticks + 1)
    dispersion_range = [i / args.ticks for i in tick_range]
    args.num_runs = 1000
    args.noiseless_phi = 0.75
    args.borda = True
    path = "results/asymmetry/borda/suitors"

    stats, borda_stats_sui, borda_stats_rev = asymmetry_prop_borda(args.n, args.num_runs, dispersion_range, args.noiseless_phi, noisy_side=args.noisy_side, borda=args.borda)

    if not os.path.isdir(path):
        os.mkdir(path)
    file_name = utils.args.get_path_name(args)
    file_path = os.path.join(path, file_name)

    if not args.borda:
        graph_mean_stdev(stats, file_name, file_path, "phi", "E[T_n]")
    else:
        graph_mean_stdev_multiple([borda_stats_sui, borda_stats_rev], file_name + "_borda_scores", file_path, "phi", "Mean of Borda scores", ["suitors borda", 'reviewers borda'])
