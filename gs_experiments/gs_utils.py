from diversity.stable_marriage import gale_shapley, players, borda_vals
from diversity.distributions import mallows

def run_gs(suitors, reviewers, rev_id_to_idx):
    """Run the GS algorithm using the given players lists."""
    _, props = gale_shapley(suitors.copy(), reviewers.copy(), rev_id_to_idx)

    return props, borda_vals(suitors), borda_vals(reviewers)

def run_gs_premium(suitors, reviewers, rev_id_to_idx, premium):
    """Run the GS algorithm using the given players lists."""
    _, props = gale_shapley(suitors.copy(), reviewers.copy(), rev_id_to_idx)

    return props, borda_vals(suitors, premium), borda_vals(reviewers, premium)

def create_mallows_profile(n, phi, ref):
    """Creates a Mallows preference profile"""
    profile = []
    for i in range(n):
        prefs = mallows.Mallows_Proposal_Sampler(phi, ref)
        profile.append(prefs)
    return profile

def create_asymmetric_mallows_profile(n1, n2, phi, ref):
    """
    Creates a Mallows preference profile
    n1: number of agents on the side for which we're creating the profile
    n2: number of agents on the other side
    """
    profile = []
    for i in range(n1):
        prefs = mallows.Mallows_Proposal_Sampler(phi, ref)
        profile.append(prefs)
    return profile

def create_players_from_profile(profile):
    mallows_players = []
    for i in range(len(profile)):
        s = players.Player(i)
        s.set_prefs(profile[i])
        mallows_players.append(s)
    return mallows_players

def create_mallows_players(n, phi, ref):
    """Creates a population of n players with mallows distributed preferences."""
    profile = create_mallows_profile(n, phi, ref)
    return create_players_from_profile(profile)

def reset_players(ps):
    for p in ps:
        p.reset()

def print_prefs(profile):
    for p in profile:
        print(p.prefs)