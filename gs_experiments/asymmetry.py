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

def asymmetry_prop_borda(n, nb_runs, dispersion_range, noiseless_phi, noisy_side="suitors", borda=False):
    """
    Returns stats on the number of proposals and borda scores for suitors and reviewers for a given number of runs of the GS algorithm.
    One side has unanimous prefs, other has mallows
    """
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

    #count variable to display progress bar
    count = 0
    max_count = pow(len(dispersion_range), 2)

    for phi_rev in dispersion_range:
        for phi_sui in dispersion_range:
            nb_props = []
            b_sui = []
            b_rev = []
            se_costs = []
            for _ in range(nb_runs):
                #create players
                ref_sui = tuple(sorted([i for i in range(n)], key=lambda k: random.random()))
                ref_rev = tuple(sorted([i for i in range(n)], key=lambda k: random.random()))
                suitors = gs_utils.create_mallows_players(n, phi_sui, ref_sui)
                reviewers = gs_utils.create_mallows_players(n, phi_rev, ref_rev)
                rev_dict = {}
                for i, p in enumerate(reviewers):
                    rev_dict[p.id] = i

                props, b_suitors, b_reviewers = gs_utils.run_gs(suitors, reviewers, rev_dict)
                mean_borda_suitors, mean_borda_reviewers = mean(b_suitors), mean(b_reviewers)
                nb_props.append(sum(props))
                b_sui.append(mean_borda_suitors)
                b_rev.append(mean_borda_reviewers)
                se_costs.append(abs(mean_borda_suitors - mean_borda_reviewers))
            stats[(phi_sui, phi_rev)] = mean(nb_props) if mode == "mean" else stdev(nb_props)
            borda_stats_sui[(phi_sui, phi_rev)] = mean(b_sui) if mode == "mean" else stdev(b_sui)
            borda_stats_rev[(phi_sui, phi_rev)] = mean(b_rev) if mode == "mean" else stdev(b_rev)
            se_cost_dict[(phi_sui, phi_rev)] = mean(se_costs) if mode == "mean" else stdev(se_costs)

            count += 1
            print(str(count / max_count * 100) + "%" + str(datetime.now()))

    return stats, borda_stats_sui, borda_stats_rev, se_cost_dict

def run_asym(args):
    tick_range = range(args.ticks + 1)
    dispersion_range = [i / args.ticks for i in tick_range]
    path = "results/asymmetry/borda/"
    if not args.grid:
        args.noisy_side = "reviewers"
        assert(args.noisy_side.lower() in {"suitors", "reviewers"})
        path = os.path.join(path, args.noisy_side)
        args.noiseless_phi = 0.75

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

    if args.grid:
        prop_stats, borda_stats_sui, borda_stats_rev, se_cost_dict = mallows_DA_grid(args.n, args.num_runs, dispersion_range)
    else:
        stats, borda_stats_sui, borda_stats_rev = asymmetry_prop_borda(args.n, args.num_runs, dispersion_range, args.noiseless_phi, noisy_side=args.noisy_side, borda=args.borda)

    if not os.path.isdir(path):
        os.mkdir(path)
    file_name = get_path_name(args)
    file_path = os.path.join(path, file_name)

    if args.grid:
        prop_min_max = (args.n, pow(args.n, 2) - (args.n - 1))
        graph_grid(prop_stats, "Number of proposals", os.path.join(path, "proposition_matrix"), prop_min_max, "phi_men", "phi_women")
        graph_grid(borda_stats_sui, "Mean Borda for men", os.path.join(path, "men_borda_matrix"), None, "phi_men", "phi_women")
        graph_grid(borda_stats_rev, "Mean Borda for women", os.path.join(path, "women_borda_matrix"), None, "phi_men", "phi_women")
        #4th grid: sex equality cost
        graph_grid(se_cost_dict, "Sex-equality cost by spread values", os.path.join(path, "se_costs"), None, "phi_men", "phi_women")
    else:
        if not args.borda:
            graph_mean_stdev(stats, file_name, file_path, "phi", "E[T_n]")
        else:
            graph_mean_stdev_multiple([borda_stats_sui, borda_stats_rev], file_name + "_borda_scores", file_path, "phi", "Mean of Borda scores", ["suitors borda", 'reviewers borda'])


def build_parser():

    parser = argparse.ArgumentParser()

    parser.add_argument('--n', type=int, default=15, required=True)
    parser.add_argument('--num_runs', type=int, default=1000, required=True)
    parser.add_argument('--borda', type=bool, default=True, required=True)
    parser.add_argument('--grid', type=bool, default=True, required=True)
    parser.add_argument('--ticks', type=int, default=10)
    
    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    run_asym(args)