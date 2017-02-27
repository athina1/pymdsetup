#!/bin/bash

#setup
test_dir="test"
source $test_dir/yaml_parser.sh
eval $(parse_yaml $test_dir/conf_test.yaml)
mkdir $p2g_paths_path
cd $p2g_paths_path

#Run TestCase
python
$p2g_paths_script \
# ../data/pdb2gmx/input_structure.pdb \
# p2g.gro \
# p2g.top \
# p2g_top.tar \
# spce \
# oplsaa \
# True \
# /usr/bin/g
#
#
#
#
# #teardown
# cd ..
# rm -rf p2g_cml
