#!/bin/bash
# set the number of nodes
#SBATCH --nodes=1
# set max wallclock time
#SBATCH --time=01:00:00
# set name of job
#SBATCH --job-name=setup_src
# partition priority
#SBATCH --partition=short
# mail alert at start, end and abortion of execution
#SBATCH --mail-type=ALL
# send mail to this address
#SBATCH --mail-user=raph.selz@gmail.com

#activate the environment
source proj_venv/bin/activate
# run the application
python gs_experiments/asymmetry.py
