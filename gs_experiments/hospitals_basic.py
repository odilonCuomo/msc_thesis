import os, sys
cwd = os.getcwd()
sys.path.append(cwd)
from utils.args import Args, get_path_name
from matching.games import HospitalResident
from statistics import mean
import numpy as np
import diversity.hospital_matching as hm


"""
setting
- no unacceptable matches
- complete preferences are given
- possible unmatched agents at the end (although we start with 400/20-20)
"""
np.random.seed(0)
#random trial
args = Args()
args.num_runs = 500
args.num_res = 400
args.num_hos = 20
args.quota = 20

r_bordas, h_bordas = [], []
r_unmatched, h_unmatched = [], []

for _ in range(args.num_runs):
    r_borda, h_borda, r_un, h_un = hm.run_hospital_gs(args.num_res, args.num_hos, args.quota)
    r_unmatched.append(r_un)
    h_unmatched.append(h_un)
    r_bordas.append(hm.get_mean_borda_matched(r_borda))
    h_bordas.append(hm.get_mean_borda_matched(h_borda))

print("Mean nb_unmatched residents:")
print(mean(r_unmatched))
print("Mean nb_unmatched hospitals:")
print(mean(h_unmatched))
print("Mean borda on matched residents:")
print(mean(r_bordas))
print("Mean borda on matched hospitals:")
print(mean(h_bordas))