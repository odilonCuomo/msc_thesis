#!/bin/bash
# set the number of nodes
#SBATCH --nodes=1
# set max wallclock time
#SBATCH --time=47:00:00
# set name of job
#SBATCH --job-name=noise_matching
# partition priority
#SBATCH --partition=medium
# mail alert at start, end and abortion of execution
#SBATCH --mail-type=ALL
# send mail to this address
#SBATCH --mail-user=raph.selz@gmail.com

#activate the environment
source proj_venv/bin/activate
# run the application
echo 0 / 4
python gs_experiments/noisy_matching.py --metric "GRID_MEAN" --n 50 --noisy_side "both" --num_runs 500 --noise_type "LOCAL"
echo 1 / 4
python gs_experiments/noisy_matching.py --metric "GRID_MEAN" --n 50 --noisy_side "suitors" --num_runs 500 --noise_type "LOCAL"
echo 2 / 4
python gs_experiments/noisy_matching.py --metric "GRID_MEAN" --n 50 --noisy_side "reviewers" --num_runs 500 --noise_type "LOCAL"
echo 3 / 4