from preflibtools.properties.distances import *

class PDI:
    def of(self, profile):
        pass

class Support_PDI(PDI):
    def of(self, profile):
        """ Returns the diversity index corresponding to the given profile
            :param profile: a population's preferences
            :type profile: dict, keys are orders, values are number of voters with those orders as preferences
            :return: A support based diversity index of the profile, i.e. an integer counting the number of distinct 
                orders in the population
            :rtype: int
        """
        cardinalities = list(profile.values())
        for c in cardinalities:
            assert(c != 0)
        return len(profile) - 1
    
    def __str__(self) -> str:
        return "support_pdi"
    
def support_pdi(profile):
    """ Returns the diversity index corresponding to the given profile
        :param profile: a population's preferences
        :type profile: dict, keys are orders, values are number of voters with those orders as preferences
        :return: A support based diversity index of the profile, i.e. an integer counting the number of distinct 
            orders in the population
        :rtype: int
    """
    cardinalities = list(profile.values())
    for c in cardinalities:
        assert(c != 0)
    return len(profile) - 1

class Top_K_Support_PDI(PDI):
    def __init__(self, k) -> None:
        super().__init__()
        self.k = k

    def of(self, profile):
        """ Returns the top-k diversity index corresponding to the given profile
            :param profile: a population's preferences
            :type profile: dict, keys are orders, values are number of voters with those orders as preferences
            :return: A support based diversity index of the profile, i.e. an integer counting the number of distinct 
                top-k orders in the population
            :rtype: int
        """
        orders = list(profile.keys())
        top_k_orders = set()
        for o in orders:
            top_k_orders.add(o[0: self.k])
        return len(top_k_orders) - 1
    
    def __str__(self) -> str:
        return "top_k_support_pdi"
    
def sum_aggregator(pair_list):
    sum = 0
    for (v, count) in pair_list:
        sum += count * v
    return sum

class Distance_PDI(PDI):
    def __init__(self, aggregate, dist_fct) -> None:
        """ 
            :param aggregator: aggregating function
            :type aggregator: function
            :param dist_fct: a distance function between two orders
            :type dist_fct: function
        """
        super().__init__()
        self.aggregate = aggregate
        self.dist_fct = dist_fct

    def of(self, profile):
        """ Returns the diversity index corresponding to the given profile
            :param profile: a population's preferences
            :type profile: dict, keys are orders, values are number of voters with those orders as preferences
            :return: A distance based diversity index of the profile. Obtained by measuring the distance between
                all pairs of voters, and aggregating those values
            :rtype: int
        """
        #list of tuples of distances and how many times they should be added to the final tally
        #e.g. [(2.3, 4), (0.33, 9)]
        distances = []
        profile_pairs = list(profile.items())
        length = len(profile_pairs)
        for i, (order1, card1) in enumerate(profile_pairs):
            for j in range(i, length):
                if (i != j):
                    order2, card2 = profile_pairs[j]
                    d = self.dist_fct(order1, order2)
                    distances.append((d, card1 * card2)) 
        return self.aggregate(distances)
    
    def __str__(self) -> str:
        return "distance_pdi"

class Top_K_Distance_PDI(PDI):
    def __init__(self, k, aggregate, dist_fct) -> None:
        super().__init__()
        self.k = k
        self.aggregate = aggregate
        self.dist_fct = dist_fct

    def of(self, profile):
        """ Returns the top-k diversity index corresponding to the given profile
            :param profile: a population's preferences
            :type profile: dict, keys are orders, values are number of voters with those orders as preferences
            :return: A distance based diversity index of the profile, i.e. an integer aggregated from the 
                pairwise distance between every top-k ordering in the profile
            :rtype: int
        """
        distances = []
        profile_pairs = list(profile.items())
        length = len(profile_pairs)
        for i, (order1, card1) in enumerate(profile_pairs):
            order1 = order1[: self.k]    #convert to top-k
            for j in range(i, length):
                if (i != j):
                    order2, card2 = profile_pairs[j]
                    order2 = order2[: self.k]
                    d = self.dist_fct(order1, order2)
                    distances.append((d, card1 * card2)) 
        return self.aggregate(distances)
    
    def __str__(self) -> str:
        return "top_k_distance_pdi"

def distance_pdi(profile, aggregate, dist_fct):
    """ Returns the diversity index corresponding to the given profile
        :param profile: a population's preferences
        :type profile: dict, keys are orders, values are number of voters with those orders as preferences
        :param aggregator: aggregating function
        :param dist: a distance function between two orders
        :return: A distance based diversity index of the profile. Obtained by measuring the distance between
            all pairs of voters, and aggregating those values
        :rtype: int
    """
    #list of tuples of distances and how many times they should be added to the final tally
    #e.g. [(2.3, 4), (0.33, 9)]
    distances = []
    profile_pairs = list(profile.items())
    length = len(profile_pairs)
    for i, (order1, card1) in enumerate(profile_pairs):
        for j in range(i, length):
            if (i != j):
                order2, card2 = profile_pairs[j]
                d = dist_fct(order1, order2)
                distances.append((d, card1 * card2)) 
    return aggregate(distances)


class Compromise_PDI(PDI):
    def __init__(self, reference, aggregate, dist_fct) -> None:
        super().__init__()
        self.reference = reference
        self.aggregate = aggregate
        self.dist_fct = dist_fct

    def of(self, profile):
        #we cheat on the compromise value: we take the reference order (to take the majority requires the FAIA definition of K distance,
        # not equivalent to Kendall distance in general)
        
        #compute all distances to this compromise
        distances = []
        profile_pairs = list(profile.items())
        for order1, card1 in profile_pairs:
            d = self.dist_fct(order1, self.reference)
            distances.append((d, card1))
        return self.aggregate(distances)
    
    def __str__(self) -> str:
        return "compromise_pdi"


def compromise_pdi(profile, reference, aggregate, dist_fct):
    #we cheat on the compromise value: we take the reference order (to take the majority requires the FAIA definition of K distance,
    # not equivalent to Kendall distance in general)
    
    #compute all distances to this compromise
    distances = []
    profile_pairs = list(profile.items())
    for order1, card1 in profile_pairs:
        d = dist_fct(order1, reference)
        distances.append((d, card1)) 
    return aggregate(distances)