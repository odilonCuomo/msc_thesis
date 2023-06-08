import preflibtools
from distributions.mallows import *
from preflibtools.instances.sampling import *
from preflibtools.properties.distances import *
from diversity.pdi import *
import numpy as np
import matplotlib.pyplot as plt

def str_order(order):
    order = [str(alt[0]) for alt in order]
    res = ""
    for alt in order:
        res += alt
    return res

def print_profile(p):
    orders = [str_order(k) for k in list(p.keys())]
    voters = list(p.values())

    fig = plt.figure(figsize = (15, 5))

    # creating the bar plot
    plt.bar(orders, voters, color ='maroon',
            width = 0.4)

    plt.xlabel("Orders")
    plt.ylabel("No. of voters")
    plt.title("Preference orders by number of voters")
    plt.show()


num_alternatives = 3
num_voters = 50
phi = 0.3

o = Mallows_Proposal_Sampler(num_alternatives, phi, reference=(1, 2, 3))
print(o)
p = Mallows_Profile(num_alternatives, 50, 0.0, (1, 2, 3))
print(p)

t = tuple(i for i in range(7))
print(t)

""" reference_order = tuple((i) for i in range(num_alternatives)) #order expressed as tuple of ints
profile1 = generate_mallows(num_voters, num_alternatives, [1], dispersions=[phi], references=[reference_order])
profile2 = Mallows_Profile(num_alternatives, num_voters, phi, reference_order)
print_profile(profile1)
print_profile(profile2) """


""" def agg1(pair_list):
    sum = 0
    for (v, count) in pair_list:
        sum += count * v
    return sum """

""" class Args:
  def __init__(self):
      self.num_voters = 10000
      self.alternatives = 5
      self.num_runs = 250
      self.dispersion_range = 4
      self.index = support_pdi

a = Args()
print(dir(a))
print(a.__dict__)
for k, v in list(a.__dict__.items()):
   print(k)
   print(v)
   if callable(v):
      print(v.__name__) """