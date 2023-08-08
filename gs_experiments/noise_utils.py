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

def add_noise_slide(players, overlap=0, window_length=3, permute_prob=1.):
    """
    creates a new list of players with noise added to the preferences of the input list
    noise is added by sliding a window on each player's preference list and performing a permutation
    """
    pref_length = len(players[0].prefs)
    assert(overlap >= 0 and overlap < window_length)
    assert(window_length <= pref_length)
    noisy_players = copy.deepcopy(players)
    for p in noisy_players:
        #define the window:
        for start in range(0, pref_length - window_length + 1, window_length - overlap):
            #determine if we swap or not
            if random.uniform(0, 1) < permute_prob:
                #permute the given window
                utility.permute_window_player(p, start, start + window_length)
    return noisy_players

def get_original_borda(noisy_players, original_players):
    #compute utility of the matchings of a matching in modified profile using the rankings of an original profile
    true_borda = []
    n = len(noisy_players)
    for i, p in enumerate(noisy_players):
        init_p = original_players[i]
        rank_of_noisy_match = init_p.get_rank_of(p.matching.id)
        true_borda.append(n - rank_of_noisy_match - 1)
    return true_borda