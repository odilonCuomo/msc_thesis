import os
import sys
cwd = os.getcwd()
sys.path.append(cwd)
from utils.args import Args
import gs_utils
from utils.graph_vals import *
import random, statistics, utils

"""
each iteration:
ranking prefix size: j
create a profile for both sides ~ uniformly
compute nb_props
randomly permute the top-j rankings of all suitors/reviewers
compute new nb_props
add difference to dict(j -> list of differences)
run nb_runs for each j
compute dict(j -> mean, stdev differences)
graph and save
"""

def prefix_effect():
    args = Args()
    args.n = 15
    args.num_runs = 500
    args.noisy_side = "reviewers"
    args.base_phi_sui = 0.5
    args.base_phi_rev = 0.
    stats = dict()

    assert(args.noisy_side.lower() in {"suitors", "reviewers"})

    for prefix_len in range(2, args.n + 1):
        prop_diffs = []
        for _ in range(args.num_runs):
            #create a profile
            ref_sui = tuple(sorted([i for i in range(args.n)], key=lambda k: random.random()))
            ref_rev = tuple(sorted([i for i in range(args.n)], key=lambda k: random.random()))
            suitors = gs_utils.create_mallows_players(args.n, phi=args.base_phi_sui, ref=ref_sui)
            reviewers = gs_utils.create_mallows_players(args.n, phi=args.base_phi_rev, ref=ref_rev)
            rev_dict = dict()
            for i, p in enumerate(reviewers):
                rev_dict[p.id] = i
            init_props, _, _ = gs_utils.run_gs(suitors, reviewers, rev_dict)
            gs_utils.reset_players(suitors)
            gs_utils.reset_players(reviewers)

            #permute top k for one side
            if args.noisy_side == "suitors":
                suitors = permute_top_k(suitors, prefix_len)
            else:
                reviewers = permute_top_k(reviewers, prefix_len)
            
            permuted_props, _, _ = gs_utils.run_gs(suitors, reviewers, rev_dict)

            prop_diffs.append(sum(init_props) - sum(permuted_props))
        
        stats[prefix_len] = (statistics.mean(prop_diffs), statistics.stdev(prop_diffs))

    path = "asymmetry/top_diversity/top_k/"
    path = utils.args.get_path_name(path, args)

    graph_mean_stdev(stats, path, "Prefix length", "T_n before minus permuted")

def sliding_window_effect():
    args = Args()
    args.n = 15
    args.window_len = 4
    args.num_runs = 500
    args.slide_side = "reviewers"
    args.base_phi_sui = 0.25
    args.base_phi_rev = 0.25
    stats_init = dict()
    stats_perm = dict()

    assert(args.slide_side.lower() in {"suitors", "reviewers"})

    for window_start in range(args.n - args.window_len):
        init_props = []
        permuted_props = []

        for _ in range(args.num_runs):
            #create a profile
            ref_sui = tuple(sorted([i for i in range(args.n)], key=lambda k: random.random()))
            ref_rev = tuple(sorted([i for i in range(args.n)], key=lambda k: random.random()))
            suitors = gs_utils.create_mallows_players(args.n, phi=args.base_phi_sui, ref=ref_sui)
            reviewers = gs_utils.create_mallows_players(args.n, phi=args.base_phi_rev, ref=ref_rev)
            rev_dict = dict()
            for i, p in enumerate(reviewers):
                rev_dict[p.id] = i
            init_prop, _, _ = gs_utils.run_gs(suitors, reviewers, rev_dict)
            init_props.append(sum(init_prop))
            gs_utils.reset_players(suitors)
            gs_utils.reset_players(reviewers)

            #permute top k for one side
            if args.slide_side == "suitors":
                suitors = permute_window(suitors, window_start, window_start + args.window_len)
            else:
                reviewers = permute_window(reviewers, window_start, window_start + args.window_len)
            
            permuted_prop, _, _ = gs_utils.run_gs(suitors, reviewers, rev_dict)
            permuted_props.append(sum(permuted_prop))
        
        m = statistics.mean(init_props)
        stats_init[window_start] = (m, statistics.stdev(init_props))
        print("init: " + str(m))
        stats_perm[window_start] = (statistics.mean(permuted_props), statistics.stdev(permuted_props))

    path = "asymmetry/top_diversity/window_slide/reviewer_sl/n15/rev0.25/"
    path = utils.args.get_path_name(path, args)

    graph_mean_stdev_multiple([stats_init, stats_perm], path, "Window start idx", "T_n before minus permuted", ["init", "permuted"])

prefix_effect()