#!/bin/bash
# set the number of nodes
#SBATCH --nodes=1
# set max wallclock time
#SBATCH --time=02:00:00
# set name of job
#SBATCH --job-name=noise_correlation
# partition priority
#SBATCH --partition=short
# mail alert at start, end and abortion of execution
#SBATCH --mail-type=ALL
# send mail to this address
#SBATCH --mail-user=raph.selz@gmail.com

#activate the environment
source proj_venv/bin/activate
# run the application
python gs_experiments/noisy_matching.py