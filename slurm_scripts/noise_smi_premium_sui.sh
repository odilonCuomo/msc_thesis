#!/bin/bash
# set the number of nodes
#SBATCH --nodes=1
# set max wallclock time
#SBATCH --time=07:00:00
# set name of job
#SBATCH --job-name=noise_smi_premium
# partition priority
#SBATCH --partition=short
# mail alert at start, end and abortion of execution
#SBATCH --mail-type=ALL
# send mail to this address
#SBATCH --mail-user=raph.selz@gmail.com

#activate the environment
source proj_venv/bin/activate
# run the application
# same bound
echo 2 /
python gs_experiments/noisy_smi.py --metric "GRID_MEAN" --n 15 --noisy_side "suitors" --num_runs 10 --noise_type "LOCAL" --window_size 2 --prefs_bound_sui 5 --prefs_bound_rev 5 --matched_premium 2

#bound men only
echo 2 /
#python gs_experiments/noisy_smi.py --metric "GRID_MEAN" --n 15 --noisy_side "suitors" --num_runs 1000 --noise_type "RANDOM" --window_size 2 --prefs_bound_sui 5 --prefs_bound_rev 15

#bound women only
echo 2 /
#python gs_experiments/noisy_smi.py --metric "GRID_MEAN" --n 15 --noisy_side "suitors" --num_runs 1000 --noise_type "RANDOM" --window_size 2 --prefs_bound_sui 15 --prefs_bound_rev 5