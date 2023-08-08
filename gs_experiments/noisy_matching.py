import copy, os, sys, random
cwd = os.getcwd()
sys.path.append(cwd)
import gs_utils, noise_utils
from utils.args import Args, get_path_name
from statistics import mean, stdev
from utils.graph_vals import graph_mean_stdev_multiple, graph_min_max_multiple
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


def noise_comparison(args, base_phi_sui, base_phi_rev):
    assert(args.noisy_side in {"suitors", "reviewers"})
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
        noisy_suitors = noise_utils.add_noise_slide(suitors, 0, 3, 1)
        noisy_reviewers = copy.deepcopy(reviewers)
    else:
        noisy_suitors = copy.deepcopy(suitors)
        noisy_reviewers = noise_utils.add_noise_slide(reviewers, 0, 3, 1)


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

def noise_run(std_or_max):
    assert(std_or_max in {"std", "max"})
    args = Args()
    args.n = 15
    args.noisy_side = "reviewers"
    #for one given profile of men & women, we want to repeat the experiment of adding noise
    #we also want to run this for many different profiles
    #for now: just one run per initial profile
    args.num_runs = 500
    phis = [i / 4 for i in range(5)]
    path = "results/noise/maxes/reviewers"

    file_name = get_path_name(args)
    file_path = os.path.join(path, file_name)

    #run
    for phi_sui in phis:
        phi_to_diffs_sui = dict()
        phi_to_diffs_rev = dict()
        for phi_rev in phis:
            mean_borda_diff_sui = []
            mean_borda_diff_rev = []
            for _ in range(args.num_runs):
                init_sui, init_rev, noisy_sui, noisy_rev = noise_comparison(args, phi_sui, phi_rev)
                mean_borda_diff_sui.append(mean(noisy_sui) - mean(init_sui))
                mean_borda_diff_rev.append(mean(noisy_rev) - mean(init_rev))

            #plot results
            """ print("sui: " + str(phi_sui))
            print("rev: " + str(phi_rev))
            print(mean(mean_borda_diff_sui))
            print(mean(mean_borda_diff_rev)) """

            if std_or_max == "std":
                phi_to_diffs_sui[phi_rev] = (mean(mean_borda_diff_sui), stdev(mean_borda_diff_sui))
                phi_to_diffs_rev[phi_rev] = (mean(mean_borda_diff_rev), stdev(mean_borda_diff_rev))
            else:
                phi_to_diffs_sui[phi_rev] = (mean(mean_borda_diff_sui), max(mean_borda_diff_sui), min(mean_borda_diff_sui))
                phi_to_diffs_rev[phi_rev] = (mean(mean_borda_diff_rev), max(mean_borda_diff_rev), min(mean_borda_diff_rev))

        if std_or_max == "std":
            graph_mean_stdev_multiple([phi_to_diffs_sui, phi_to_diffs_rev], file_name + "_phi_sui_" + str(phi_sui), file_path + "_phi_sui_" + str(phi_sui), "phi rev", "Mean of Borda score diff", ["suitors", 'reviewers'])
        else:
            graph_min_max_multiple([phi_to_diffs_sui, phi_to_diffs_rev], file_name + "_phi_sui_" + str(phi_sui), file_path + "_phi_sui_" + str(phi_sui), "phi rev", "Mean of Borda score diff", ["suitors", 'reviewers'])

noise_run("max")