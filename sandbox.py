import preflibtools
from preflibtools.instances.sampling import *
from preflibtools.properties.distances import *
from pdi import *
import numpy as np
import matplotlib.pyplot as plt

def str_order(order):
    order = [str(alt[0]) for alt in order]
    res = ""
    for alt in order:
        res += alt
    return res

num_alternatives = 5
num_voters = 20

reference_order = tuple((i) for i in range(num_alternatives)) #order expressed as tuple of ints
profile = generate_mallows(num_voters, num_alternatives, [1], dispersions=[0.6], references=[reference_order])
orders = [str_order(k) for k in list(profile.keys())]
voters = list(profile.values())

fig = plt.figure(figsize = (15, 5))

# creating the bar plot
plt.bar(orders, voters, color ='maroon',
		width = 0.4)

plt.xlabel("Orders")
plt.ylabel("No. of voters")
plt.title("Preference orders by number of voters")
plt.show()


""" def agg1(pair_list):
    sum = 0
    for (v, count) in pair_list:
        sum += count * v
    return sum """
""" num_alternatives = 5
reference_order = tuple((i) for i in range(num_alternatives)) #order expressed as tuple of ints
profile = generate_mallows(20, num_alternatives, [1], dispersions=[10.], references=[reference_order])
print(profile)

def str_order(order):
    order = [str(alt[0]) for alt in order]
    res = ""
    for alt in order:
        res += alt
    return res

# creating the dataset
orders = [str_order(k) for k in list(profile.keys())]
voters = list(profile.values())

fig = plt.figure(figsize = (15, 5))

# creating the bar plot
plt.bar(orders, voters, color ='maroon',
		width = 0.4)

plt.xlabel("Orders")
plt.ylabel("No. of voters")
plt.title("Preference orders by number of voters")
plt.show()

 """
""" print(len(d))
print("support pdi:")
print(support_pdi(d))
print("distance pdi:")
dist_pdi = distance_pdi(d, agg1, kendall_tau_distance)

reference = tuple((i, ) for i in range(3)) #order expressed as tuple of ints
c_pdi = Compromise_PDI(reference, agg1, kendall_tau_distance)
c_pdi.of(d) """

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