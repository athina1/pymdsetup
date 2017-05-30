#!/bin/bash

#BSUB -n 1
#BSUB -oo output_serial_1_thread.out
#BSUB -eo output_serial_1_thread.err
#BSUB -J sequential
#BSUB -W 08:00

export PYTHONPATH=${PYTHONPATH}:/gpfs/home/bsc51/bsc51210/pymdsetup
python workflows/gromacs_full.py
