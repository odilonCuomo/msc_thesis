import os, sys
cwd = os.getcwd()
sys.path.append(cwd)
from matching.games import HospitalResident
from statistics import mean
import numpy as np

"""
setting
- no unacceptable matches
- complete preferences are given
- possible unmatched agents at the end (although we start with 400/20-20)
"""

def get_mean_borda(matches, pref_list):
    utils = [len(pref_list) - list(pref_list).index(m.name) - 1 for m in matches]
    return mean(utils)

def get_mean_rank(matches, pref_list):
    utils = [list(pref_list).index(m.name) for m in matches]
    return mean(utils)

def get_resident_matches(h_matching, num_residents):
    """
    Returns a dictionary from each resident to their hospital match.
    """
    r_matching = dict.fromkeys(list(range(num_residents)), None)
    for h, matches in h_matching.items():
        for r in matches:
            current_state = r_matching[r.name]
            assert(current_state is None) #can't be matched to multiple hospitals
            r_matching[r.name] = h
    return r_matching


def get_polygamous_res(resident_prefs, hospital_prefs, matching, metric):
    """
    assigns borda utility scores to hospitals and students
    if a student/hospital is unmatched they do not get a borda score, are not counted toward the 
    borda score aggregate, and instead are accounted for by a unmatched counter variable
    Returns each side's rank information (borda or mean rank of matched partner) and counts of unmatched agents.
    """
    r_matching = get_resident_matches(matching, len(resident_prefs))

    h_unmatched = 0
    r_unmatched = 0
    r_metric = dict.fromkeys(list(resident_prefs.keys()), None)
    h_metric = dict.fromkeys(list(hospital_prefs.keys()), None)
    for h, matches in matching.items():
        if len(matches) == 0:
            h_unmatched += 1
        else:
            #get mean over each hospital's #quota matches
            mean_metric = get_mean_borda(matches, hospital_prefs[h.name]) if metric == "borda" else get_mean_rank(matches, hospital_prefs[h.name])
            h_metric[h.name] = mean_metric
    for r, match in r_matching.items():
        if match is None:
            r_unmatched += 1
        else:
            r_metric[r] = len(hospital_prefs) - list(resident_prefs[r]).index(match.name) - 1 if metric == "borda" else list(resident_prefs[r]).index(match.name)
    return r_metric, h_metric, r_unmatched, h_unmatched

def solve_hospital_gs(resident_prefs, hospital_prefs, quota):
    capacities = {h: quota for h in hospital_prefs}
    game = HospitalResident.create_from_dictionaries(
    resident_prefs, hospital_prefs, capacities)
    sol = game.solve()
    return sol

def run_hospital_gs(resident_prefs, hospital_prefs, quota, metric):
    assert(metric in {"rank", "borda"})
    sol = solve_hospital_gs(resident_prefs, hospital_prefs, quota)
    return get_polygamous_res(resident_prefs, hospital_prefs, sol, metric)

def get_mean_borda_matched(side_borda):
    """
    Given a dictionary mapping each agent to their mean utility (possibly None if unmatched), 
    compute the mean utilities over all agents of the given group (keys in dictionary)
    """
    utils = list(side_borda.values())
    utils = [u for u in utils if u is not None]
    return mean(utils)