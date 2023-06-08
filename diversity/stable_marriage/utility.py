import statistics

def borda_vals(players):
    """get a list of each player's Borda utility"""
    us = []
    for p in players:
        us.append(p.get_borda())
    return us

def borda_stats(players):
    """util function returning the mean and stddev Borda count utility of a list of players.
    Supposes the matching algorithm has already been run (all players are matched up)."""
    utilities = []
    for s in players:
        utilities.append[s.get_Borda()]
    return statistics.mean(utilities), statistics.stdev(utilities)