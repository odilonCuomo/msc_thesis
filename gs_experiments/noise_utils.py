import random, copy
from diversity.stable_marriage import utility

def add_noise_profile(profile, overlap=0, window_length=3, permute_prob=1.):
    noisy_profile = copy.deepcopy(profile)
    pref_length = len(noisy_profile[0])
    for k, pref_list in noisy_profile.items():
        #define the window:
        for start in range(0, pref_length - window_length + 1, window_length - overlap):
            #determine if we swap or not
            if random.uniform(0, 1) < permute_prob:
                #permute the given window
                pref_list = list(pref_list)
                window = pref_list[start: start + window_length]
                random.shuffle(window)
                pref_list[start: start + window_length] = window
                noisy_profile[k] = pref_list
    return noisy_profile

def add_noise(players, overlap=0, window_length=3, permute_prob=1., window_start_min=0, noise_type="RANDOM"):
    if noise_type == "LOCAL":
        return add_noise_slide(players, overlap, window_length, permute_prob, window_start_min)
    elif noise_type == "RANDOM":
        return add_random_permute_noise(players, window_start_min)
    else:
        assert(False)

def add_random_permute_noise(players, window_start_min):
    pref_length = len(players[0].prefs)
    noisy_players = copy.deepcopy(players)
    for p in noisy_players:
        utility.permute_window_player(p, window_start_min, pref_length - 1)
    return noisy_players

def add_noise_slide(players, overlap=0, window_length=3, permute_prob=1., window_start_min=0):
    """
    creates a new list of players with noise added to the preferences of the input list
    noise is added by sliding a window on each player's preference list and performing a permutation
        :param players: list of players
        :type players: List[Player]
        :param overap: size of the overlap between each adjancent sliding window
        :type overlap: int
        :param window_length: says on the tin
        :type window_length: int
        :param permute_prob: probability for each window's content to be permuted.
        :type permute_prob: float
        :param window_start_min: where to start the window sliding. If 0 starts at the top of the preference list.
        :type window_start_min: int
        :return: a list of players with the described noise added to their preference lists
        :rtype: List[Player]
    """
    pref_length = len(players[0].prefs)
    assert(overlap >= 0 and overlap < window_length)
    assert(window_length <= pref_length)
    noisy_players = copy.deepcopy(players)
    for p in noisy_players:
        #define the window:
        for start in range(window_start_min, pref_length - 1, window_length - overlap):
            #determine if we swap or not
            if random.uniform(0, 1) < permute_prob:
                #permute the given window
                utility.permute_window_player(p, start, start + window_length - 1)
    return noisy_players

def get_original_borda(noisy_players, original_players):
    #compute utility of the matchings of a matching in modified profile using the rankings of an original profile
    true_borda = []
    n = len(noisy_players)
    for i, p in enumerate(noisy_players):
        if p.matching is None:
            true_borda.append(0) #assumes original player preference list defined same set of unacceptable agents
        else:
            init_p = original_players[i]
            rank_of_noisy_match = init_p.get_rank_of(p.matching.id)
            true_borda.append(n - rank_of_noisy_match - 1)
    return true_borda