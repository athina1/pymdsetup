#!/bin/bash

#setup
test_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $test_dir/yaml_parser.sh
eval $(parse_yaml $test_dir/conf_test.yaml)
wd=$pymdsetup_path/$p2g_paths_path
mkdir $wd

#Run command
cd $wd && \
python \
$pymdsetup_path/$p2g_paths_script \
$pymdsetup_path/$p2g_paths_in_pdb \
$wd/$p2g_paths_gro \
$wd/$p2g_paths_top \
$p2g_paths_itp \
$wd/$p2g_paths_tar \
$p2g_properties_water_type \
$p2g_properties_force_field \
$p2g_properties_ignh \
$gmx_path \
$wd/$p2g_paths_out \
$wd/$p2g_paths_err

#Run tests
test1=$(diff $wd/$p2g_paths_gro $pymdsetup_path/$p2g_paths_gold_gro)
test2=$(diff -I '^;.*' $wd/$p2g_paths_top $pymdsetup_path/$p2g_paths_gold_top)
test3=$(diff $wd/$p2g_paths_itp $pymdsetup_path/$p2g_paths_gold_itp)

echo -e "Test1:"
echo $test1
echo ""

echo -e "Test2:"
echo $test2
echo ""

echo -e "Test3:"
echo $test3
echo ""

#teardown
rm *.itp
rm -rf $wd
