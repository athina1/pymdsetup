#!/bin/bash
# @ job_name="pymdsetup"
# @ initialdir= .
# @ output= k80_serial_%j.out
# @ error= k80_serial_%j.err
# @ total_tasks=  1
# @ cpus_per_task=  6
# @ gpus_per_node=  1
# @ wall_clock_limit = 00:20:00
module purge
module load openmpi/1.8.1 gcc/4.9.1 cuda/7.0 GROMACS/5.0.4-cuda7
python workflows/gromacs_full.py workflows/conf_2mut_gpu_test.yaml minotauro 1

# mnsubmit mt_serial.sh
