from validating_pdi import *
from diversity.pdi import *
from preflibtools.instances.sampling import *

class Args:
  def __init__(self):
      self.num_voters = 50
      self.alternatives = 50
      self.num_runs = 25
      self.dispersion_range = [p * 0.05 for p in range(21)]
      self.index = Support_PDI()

def get_path_name(path, args):
   for attr_name, attr_val in list(args.__dict__.items()):
        if isinstance(attr_val, PDI):
            path += attr_val.__str__()
        elif not isinstance(attr_val, list):
            path += attr_name + str(attr_val) + "_"
   l = len(path)
   if path[l - 1] == "_":
       path = path[: l - 1]
   return path

def run(args, path):
    stats = pdi_on_mallows(args.num_voters, args.alternatives, args.index, args.dispersion_range, args.num_runs)
    full_path = get_path_name(path, args)
    graph_vals(stats, full_path)

def sum_aggregator(pair_list):
    sum = 0
    for (v, count) in pair_list:
        sum += count * v
    return sum

def all_three():
    base_folder = "validate_pdi/zero_one/"
    #SUPPORT
    args = Args()
    run(args, base_folder)

    #DISTANCE
    args.index = Distance_PDI(sum_aggregator, kendall_tau_distance)
    run(args, base_folder)

    #COMPROMISE
    reference = tuple((i, ) for i in range(args.alternatives))
    args.index = Compromise_PDI(reference, sum_aggregator, kendall_tau_distance)
    run(args, base_folder)

def top_k(choice):
    base_folder = "validate_pdi/top_k/"
    #SUPPORT
    args = Args()
    if (choice == "support"):
        args.index = Top_K_Support_PDI(k=3)
        run(args, base_folder)
    elif (choice == "distance"):
        args.index = Top_K_Distance_PDI(k=3, aggregate=sum_aggregator, dist_fct=kendall_tau_distance)
        run(args, base_folder)


top_k("distance")