#!/bin/bash

enqueue_compss \
  --exec_time=$1 \
  --num_nodes=$2 \
  --queue=$5 \
  --tasks_per_node=16 \
  --master_working_dir=. \
  --worker_working_dir=gpfs \
  --network=infiniband \
  --lang=python \
  --pythonpath=/gpfs/home/bsc51/bsc51210/pymdsetup/:/gpfs/home/bsc51/bsc51210/ \
  --tracing=$3 \
  --graph=$4 \
  --log_level=off \
/gpfs/home/bsc51/bsc51210/pymdsetup/workflows/gromacs_full_pycompss_test.py $6 $7 $8 $9 ${10} ${11} ${12} ${13} ${14} ${15} ${16} ${17} ${18} ${19} ${20}

#./run_pycompss_mn.sh 120 3 false false bsc_ls
#./run_pycompss_mn.sh 60 3 false false debug
#./run_pycompss_mn.sh 120 3 false false bsc_debug
