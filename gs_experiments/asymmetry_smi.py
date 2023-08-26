import random, os, sys, git, json, argparse
cwd = os.getcwd()
sys.path.append(cwd)
import gs_utils
from diversity.stable_marriage import gale_shapley, players, borda_vals
from diversity.distributions import mallows
from utils.args import Args, get_path_name
from utils.graph_vals import graph_mean_stdev, graph_mean_stdev_multiple, graph_grid

from statistics import mean, stdev
from datetime import datetime

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

def mallows_DA_grid(n, nb_runs, dispersion_range, mode="mean"):
    """
    Returns a 2D grid of means on the number of proposals and borda scores for suitors and reviewers for a given number of runs of the GS algorithm.
    Both sides have Mallows-distributed preferences.
    """
    #create players & run GS nb_runs times
    stats = dict()
    borda_stats_sui = dict()
    borda_stats_rev = dict()
    se_cost_dict = dict()
    unmatched_dict = dict()

    for phi_rev in dispersion_range:
        for phi_sui in dispersion_range:
            nb_props = []
            b_sui = []
            b_rev = []
            se_costs = []
            unmatched_nbs = []
            for _ in range(nb_runs):
                #create players
                ref_sui = tuple(sorted([i for i in range(n)], key=lambda k: random.random()))
                ref_rev = tuple(sorted([i for i in range(n)], key=lambda k: random.random()))
                suitors = gs_utils.create_mallows_players(n, phi_sui, ref_sui)
                reviewers = gs_utils.create_mallows_players(n, phi_rev, ref_rev)
                truncate_prefs(suitors, args.prefs_bound_sui)
                truncate_prefs(reviewers, args.prefs_bound_rev)
                rev_dict = {}
                for i, p in enumerate(reviewers):
                    rev_dict[p.id] = i

                props, b_suitors, b_reviewers = gs_utils.run_gs_premium(suitors, reviewers, rev_dict, args.matched_premium)
                mean_borda_suitors, mean_borda_reviewers = mean(b_suitors), mean(b_reviewers)
                nb_props.append(sum(props))
                b_sui.append(mean_borda_suitors)
                b_rev.append(mean_borda_reviewers)
                se_costs.append(mean_borda_suitors - mean_borda_reviewers)
                unmatched_nbs.append(count_unmatched(suitors * 2))
            stats[(phi_sui, phi_rev)] = mean(nb_props) if mode == "mean" else stdev(nb_props)
            borda_stats_sui[(phi_sui, phi_rev)] = mean(b_sui) if mode == "mean" else stdev(b_sui)
            borda_stats_rev[(phi_sui, phi_rev)] = mean(b_rev) if mode == "mean" else stdev(b_rev)
            se_cost_dict[(phi_sui, phi_rev)] = mean(se_costs) if mode == "mean" else stdev(se_costs)
            unmatched_dict[(phi_sui, phi_rev)] = mean(unmatched_nbs) if mode == "mean" else stdev(unmatched_nbs)

    return stats, borda_stats_sui, borda_stats_rev, se_cost_dict, unmatched_dict

def run_asym(args):
    tick_range = range(args.ticks + 1)
    dispersion_range = [i / args.ticks for i in tick_range]
    path = "results/asymmetry/incomplete/"
    
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

    prop_stats, borda_stats_sui, borda_stats_rev, se_cost_dict, unmatched_dict = mallows_DA_grid(args.n, args.num_runs, dispersion_range)

    if not os.path.isdir(path):
        os.mkdir(path)
    file_name = get_path_name(args)
    file_path = os.path.join(path, file_name)

    prop_min_max = (args.n, pow(args.n, 2) - (args.n - 1))
    graph_grid(prop_stats, "", os.path.join(path, "proposition_matrix"), prop_min_max, "phi_men", "phi_women")
    graph_grid(borda_stats_sui, "", os.path.join(path, "men_borda_matrix"), None, "phi_men", "phi_women")
    graph_grid(borda_stats_rev, "", os.path.join(path, "women_borda_matrix"), None, "phi_men", "phi_women")
    #4th grid: sex equality cost
    graph_grid(se_cost_dict, "", os.path.join(path, "se_costs"), None, "phi_men", "phi_women")
    graph_grid(unmatched_dict, "", os.path.join(path, "unmatched"), None, "phi_men", "phi_women")
    

def build_parser():

    parser = argparse.ArgumentParser()

    parser.add_argument('--n', type=int, default=15, required=True)
    parser.add_argument('--num_runs', type=int, default=1000, required=True)
    parser.add_argument('--ticks', type=int, default=10)

    parser.add_argument('--prefs_bound_sui', type=int, default=10, required=True)
    parser.add_argument('--prefs_bound_rev', type=int, default=10, required=True)
    parser.add_argument('--matched_premium', type=int, default=0, required=True)
    
    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    run_asym(args)