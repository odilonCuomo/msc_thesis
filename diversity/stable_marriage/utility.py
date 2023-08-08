import statistics, random

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

def permute_window_player(player, i, j):
    """Given a player and two indices i and j, randomly permute the elements between i and j (included) of the players ranking.
        
        Parameters
        ----------
        player : a matching problem Player object
        i : int
        j : int

        Returns
        -------
        -nothing-
    """
    prefs = list(player.prefs)
    window = prefs[i:j + 1]
    random.shuffle(window)
    prefs[i:j + 1] = window
    player.prefs = tuple(prefs)

def permute_window(profile, i, j):
    """Given a preference profile and two indices i and j, randomly permute the elements between i and j (included) of all players in the profile.
        
        Parameters
        ----------
        profile : list of Player
        i : int
        j : int

        Returns
        -------
        profile : list of Player
            The original profile with the window permuted randomly.
    """
    for p in profile:
        permute_window_player(p, i, j)
    return profile

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
    return permute_window(profile, 0, k)