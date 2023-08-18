import random, os, sys
cwd = os.getcwd()
sys.path.append(cwd)
from collections import Counter
import matplotlib.pyplot as plt
from utils.graph_vals import *
""" 
num_hos = 20
num_res = 400

ref_res = tuple(sorted([i for i in range(num_hos)], key=lambda k: random.random()))
ref_hos = tuple(sorted([i for i in range(num_res)], key=lambda k: random.random()))
res_prefs = {i: ranking for i, ranking in enumerate(gs_utils.create_asymmetric_mallows_profile(num_res, num_hos, 0.5, ref_res))}
hos_prefs = {i: ranking for i, ranking in enumerate(gs_utils.create_asymmetric_mallows_profile(num_hos, num_res, 0.5, ref_hos))}

noisy_r_borda, noisy_h_borda, _, _ = hm.run_hospital_gs(res_prefs, hos_prefs, 20, "rank")
print(noisy_r_borda, noisy_h_borda) """

grid_stats = {(0, 1): 1, (1, 0): 2, (0, 0): 0.5, (1, 1): 0}
save_name = "dummy_grid_big"
save_path = "results/dummy_grid_medium"
#graph_grid(grid_stats, save_name, save_path, "x", "y")

xs = [0.2 * i for i in range(10)]
ys = [0.1 + 0.2 * i for i in range(10)]
intersection_matrix = [[1, 2, 3], [3, 0, -1], [0, 2, 5]]

stats_dico = {}
for x in xs:
    for y in ys:
        stats_dico[(x, y)] = x * y
graph_grid(stats_dico, save_name, save_path, (0, 1), "x", "y")