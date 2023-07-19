import random
import os
import sys
cwd = os.getcwd()
sys.path.append(cwd)
import copy, random
from statistics import mean, stdev
from diversity.stable_marriage import gale_shapley, players, borda_vals
from diversity.distributions import mallows
from utils.graph_vals import graph_mean_stdev_multiple, graph_mean_stdev_groups
from utils.args import Args
import utils.args
import gs_utils


def swap_window(players, locality, window_len, swap_prob):
    """
    Returns a list of players with a modified preference profile.
    Every player's choice in the given window will be randomly swapped
    with a element from outisde the window , w.p. swap_prob.
    """
    assert(locality.lower() in {"top", "bottom"})
    #swap out
    for p in players:
        prefs = list(p.prefs)
        if locality.lower() == "top":
            target_space = list(range(window_len, len(players)))
            offset = 0
        else: 
            target_space = list(range(len(players) - window_len))
            offset = len(players) - window_len
        for i in range(window_len):
            if random.random() < swap_prob: #swap wp swap_prob
                #select a random candidate from outside the window
                target = random.choice(target_space)
                prefs[offset + i], prefs[target] = prefs[target], prefs[offset + i]
        p.prefs = tuple(prefs)
    return players

def symmetric_swap_props(n, num_runs, window_l, window_side, other_side_phi, swap_prob, borda=False):
    init_stats = ([], [], []) #props, men, women
    top_stats = ([], [], [])
    bottom_stats = ([], [], [])
    for _ in range(num_runs):
        #create a profile
        ref_sui = tuple(sorted([i for i in range(n)], key=lambda k: random.random()))
        ref_rev = tuple(sorted([i for i in range(n)], key=lambda k: random.random()))
        suitors = gs_utils.create_mallows_players(n, phi=0, ref=ref_sui)
        reviewers = gs_utils.create_mallows_players(n, phi=other_side_phi, ref=ref_rev)
        if window_side.lower() == "reviewers":
            suitors, reviewers = reviewers, suitors
            ref_sui, ref_rev = ref_rev, ref_sui
        rev_dict = dict()
        for i, p in enumerate(reviewers):
            rev_dict[p.id] = i

        stats_res = gs_utils.run_gs(suitors, reviewers, rev_dict)
        for i, stat in enumerate(stats_res):
            init_stats[i].append(sum(stat))
        gs_utils.reset_players(suitors)
        gs_utils.reset_players(reviewers)
        

        #Swaps: create a deep copy, & perform swaps, then reset other side
        if window_side == "suitors":
            #TOP
            top_suitors = copy.deepcopy(suitors)
            top_swap_suitors = swap_window(top_suitors, "top", window_l, swap_prob)
            top_stats_res = gs_utils.run_gs(top_swap_suitors, reviewers, rev_dict)
            gs_utils.reset_players(reviewers)
            #BOTTOM
            bottom_swap_suitors = swap_window(suitors, "bottom", window_l, swap_prob)
            bottom_stats_res = gs_utils.run_gs(bottom_swap_suitors, reviewers, rev_dict)
        else:
            #TOP
            top_reviewers = copy.deepcopy(reviewers)
            top_swap_reviewers = swap_window(top_reviewers, "top", window_l, swap_prob)
            top_stats_res = gs_utils.run_gs(suitors, top_swap_reviewers, rev_dict)
            gs_utils.reset_players(suitors)
            #BOTTOM
            bottom_swap_reviewers = swap_window(reviewers, "bottom", window_l, swap_prob)
            bottom_stats_res = gs_utils.run_gs(suitors, bottom_swap_reviewers, rev_dict)
        for i, stat in enumerate(top_stats_res):
            top_stats[i].append(sum(stat))
        for i, stat in enumerate(bottom_stats_res):
            bottom_stats[i].append(sum(stat))
    return init_stats, top_stats, bottom_stats

def symmetric_swap_stats_vary_window_len(n, num_runs, window_lengths, window_side, other_side_phi, swap_prob, borda=False):
    assert(window_side.lower() in {"suitors", "reviewers"})
    assert(max(window_lengths) < n / 2)

    prop_ix, men_ix, women_ix = tuple(range(3))

    stats_init = (dict(), dict()) if borda else dict()
    stats_top = (dict(), dict()) if borda else dict()
    stats_bottom = (dict(), dict()) if borda else dict()
    all_stages_stats = (stats_init, stats_top, stats_bottom)

    for window_l in window_lengths:
        if borda:
            init_borda, top_borda, bottom_borda = symmetric_swap_props(n, num_runs, window_l, window_side, other_side_phi, swap_prob)
            mens_stats = (init_borda[men_ix], top_borda[men_ix], bottom_borda[men_ix])
            womens_stats = (init_borda[women_ix], top_borda[women_ix], bottom_borda[women_ix])
            #men
            for i, stat in enumerate(mens_stats):
                all_stages_stats[i][0][window_l] = (mean(stat), stdev(stat))
            #women
            for i, stat in enumerate(womens_stats):
                all_stages_stats[i][1][window_l] = (mean(stat), stdev(stat))

        else:
            init_props, top_props, bottom_props = symmetric_swap_props(n, num_runs, window_l, window_side, other_side_phi, swap_prob)
            init_props, top_props, bottom_props = init_props[prop_ix], top_props[prop_ix], bottom_props[prop_ix]

            stats_init[window_l] = (mean(init_props), stdev(init_props))
            stats_top[window_l] = (mean(top_props), stdev(top_props))
            stats_bottom[window_l] = (mean(bottom_props), stdev(bottom_props))

    return stats_init, stats_top, stats_bottom

def symmetric_swap_stats_vary_swap_prob(n, num_runs, window_l, window_side, other_side_phi, swap_probs):
    assert(window_side.lower() in {"suitors", "reviewers"})

    stats_init = dict()
    stats_top = dict()
    stats_bottom = dict()

    for sp in swap_probs:
        init_props, top_props, bottom_props = symmetric_swap_props(n, num_runs, window_l, window_side, other_side_phi, sp)

        m = mean(init_props)
        stats_init[sp] = (m, stdev(init_props))
        stats_top[sp] = (mean(top_props), stdev(top_props))
        stats_bottom[sp] = (mean(bottom_props), stdev(bottom_props))

    return stats_init, stats_top, stats_bottom

if __name__ == "__main__":
    args = Args()
    args.n = 25
    args.window_side = "reviewers"
    window_lengths = list(range(2, int(args.n / 2)))
    args.num_runs = 150
    args.other_side_phi = 0.5
    borda = True
    swap_prob = 1.
    path = "results/asymmetry/top_diversity/swap/window/borda/reviewers"

    stats, top_stats, bottom_stats = symmetric_swap_stats_vary_window_len(args.n, args.num_runs, window_lengths, args.window_side, args.other_side_phi, swap_prob, borda)

    file_name = utils.args.get_path_name(args)
    file_path = os.path.join(path, file_name)

    if not borda:
        graph_mean_stdev_multiple([stats, top_stats, bottom_stats], file_name, file_path, "Window length", "T_n", ["init", "top", "bottom"])
    else:
        graph_mean_stdev_groups([stats, top_stats, bottom_stats], file_name, file_path, "Window length", "T_n", ["men", "women"], ["init", "top", "bottom"])
