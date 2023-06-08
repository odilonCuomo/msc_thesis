import random
import statistics
import os
import sys
cwd = os.getcwd()
sys.path.append(cwd)
from diversity.stable_marriage import gale_shapley, players, borda_vals
from diversity.distributions import mallows

"""
#2 for a given n:
x = phi
y = mean and stddev Borda of both sides
"""

def run_gs(suitors, reviewers, rev_id_to_idx):
    """Run the GS algorithm using the given players lists."""
    _, props = gale_shapley(suitors.copy(), reviewers.copy(), rev_id_to_idx)

    return props, borda_vals(suitors), borda_vals(reviewers)

def create_mallows_players(n, phi, ref):
    """Creates a population of n players with mallows distributed preferences."""
    mallows_players = []
    for i in range(n):
        s = players.Player(i)
        s.set_prefs(mallows.Mallows_Proposal_Sampler(n, phi, ref))
        mallows_players.append(s)
    return mallows_players

def asym_nb_prop(n, nb_runs, phi, ref, noisy_side="suitors"):
    """
    Returns stats on the number of proposals for a given number of runs of the GS algorithm.
    One side has unanimous prefs, other has mallows
    """
    assert(noisy_side.lower() in {"suitors", "reviewers"})
    #create players & run GS nb_runs times
    nb_props = []
    for _ in range(nb_runs):
        #create players
        suitors = create_mallows_players(n, phi, ref)
        reviewers = create_mallows_players(n, 0, ref=ref)
        #asymmetry depends on side
        if noisy_side.lower() == "reviewers":
            suitors, reviewers = reviewers, suitors
        rev_dict = {}
        for i, p in enumerate(reviewers):
            rev_dict[p.id] = i

        props, _, _ = run_gs(suitors, reviewers, rev_dict)
        nb_props.append(sum(props))

    return statistics.mean(nb_props), statistics.stdev(nb_props)

n = 2
print(asym_nb_prop(n, nb_runs=10000, phi=1, ref=tuple(i for i in range(n))))