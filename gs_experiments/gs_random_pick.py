import random
import statistics
import os
import sys
cwd = os.getcwd()
sys.path.append(cwd)
from diversity.stable_marriage import gale_shapley, players, borda_vals
from diversity.distributions import mallows
from utils.graph_vals import graph_mean_stdev
from utils.args import Args
import utils.args
import gs_utils

def rand_pick(n, nb_runs, nb_epochs):
    """
    On a given profile of players, run the GS algorithm for nb_runs times, each time with a different permutation
    in the order of men. Do this on nb_epochs different profiles.
    Compare men's happiness within each epoch.
    """
    nb_props = []
    for _ in range(nb_epochs):
        #create players
        ref_sui = tuple(sorted([i for i in range(n)], key=lambda k: random.random()))
        ref_rev = tuple(sorted([i for i in range(n)], key=lambda k: random.random()))
        suitors = gs_utils.create_mallows_players(n, phi=1, ref=ref_sui)
        reviewers = gs_utils.create_mallows_players(n, phi=1, ref=ref_rev)
        rev_dict = {}
        for i, p in enumerate(reviewers):
            rev_dict[p.id] = i
        
        runs = []
        for _ in range(nb_runs):
            #run GS 
            props, _, _ = gs_utils.run_gs(suitors, reviewers, rev_dict)
            runs.append(sum(props))
            gs_utils.reset_players(suitors)
            gs_utils.reset_players(reviewers)

            #shuffle the suitors
            random.shuffle(suitors)
        
        nb_props.append(max(runs) - min(runs))

    return nb_props

print(max(rand_pick(15, 10000, 1000)))