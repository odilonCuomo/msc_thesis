from diversity.stable_marriage import gale_shapley, players, borda_vals
from diversity.distributions import mallows

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

def reset_players(ps):
    for p in ps:
        p.reset()