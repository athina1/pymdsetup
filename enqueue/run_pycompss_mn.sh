#!/bin/bash

enqueue_compss \
  --job_dependency=$1 \
  --exec_time=$2 \
  --num_nodes=$3 \
  --max_tasks_per_node=1 \
  --qos=bsc_ls \
  --worker_working_dir=scratch \
  --network=infiniband \
  --lang=python \
  --pythonpath=/gpfs/home/bsc23/bsc23210/pymdsetup/:/gpfs/home/bsc23/bsc23210/ \
  --master_working_dir=/gpfs/scratch/bsc23/bsc23210/ \
  --worker_working_dir=/gpfs/scratch/bsc23/bsc23210/ \
  --tracing=$4 \
  --graph=$5 \
  --log_level=debug \
/gpfs/home/bsc23/bsc23210/pymdsetup/workflows/pyruvateKinase_MN.py $6 $7 $3 $8 $9 ${10} ${11} ${12} ${13} ${14} ${15} ${16} ${17} ${18} ${19} ${20}

#bash /gpfs/home/bsc23/bsc23210/pymdsetup/enqueue/run_pycompss_mn.sh None 15 3 false false /gpfs/home/bsc23/bsc23210/pymdsetup/workflows/conf/conf_pyruvateKinase_MN_test.yaml mare_nostrum
