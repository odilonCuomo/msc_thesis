import numpy as np
# utils to sample from mallows


def Mallows_Proposal_Sampler(nb_alternatives, phi, reference):
    ordering = []
    alternatives_left = list(int(a) for a in reference)
    #indices of elements already seen
    indices = set()
    basic_distro = [pow(phi, i) for i in range(nb_alternatives)]

    for i in range(nb_alternatives):
        #draw from a n-i sized geometric distribution
        choice = np.random.choice(a=alternatives_left, p=basic_distro[: nb_alternatives - i])
        #delete drawn alt from alt_left, add to final ordering
        alternatives_left.remove(choice)
        ordering.append(choice)

    return ordering

#mallows proposal sampler - returns a profile
def Mallows_Proposal_Profile(nb_alternatives, nb_agents, phi, reference):
    profile = 
    for agent in range(nb_agents):
        #create ordering
        ordering = Mallows_Proposal_Sampler(nb_alternatives, phi, reference)
        #add to ordering dictionary

    return profile