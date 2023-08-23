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
echo Local
echo 0 / 1
python gs_experiments/noisy_matching.py --metric "GRID_MEAN" --n 15 --noisy_side "both" --num_runs 1000 --noise_type "LOCAL" --window_size 2
echo 1 / 1
python gs_experiments/noisy_matching.py --metric "GRID_MEAN" --n 15 --noisy_side "suitors" --num_runs 1000 --noise_type "LOCAL" --window_size 2
echo 2 / 1
python gs_experiments/noisy_matching.py --metric "GRID_MEAN" --n 15 --noisy_side "reviewers" --num_runs 1000 --noise_type "LOCAL" --window_size 2
echo 3 / 1