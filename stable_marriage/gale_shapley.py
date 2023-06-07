""" Implements the GS algorithm. """


def _unmatch_pair(suitor, reviewer):
    """Unmatch a (suitor, reviewer) pair."""

    suitor._unmatch()
    reviewer._unmatch()

def _match_pair(player, other):
    """Match the players given by `player` and `other`."""

    player._match(other)
    other._match(player)


def stable_marriage(suitors, reviewers, rev_id_to_idx):
    """An extended version of the original Gale-Shapley algorithm which makes
    use of the inherent structures of SM instances. A unique, stable and optimal
    matching is found for any valid set of suitors and reviewers. The optimality
    of the matching is with respect to one party and is subsequently the worst
    stable matching for the other.

    Parameters
    ----------
    suitors : list of Player
        The suitors in the game. Each must rank all of those in ``reviewers``.
    reviewers : list of Player
        The reviewers in the game. Each must rank all of those in ``suitors``.
    reviewer_id_to_idx : dictionary object where keys are player ids and values are 
        indices in reviewers list

    Returns
    -------
    matching : Matching
        A dictionary-like object where the keys are given by the members of
        ``suitors``, and the values are their match in ``reviewers``.
    """

    free_suitors = suitors[:]
    while free_suitors:

        suitor = free_suitors[-1]
        rev_id = suitor.get_next_favourite()
        reviewer = reviewers[rev_id_to_idx[rev_id]]

        if reviewer.matching:
            current_match = reviewer.matching
            ditched = reviewer.prefers(suitor.id, current_match.id)
            if ditched:
                _unmatch_pair(current_match, reviewer)
                free_suitors.pop() #remove the current suitor from the list of free ones
                free_suitors.append(current_match)
                _match_pair(suitor, reviewer)
            #else: keep existing match, don't drop suitor to free suitor list
        else:
            #just match them up
            _match_pair(suitor, reviewer) 
            free_suitors.pop()

    return {s: s.matching for s in suitors}