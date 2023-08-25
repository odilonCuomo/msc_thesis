import copy, os, sys, random, json, git, argparse
cwd = os.getcwd()
sys.path.append(cwd)
import gs_utils, noise_utils
from utils.args import Args, get_path_name
from utils.graph_vals import *

from enum import Enum
import numpy as np
from statistics import mean, stdev
from datetime import datetime

"""
Study of the effect of different preference bound lengths for both men and women
"""

class Metric(Enum):
    STD = 1
    MAX = 2
    CORRELATION = 3
    GRID_MEAN = 4

class Noise_Type(Enum):
    RANDOM = 1
    LOCAL = 2

def truncate_prefs(players, bound):
    for p in players:
        prefs = p.prefs
        prefs = prefs[: bound]
        p.prefs = prefs

def count_unmatched(players):
    unmatched = 0
    for p in players:
        if p.matching is None:
            unmatched += 1
    return unmatched

def noise_comparison(args, base_phi_sui, base_phi_rev):
    assert(args.noisy_side in {"suitors", "reviewers", "both"})
    #create profiles
    ref_sui = tuple(sorted([i for i in range(args.n)], key=lambda k: random.random()))
    ref_rev = tuple(sorted([i for i in range(args.n)], key=lambda k: random.random()))
    suitors = gs_utils.create_mallows_players(args.n, phi=base_phi_sui, ref=ref_sui)
    reviewers = gs_utils.create_mallows_players(args.n, phi=base_phi_rev, ref=ref_rev)
    truncate_prefs(suitors, args.prefs_bound_sui)
    truncate_prefs(reviewers, args.prefs_bound_rev)
    rev_dict = dict()
    for i, p in enumerate(reviewers):
        rev_dict[p.id] = i

    #add noise
    if args.noisy_side == "suitors":
        noisy_suitors = noise_utils.add_noise(suitors, 0, args.window_size, 1, window_start_min=0, noise_type=args.noise_type)
        noisy_reviewers = copy.deepcopy(reviewers)
    elif args.noisy_side == "reviewers":
        noisy_suitors = copy.deepcopy(suitors)
        #start at 1 given theorem 5 in Ms Machiavelli paper (not first choice in pref list => strictly dominated)
        noisy_reviewers = noise_utils.add_noise(reviewers, 0, args.window_size, 1, window_start_min=1, noise_type=args.noise_type)
    else: #add noise to both
        noisy_suitors = noise_utils.add_noise(suitors, 0, args.window_size, 1, window_start_min=0, noise_type=args.noise_type)
        noisy_reviewers = noise_utils.add_noise(reviewers, 0, args.window_size, 1, window_start_min=1, noise_type=args.noise_type)

    #run GS on initial profiles
    _, init_borda_sui, init_borda_rev = gs_utils.run_gs_premium(suitors, reviewers, rev_dict, args.matched_premium)

    #re run GS
    _ = gs_utils.run_gs(noisy_suitors, noisy_reviewers, rev_dict)
    
    #compute utility of both
    #we've already got the utility of the first run
    #we need the utility of the second matching w respect to the original profile
    true_noisy_borda_sui = noise_utils.get_original_borda_premium(noisy_suitors, suitors, args.matched_premium)
    true_noisy_borda_rev = noise_utils.get_original_borda_premium(noisy_reviewers, reviewers, args.matched_premium)

    #compute the number of unmatched men/women
    init_unmatched = count_unmatched(suitors)
    noisy_unmatched = count_unmatched(noisy_suitors)

    return init_borda_sui, init_borda_rev, true_noisy_borda_sui, true_noisy_borda_rev, init_unmatched, noisy_unmatched

