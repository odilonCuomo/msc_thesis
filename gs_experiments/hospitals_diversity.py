import os, sys, random
cwd = os.getcwd()
sys.path.append(cwd)
from utils.args import Args, get_path_name
import gs_utils
from matching.games import HospitalResident
from statistics import mean, stdev
import numpy as np
import diversity.hospital_matching as hm
from utils.graph_vals import graph_mean_stdev_multiple


"""
setting
- no unacceptable matches
- complete preferences are given
- possible unmatched agents at the end (although we start with 400/20-20)
"""
np.random.seed(0)
args = Args()
args.num_runs = 50
args.num_res = 400
args.num_hos = 20
args.quota = 20
args.noisy_side = "hospitals"
#args.static_phi = 1.
args.metric = "rank"
ticks = 6
dispersion_range = [i / (ticks - 1) for i in range(ticks)]
path = os.path.join("results/hospitals/rank/", args.noisy_side)
static_side = "hospitals" if args.noisy_side == "residents" else "residents"

assert(args.noisy_side.lower() in {"hospitals", "residents"})

r_borda_stats = dict()
h_borda_stats = dict()
r_unmatched_stats = dict()
h_unmatched_stats = dict()

for static_phi in dispersion_range:
    for changing_phi in dispersion_range:
        
        r_bordas, h_bordas = [], []
        r_unmatched, h_unmatched = [], []

        for _ in range(args.num_runs):
            #create players
            ref_res = tuple(sorted([i for i in range(args.num_hos)], key=lambda k: random.random()))
            ref_hos = tuple(sorted([i for i in range(args.num_res)], key=lambda k: random.random()))
            phi_res = changing_phi
            phi_hos = static_phi
            if args.noisy_side.lower() == "hospitals":
                phi_res, phi_hos = phi_hos, phi_res
            res_prefs = {i: ranking for i, ranking in enumerate(gs_utils.create_asymmetric_mallows_profile(args.num_res, args.num_hos, phi_res, ref_res))}
            hos_prefs = {i: ranking for i, ranking in enumerate(gs_utils.create_asymmetric_mallows_profile(args.num_hos, args.num_res, phi_hos, ref_hos))}
            r_metric, h_metric, r_un, h_un = hm.run_hospital_gs(res_prefs, hos_prefs, args.quota, args.metric)
            r_unmatched.append(r_un)
            h_unmatched.append(h_un)
            r_bordas.extend(r_metric.values())
            h_bordas.extend(h_metric.values())
        
        #record stats
        r_borda_stats[changing_phi] = (mean(r_bordas), stdev(r_bordas))
        h_borda_stats[changing_phi] = (mean(h_bordas), stdev(h_bordas))
        r_unmatched_stats[changing_phi] = (mean(r_unmatched), stdev(r_unmatched))
        h_unmatched_stats[changing_phi] = (mean(h_unmatched), stdev(h_unmatched))

    if not os.path.isdir(path):
        os.mkdir(path)
    file_name = get_path_name(args)
    file_path = os.path.join(path, file_name)

    suffix = "_phi_" + static_side + str(static_phi)

    graph_mean_stdev_multiple([r_borda_stats, h_borda_stats], file_name + suffix, file_path + suffix + "_rank", "phi_" + static_side, "Mean of rank of matched agents", ["residents", 'hospitals'])
    #graph_mean_stdev_multiple([r_unmatched_stats, h_unmatched_stats], file_name + suffix, file_path + suffix + "_unmatched", "phi_" + static_side, "Number of unmatched agents", ["residents", 'hospitals'])
    print(r_unmatched_stats)
    print(h_unmatched_stats)