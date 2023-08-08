import copy, os, sys, random
cwd = os.getcwd()
sys.path.append(cwd)
import gs_utils
import diversity.hospital_matching as hm
from noise_utils import add_noise_profile
from utils.args import Args, get_path_name
from statistics import mean, stdev
from utils.graph_vals import graph_mean_stdev_multiple, graph_min_max_multiple
"""
Goal:

investigate whether adding noise to Hospitals' preference profiles might help aggregated utility scores.

Same setup as the symmetric case.
"""

def noise_comparison(args, base_phi_res, base_phi_hos, select_prop):
    assert(args.noisy_side in {"hospitals", "residents"})
    #create profiles
    ref_res = tuple(sorted([i for i in range(args.num_hos)], key=lambda k: random.random()))
    ref_hos = tuple(sorted([i for i in range(args.num_res)], key=lambda k: random.random()))
    res_prefs = {i: ranking for i, ranking in enumerate(gs_utils.create_asymmetric_mallows_profile(args.num_res, args.num_hos, base_phi_res, ref_res))}
    hos_prefs = {i: ranking for i, ranking in enumerate(gs_utils.create_asymmetric_mallows_profile(args.num_hos, args.num_res, base_phi_hos, ref_hos))}

    #add noise
    if args.noisy_side == "residents":
        noisy_res_prefs = add_noise_profile(res_prefs, args.overlap, args.window_length, args.swap_prob)
        noisy_hos_prefs = copy.deepcopy(hos_prefs)
    else:
        noisy_res_prefs = copy.deepcopy(res_prefs)
        noisy_hos_prefs = add_noise_profile(hos_prefs, args.overlap, args.window_length, args.swap_prob)

    #leave a proportion (1 - select_prop) of the population with unmodified preferences
    if args.noisy_side == "residents":
        cutoff = int((1 - select_prop) * args.num_res)
        indices = random.sample(list(res_prefs.keys()), cutoff)
        for ix in indices:
            noisy_res_prefs[ix] = res_prefs[ix]
    else:
        cutoff = int((1 - select_prop) * args.num_hos)
        indices = random.sample(list(hos_prefs.keys()), cutoff)
        for ix in indices:
            noisy_hos_prefs[ix] = hos_prefs[ix]


    #run GS on initial profiles
    r_borda, h_borda, _, _ = hm.run_hospital_gs(res_prefs, hos_prefs, args.quota, args.metric)
    init_r_mean = hm.get_mean_borda_matched(r_borda)
    init_h_mean = hm.get_mean_borda_matched(h_borda)

    #run noisy GS
    matchings = hm.solve_hospital_gs(noisy_res_prefs, noisy_hos_prefs, args.quota)
    #compute borda given initial preference lists
    noisy_r_borda, noisy_h_borda, _, _ = hm.get_polygamous_res(res_prefs, hos_prefs, matchings, args.metric)
    noisy_r_mean = hm.get_mean_borda_matched(noisy_r_borda)
    noisy_h_mean = hm.get_mean_borda_matched(noisy_h_borda)

    return init_r_mean, init_h_mean, noisy_r_mean, noisy_h_mean

def noise_run(std_or_max):
    assert(std_or_max in {"std", "max"})
    args = Args()
    args.num_hos = 10
    args.num_res = 100
    args.quota = 10
    args.metric = "borda"
    args.noisy_side = "residents"
    args.window_length = 4
    args.swap_prob = 1
    args.overlap = 0
    args.num_runs = 100
    #args.select_prop = 0.25
    ticks = 5
    phis = [i / (ticks - 1) for i in range(ticks)]
    path = os.path.join("results/noise/hospitals/trial/rand_select", args.noisy_side)

    file_name = get_path_name(args)
    file_path = os.path.join(path, file_name)

    select_prop_range = [i / (ticks - 1) for i in range(ticks)]

    #run
    """ phi_res = 0.1
    phi_to_diffs_sui = dict()
    phi_to_diffs_rev = dict()
    for phi_hos in phis:
        mean_borda_diff_sui = []
        mean_borda_diff_rev = []
        for _ in range(args.num_runs):
            init_res, init_hos, noisy_res, noisy_hos = noise_comparison(args, phi_res, phi_hos, args.select_prop)
            mean_borda_diff_sui.append(noisy_res - init_res)
            mean_borda_diff_rev.append(noisy_hos - init_hos)
        
        if std_or_max == "std":
            phi_to_diffs_sui[phi_hos] = (mean(mean_borda_diff_sui), stdev(mean_borda_diff_sui))
            phi_to_diffs_rev[phi_hos] = (mean(mean_borda_diff_rev), stdev(mean_borda_diff_rev))
        else:
            phi_to_diffs_sui[phi_hos] = (mean(mean_borda_diff_sui), max(mean_borda_diff_sui), min(mean_borda_diff_sui))
            phi_to_diffs_rev[phi_hos] = (mean(mean_borda_diff_rev), max(mean_borda_diff_rev), min(mean_borda_diff_rev))

    if std_or_max == "std":
        graph_mean_stdev_multiple([phi_to_diffs_sui, phi_to_diffs_rev], file_name + "_phi_sui_" + str(phi_res), file_path + "_phi_sui_" + str(phi_res), "phi hospitals", "Mean of Borda score diff", ["residents", 'hospitals'])
    else:
        graph_min_max_multiple([phi_to_diffs_sui, phi_to_diffs_rev], file_name + "_phi_sui_" + str(phi_res), file_path + "_phi_sui_" + str(phi_res), "phi hospitals", "Mean of Borda score diff", ["residents", 'hospitals']) """
    
    args.phi_res = 0.1
    args.phi_hos = 0.5
    phi_to_diffs_sui = dict()
    phi_to_diffs_rev = dict()
    for prop in select_prop_range:
        mean_borda_diff_sui = []
        mean_borda_diff_rev = []
        for _ in range(args.num_runs):
            init_res, init_hos, noisy_res, noisy_hos = noise_comparison(args, args.phi_res, args.phi_hos, prop)
            mean_borda_diff_sui.append(noisy_res - init_res)
            mean_borda_diff_rev.append(noisy_hos - init_hos)
        
        if std_or_max == "std":
            phi_to_diffs_sui[prop] = (mean(mean_borda_diff_sui), stdev(mean_borda_diff_sui))
            phi_to_diffs_rev[prop] = (mean(mean_borda_diff_rev), stdev(mean_borda_diff_rev))
        else:
            phi_to_diffs_sui[prop] = (mean(mean_borda_diff_sui), max(mean_borda_diff_sui), min(mean_borda_diff_sui))
            phi_to_diffs_rev[prop] = (mean(mean_borda_diff_rev), max(mean_borda_diff_rev), min(mean_borda_diff_rev))

    if std_or_max == "std":
        graph_mean_stdev_multiple([phi_to_diffs_sui, phi_to_diffs_rev], file_name, file_path, "select_prop", "Mean of Borda score diff", ["residents", 'hospitals'])
    else:
        graph_min_max_multiple([phi_to_diffs_sui, phi_to_diffs_rev], file_name, file_path, "select prop", "Mean of Borda score diff", ["residents", 'hospitals'])

noise_run("std")