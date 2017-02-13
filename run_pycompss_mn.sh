#!/bin/bash

enqueue_compss \
  --exec_time=$1 \
  --num_nodes=$2 \
  --queue=bsc_ls \
  --tasks_per_node=1 \
  --master_working_dir=. \
  --worker_working_dir=gpfs \
  --network=infiniband \
  --lang=python \
  --pythonpath=/gpfs/home/bsc51/bsc51210/pymdsetup/:/gpfs/home/bsc51/bsc51210/ \
  --tracing=$3 \
  --graph=$4 \
  --log_level=off \
/gpfs/home/bsc51/bsc51210/pymdsetup/workflows/gromacs_full_pycompss_test.py $5 $6 $7 $8 $9 ${10} ${11} ${12} ${13} ${14} ${15} ${16} ${17} ${18} ${19} ${20}

#./run_pycompss_mn.sh 10 3 false false