def noise_run(args):
    assert(args.metric.upper() in [m.name for m in Metric])
    assert(args.noise_type.upper() in [m.name for m in Noise_Type])
    tick_range = range(args.ticks + 1)
    phis = [i / args.ticks for i in tick_range]
    path = "results/noise/"
    path = os.path.join(path, "incomplete")
    path = os.path.join(path, "bound_study")
    path = os.path.join(path, args.noisy_side)
    path = os.path.join(path, args.noise_type)

    #create directory for this run
    path = os.path.join(path, args.run_dir)

    #run
    correlation_dict = dict()
    mean_dict_sui = dict()
    mean_dict_rev = dict()
    mean_dict_sum = dict()
    sex_eq_cost_dict = dict() #measures difference in SE cost init -> noisy
    unmatched_diff_dict = dict()
    for phi_sui in phis:
        temp_correlation_dict = dict()
        phi_to_diffs_sui = dict()
        phi_to_diffs_rev = dict()
        for phi_rev in phis:
            mean_borda_diff_sui = []
            mean_borda_diff_rev = []
            se_costs = []
            unmatched_diffs = []
            for _ in range(args.num_runs):
                init_sui, init_rev, noisy_sui, noisy_rev, init_unmatched, noisy_unmatched = noise_comparison(args, phi_sui, phi_rev)
                mean_init_sui, mean_init_rev = mean(init_sui), mean(init_rev)
                mean_noisy_sui, mean_noisy_rev = mean(noisy_sui), mean(noisy_rev)
                mean_borda_diff_sui.append(mean_noisy_sui - mean_init_sui)
                mean_borda_diff_rev.append(mean_noisy_rev - mean_init_rev)
                noisy_equality_cost = abs(mean_noisy_sui - mean_noisy_rev)
                init_equality_cost = abs(mean_init_sui - mean_init_rev)
                se_costs.append(noisy_equality_cost - init_equality_cost)
                unmatched_diffs.append((noisy_unmatched - init_unmatched) * 2)


            #plot results
            if args.metric == Metric.STD.name:
                phi_to_diffs_sui[phi_rev] = (mean(mean_borda_diff_sui), stdev(mean_borda_diff_sui))
                phi_to_diffs_rev[phi_rev] = (mean(mean_borda_diff_rev), stdev(mean_borda_diff_rev))
            elif args.metric == Metric.MAX.name:
                phi_to_diffs_sui[phi_rev] = (mean(mean_borda_diff_sui), max(mean_borda_diff_sui), min(mean_borda_diff_sui))
                phi_to_diffs_rev[phi_rev] = (mean(mean_borda_diff_rev), max(mean_borda_diff_rev), min(mean_borda_diff_rev))
            elif args.metric == Metric.CORRELATION.name:
                corr_coef = np.corrcoef(mean_borda_diff_sui, mean_borda_diff_rev)
                correlation_dict[(phi_sui, phi_rev)] = corr_coef[0][1] #get correct element from Pearson correlation matrix
                temp_correlation_dict[phi_rev] = corr_coef[0][1]
            else: #grid mean
                mean_sui, mean_rev = mean(mean_borda_diff_sui), mean(mean_borda_diff_rev)
                mean_dict_sui[(phi_sui, phi_rev)] = mean_sui
                mean_dict_rev[(phi_sui, phi_rev)] = mean_rev
                mean_dict_sum[(phi_sui, phi_rev)] = mean_sui + mean_rev
                sex_eq_cost_dict[(phi_sui, phi_rev)] = mean(se_costs)
                unmatched_diff_dict[(phi_sui, phi_rev)] = mean(unmatched_diffs)

    grid_stats = unmatched_diff_dict
    #write to csv the grid values
    header = ["phi_men, phi_women", "diff_unmatched"]
    data = [[disp, v] for (disp, v) in list(grid_stats.items())]

    tag = "b_sui_" + str(args.prefs_bound_sui) + "_b_rev_" + str(args.prefs_bound_rev)
    csv_path = os.path.join(path, tag)
    with open(csv_path + '.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerows(data)

def build_parser():

    parser = argparse.ArgumentParser()

    parser.add_argument('--metric', type=str, required=True, choices=[m.name for m in Metric])
    parser.add_argument('--n', type=int, default=15, required=True)
    parser.add_argument('--noisy_side', type=str, default="suitors", required=True)
    parser.add_argument('--prefs_bound_sui', type=int, default=10, required=True)
    parser.add_argument('--prefs_bound_rev', type=int, default=10, required=True)
    parser.add_argument('--num_runs', type=int, default=1000, required=True)
    parser.add_argument('--ticks', type=int, default=10)
    parser.add_argument('--noise_type', type=str, default="LOCAL", required=True, choices=[n.name for n in Noise_Type])
    parser.add_argument('--window_size', type=int)
    parser.add_argument('--matched_premium', type=int, default=0, required=True)
    parser.add_argument('--run_dir', type=str, default=0, required=True)
    
    return parser

if __name__ == "__main__":
    parser = build_parser()

    args = parser.parse_args()

    noise_run(args)