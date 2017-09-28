#!/bin/bash
#SBATCH --job-name="pymdsetup"
#SBATCH -D .
#SBATCH --output=serial_%j.out
#SBATCH --error=serial_%j.err
#SBATCH --ntasks=1
#SBATCH --time=00:10:00
#SBATCH --qos=debug
python workflows/gromacs_full.py workflows/conf_2mut_nt0.yaml mare_nostrum > out.txt
