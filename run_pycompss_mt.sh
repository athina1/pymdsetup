#!/bin/bash
module purge
module load COMPSs/2.1.rc1709
module unload PYTHON
module load openmpi/1.8.1 gcc/4.9.1 cuda/7.0 mkl/11.1 GROMACS/5.1

enqueue_compss \
  --job_dependency=$1 \
  --exec_time=$2 \
  --gpus_per_node=2 \
  --num_nodes=$3 \
  --worker_working_dir=gpfs \
  --network=infiniband \
  --lang=python \
  --pythonpath=/gpfs/home/bsc23/bsc23210/pymdsetup/:/gpfs/home/bsc23/bsc23210/ \
  --master_working_dir=/gpfs/scratch/bsc23/bsc23210/ \
  --worker_working_dir=/gpfs/scratch/bsc23/bsc23210/ \
  --tracing=$4 \
  --graph=$5 \
  --log_level=debug \
/gpfs/home/bsc23/bsc23210/pymdsetup/workflows/gromacs_full_pycompss.py $6 $7 $3 $8 $9 ${10} ${11} ${12} ${13} ${14} ${15} ${16} ${17} ${18} ${19} ${20}

#/gpfs/home/bsc23/bsc23210/pymdsetup/run_pycompss_mt.sh None 20 3 false false /gpfs/home/bsc23/bsc23210/pymdsetup/workflows/conf_2mut_gpu_test.yaml minotauro
