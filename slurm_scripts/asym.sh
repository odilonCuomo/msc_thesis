#!/bin/bash
# set the number of nodes
#SBATCH --nodes=1
# set max wallclock time
#SBATCH --time=47:00:00
# set name of job
#SBATCH --job-name=asymmetry_grid
# partition priority
#SBATCH --partition=medium
# mail alert at start, end and abortion of execution
#SBATCH --mail-type=ALL
# send mail to this address
#SBATCH --mail-user=raph.selz@gmail.com

#activate the environment
source proj_venv/bin/activate
# run the application
python gs_experiments/asymmetry.py --n 15 --num_runs 1000 --borda True --grid True --ticks 10
python gs_experiments/asymmetry.py --n 50 --num_runs 1000 --borda True --grid True --ticks 10
python gs_experiments/asymmetry.py --n 150 --num_runs 500 --borda True --grid True --ticks 10
