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

printf "cd $wd && \
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
$wd/$p2g_paths_err"
echo ""
echo ""

#Run tests
test1=$(diff $wd/$p2g_paths_gro $pymdsetup_path/$p2g_paths_gold_gro)
test2=$(diff -I '^;.*' $wd/$p2g_paths_top $pymdsetup_path/$p2g_paths_gold_top)
test3=$(diff $wd/$p2g_paths_itp $pymdsetup_path/$p2g_paths_gold_itp)

printf "Test1: "
if [ -n "$test1" ]; then
	printf "Error --> "
	printf $test1
else
	printf "OK"
fi
echo ""

printf "Test2: "
if [ -n "$test2" ]; then
	printf "Error --> "
	printf $test2
else
	printf "OK"
fi
echo ""

printf "Test3: "
if [ -n "$test3" ]; then
	printf "Error --> "
	printf $test3
else
	printf "OK"
fi
echo ""

#teardown
rm *.itp
rm -rf $wd
