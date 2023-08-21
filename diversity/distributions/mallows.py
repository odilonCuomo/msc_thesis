import numpy as np
# utils to sample from mallows


def Mallows_Proposal_Sampler(phi, reference):
    nb_alternatives = len(reference)
    ordering = []
    alternatives_left = list(int(a) for a in reference)
    basic_distro = [pow(phi, i) for i in range(nb_alternatives)]

    for i in range(nb_alternatives):
        #draw from a n-i sized geometric distribution
        p = np.asarray(basic_distro[: nb_alternatives - i]).astype('float64')
        p = p / np.sum(p)
        choice = np.random.choice(a=alternatives_left, p=p)
        #delete drawn alt from alt_left, add to final ordering
        alternatives_left.remove(choice)
        ordering.append(choice)

    return tuple(ordering)

def Mallows_Profile(nb_alternatives, nb_agents, phi, reference):
    """ Returns a population's preferences distributed according to the Mallows model
        :param nb_alternatives: number of alternatives to totally order 
        :type nb_alternatives: int
        :param nb_agents: number of agents in the profile
        :type nb_agents: int
        :param phi: dispersion factor, in [0, 1]
        :type phi: double
        :param reference: reference ordering for the Mallows distribution
        :type reference: tuple of tuple of ints or tuple of ints
        :return: a population's preferences distributed according to the Mallows model
        :rtype: dict, keys are orders, values are number of voters with those orders as preferences
    """
    profile = dict()
    for agent in range(nb_agents):
        #create ordering
        ordering = Mallows_Proposal_Sampler(phi, reference)
        #add to ordering dictionary
        profile[ordering] = profile.get(ordering, 0) + 1

    return profile