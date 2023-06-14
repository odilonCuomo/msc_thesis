import os
import sys
cwd = os.getcwd()
sys.path.append(cwd)
from utils.args import Args
import gs_utils
from utils.graph_vals import graph_mean_stdev
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

def permute_top_k(profile, k):
    """Given a preference profile and a length k, randomly permute the first k elements of each ordering.
        
        Parameters
        ----------
        profile : list of Player
        k : int

        Returns
        -------
        profile : list of Player
            The original profile with prefixes permuted randomly.
    """
    for p in profile:
        prefs = list(p.prefs)
        prefix = prefs[:k]
        random.shuffle(prefix)
        prefs[:k] = prefix
        p.prefs = tuple(prefs)
    return profile


args = Args()
args.n = 25
args.prefix_max = args.n
args.num_runs = 1000
args.noisy_side = "suitors"
stats = dict()
ref = tuple(i for i in range(args.n))

assert(args.noisy_side.lower() in {"suitors", "reviewers"})

for prefix_len in range(2, args.prefix_max + 1):
    prop_diffs = []
    for _ in range(args.num_runs):
        #create a profile
        suitors = gs_utils.create_mallows_players(args.n, phi=1, ref=ref)
        reviewers = gs_utils.create_mallows_players(args.n, phi=1, ref=ref)
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

path = "asymmetry/top_diversity/"
path = utils.args.get_path_name(path, args)

graph_mean_stdev(stats, path, "Prefix length", "T_n before minus permuted")

