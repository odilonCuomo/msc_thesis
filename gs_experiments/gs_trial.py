#create mallows profile
#convert to GS players, dict and player creation
import os
import sys
cwd = os.getcwd()
sys.path.append(cwd)
from diversity.stable_marriage import gale_shapley, players
from diversity.distributions import mallows

n = 2
suitors = []
reviewers = []
phi_suitors = 1
phi_reviewers = 1
ref_suitors = tuple(i for i in range(n))
ref_rev = tuple(i for i in range(n))
rev_dict = dict()

for i in range(n):
    s = players.Player(i)
    s.set_prefs(mallows.Mallows_Proposal_Sampler(n, phi_suitors, ref_suitors))
    suitors.append(s)

    r = players.Player(i)
    r.set_prefs(mallows.Mallows_Proposal_Sampler(n, phi_reviewers, ref_rev))
    reviewers.append(r)
    rev_dict[i] = i

gs_res, nb_prop = gale_shapley(suitors, reviewers, rev_dict)
print(nb_prop)
print(sum(nb_prop))