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
Goal:

investigate whether adding noise to preference profiles might help aggregated utility scores.

Vision: profiles in practice follow (to confirm) mallows distributions. This is not ideal (more collisions).
Assumptions: introducing per-agent noise might help alleviate this.

Experiment design:
- to initial Mallows-distributed profiles (maybe identity profiles), we will add 
noise. The interpretation here is that one or both sides are given the original data + some minor
modification about the other side.
- we'll run GS on both the original profiles and the noisy ones.
- we'll compute the utilities of the final matchings, USING THE INITIAL PROFILES (regarded as TRUE here)

Metrics: getting higher aggregated utility in the noisy scenario is interpreted as a better solution.
Independent variables: the spread in initial population
"""

class Metric(Enum):
    STD = 1
    MAX = 2
    CORRELATION = 3
    GRID_MEAN = 4

class Noise_Type(Enum):
    RANDOM = 1
    LOCAL = 2

def noise_comparison(args, base_phi_sui, base_phi_rev):
    assert(args.noisy_side in {"suitors", "reviewers", "both"})
    #create profiles
    ref_sui = tuple(sorted([i for i in range(args.n)], key=lambda k: random.random()))
    ref_rev = tuple(sorted([i for i in range(args.n)], key=lambda k: random.random()))
    suitors = gs_utils.create_mallows_players(args.n, phi=base_phi_sui, ref=ref_sui)
    reviewers = gs_utils.create_mallows_players(args.n, phi=base_phi_rev, ref=ref_rev)
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
    _, init_borda_sui, init_borda_rev = gs_utils.run_gs(suitors, reviewers, rev_dict)

    #re run GS
    _, noisy_borda_sui, noisy_borda_rev = gs_utils.run_gs(noisy_suitors, noisy_reviewers, rev_dict)
    
    #compute utility of both
    #we've already got the utility of the first run
    #we need the utility of the second matching w respect to the original profile
    true_noisy_borda_sui = noise_utils.get_original_borda(noisy_suitors, suitors)
    true_noisy_borda_rev = noise_utils.get_original_borda(noisy_reviewers, reviewers)

    return init_borda_sui, init_borda_rev, true_noisy_borda_sui, true_noisy_borda_rev

def noise_run(args):
    assert(args.metric.upper() in [m.name for m in Metric])
    assert(args.noise_type.upper() in [m.name for m in Noise_Type])
    tick_range = range(args.ticks + 1)
    phis = [i / args.ticks for i in tick_range]
    path = "results/noise/"
    path = os.path.join(path, args.metric.lower())
    path = os.path.join(path, args.noisy_side)

    #create directory for this run
    path = os.path.join(path, str(datetime.now()))
    os.makedirs(path)

    #record arguments in directory as .json
    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    dictionary = {"commit_id" : sha}
    for key in vars(args):
        dictionary[str(key)] = getattr(args, key)

    with open(os.path.join(path, "args.json"), "w") as outfile:
        json.dump(dictionary, outfile, indent=4, sort_keys=True, default=lambda x: x.__name__)

    file_name = get_path_name(args)
    file_path = os.path.join(path, file_name)

    #run
    correlation_dict = dict()
    mean_dict_sui = dict()
    mean_dict_rev = dict()
    mean_dict_sum = dict()
    sex_eq_cost_dict = dict() #measures difference in SE cost init -> noisy
    for phi_sui in phis:
        temp_correlation_dict = dict()
        phi_to_diffs_sui = dict()
        phi_to_diffs_rev = dict()
        for phi_rev in phis:
            mean_borda_diff_sui = []
            mean_borda_diff_rev = []
            se_costs = []
            for _ in range(args.num_runs):
                init_sui, init_rev, noisy_sui, noisy_rev = noise_comparison(args, phi_sui, phi_rev)
                mean_init_sui, mean_init_rev = mean(init_sui), mean(init_rev)
                mean_noisy_sui, mean_noisy_rev = mean(noisy_sui), mean(noisy_rev)
                mean_borda_diff_sui.append(mean_noisy_sui - mean_init_sui)
                mean_borda_diff_rev.append(mean_noisy_rev - mean_init_rev)
                noisy_equality_cost = abs(mean_noisy_sui - mean_noisy_rev)
                init_equality_cost = abs(mean_init_sui - mean_init_rev)
                se_costs.append(noisy_equality_cost - init_equality_cost)


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
        temp_file_name = file_name + "_phi_sui_" + str(phi_sui)
        temp_file_path = file_path + "_phi_sui_" + str(phi_sui)
        if args.metric == Metric.STD.name:
            graph_mean_stdev_multiple([phi_to_diffs_sui, phi_to_diffs_rev], temp_file_name, temp_file_path, "phi rev", "Mean of Borda score diff", ["suitors", 'reviewers'])
        elif args.metric == Metric.MAX.name:
            graph_min_max_multiple([phi_to_diffs_sui, phi_to_diffs_rev], temp_file_name, temp_file_path, "phi rev", "Mean of Borda score diff", ["suitors", 'reviewers'])
    #if we're recording correlation, plot a grid of the correlations for each (phi_sui, phi_rev) pair
    if args.metric == Metric.CORRELATION.name:
        graph_grid(correlation_dict, "Correlation between suitor and reviewer differences in utility", os.path.join(path, "correlation_matrix"), (-1, 1), "phi_sui", "phi_rev")
    elif args.metric == Metric.GRID_MEAN.name:
        graph_grid(mean_dict_sui, "Mean of differences in suitor Borda scores", os.path.join(path, "mean_matrix_suitors"), None, "phi_sui", "phi_rev")
        graph_grid(mean_dict_rev, "Mean of differences in reviewer Borda scores", os.path.join(path, "mean_matrix_reviewers"), None, "phi_sui", "phi_rev")
        #3rd grid: sum of both sides' borda
        graph_grid(mean_dict_sum, "Mean of differences in all agents' Borda scores", os.path.join(path, "mean_matrix_sum_both"), None, "phi_sui", "phi_rev")
        #4th grid: SE cost difference
        graph_grid(sex_eq_cost_dict, "Difference in sex-equality cost", os.path.join(path, "mean_matrix_se_cost"), None, "phi_sui", "phi_rev")

            

def build_parser():

    parser = argparse.ArgumentParser()

    parser.add_argument('--metric', type=str, required=True, choices=[m.name for m in Metric])
    parser.add_argument('--n', type=int, default=15, required=True)
    parser.add_argument('--noisy_side', type=str, default="suitors", required=True)
    parser.add_argument('--num_runs', type=int, default=1000, required=True)
    parser.add_argument('--ticks', type=int, default=10)
    parser.add_argument('--noise_type', type=str, default="LOCAL", required=True, choices=[n.name for n in Noise_Type])
    parser.add_argument('--window_size', type=int)
    
    return parser

if __name__ == "__main__":
    parser = build_parser()

    args = parser.parse_args()

    noise_run(args)