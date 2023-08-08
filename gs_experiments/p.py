import random, os, sys
cwd = os.getcwd()
sys.path.append(cwd)
from collections import Counter
import matplotlib.pyplot as plt
""" 
num_hos = 20
num_res = 400

ref_res = tuple(sorted([i for i in range(num_hos)], key=lambda k: random.random()))
ref_hos = tuple(sorted([i for i in range(num_res)], key=lambda k: random.random()))
res_prefs = {i: ranking for i, ranking in enumerate(gs_utils.create_asymmetric_mallows_profile(num_res, num_hos, 0.5, ref_res))}
hos_prefs = {i: ranking for i, ranking in enumerate(gs_utils.create_asymmetric_mallows_profile(num_hos, num_res, 0.5, ref_hos))}

noisy_r_borda, noisy_h_borda, _, _ = hm.run_hospital_gs(res_prefs, hos_prefs, 20, "rank")
print(noisy_r_borda, noisy_h_borda) """

d = {1: "a", 2: "b", 3: "c"}
print(random.sample(list(d.keys()), 3))