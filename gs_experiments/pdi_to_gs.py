import random
from statistics import mean, stdev
import os
import sys
cwd = os.getcwd()
sys.path.append(cwd)
from utils.graph_vals import graph_pairs_and_save
from utils.args import Args
import utils.args
import gs_utils
from collections import Counter
from diversity.pdi import *

def pdi_to_borda(n, nb_runs, PDI_function, phi_vals):
    """
    Run GS using Mallows distributed profiles, nb_runs times for each dispersion value in the range.
    Return two lists of pairs of PDI values, using the PDI metric provided, 
    each matching its side's PDI value to the mean borda in the corresponding GS run.
    """
    suitor_stats = [] #list of tuples (PDI_measure_side, nb_props)
    reviewer_stats = []

    for _ in range(nb_runs):
        #create profiles
        ref_sui = tuple(sorted([i for i in range(n)], key=lambda k: random.random()))
        ref_rev = tuple(sorted([i for i in range(n)], key=lambda k: random.random()))
        profile_sui = gs_utils.create_mallows_profile(n, phi_vals[0], ref_sui)
        profile_rev = gs_utils.create_mallows_profile(n, phi_vals[1], ref_rev)
        #compute PDIs
        if str(PDI_function) == "compromise_pdi":
            PDI_function.reference = ref_sui
        pdi_sui = PDI_function.of(Counter(profile_sui))
        if str(PDI_function) == "compromise_pdi":
            PDI_function.reference = ref_rev
        pdi_rev = PDI_function.of(Counter(profile_rev))
        #create players
        suitors = gs_utils.create_players_from_profile(profile_sui)
        reviewers = gs_utils.create_players_from_profile(profile_rev)
        rev_dict = {}
        for i, p in enumerate(reviewers):
            rev_dict[p.id] = i

        _, b_suitors, b_reviewers = gs_utils.run_gs(suitors, reviewers, rev_dict)
        suitor_stats.append((pdi_sui, sum(b_suitors)))
        reviewer_stats.append((pdi_rev, sum(b_reviewers)))
    return suitor_stats, reviewer_stats

if __name__ == "__main__":
    args = Args()
    args.n = 15
    args.num_runs = int(1e4)
    args.phi_vals = [0.7, 0.7]
    args.pdi = Compromise_PDI(None, sum_aggregator, kendall_tau_distance)
    path = "results/pdi_to_gs/pdi_to_borda/compromise"

    stats_sui, stats_rev = pdi_to_borda(args.n, args.num_runs, args.pdi, args.phi_vals)

    if not os.path.isdir(path):
        os.mkdir(path)
    file_name = utils.args.get_path_name(args)
    file_path = os.path.join(path, file_name)
    
    for stats, side in [(stats_sui, "suitors"), (stats_rev, "reviewers")]:
        graph_pairs_and_save(stats, file_name + '_' + side, file_path + '_' + side, str(args.pdi), "borda sum")
