#!/bin/bash
# @ job_name="pymdsetup"
# @ initialdir= .
# @ output= k80_serial_%j.out
# @ error= k80_serial_%j.err
# @ total_tasks=  2
# @ cpus_per_task=  6
# @ gpus_per_node=  2
# @ features = k80
# @ wall_clock_limit = 20:00:00
module purge
module load openmpi/1.8.1 gcc/4.9.1 cuda/7.0 mkl/11.1 GROMACS/5.1
python workflows/gromacs_full.py workflows/conf_2mut_gpu.yaml minotauro 1

# mnsubmit mt_serial.sh
