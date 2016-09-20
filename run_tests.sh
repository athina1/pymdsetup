#!/bin/bash

source activate pymdsetup
#nosetests /home/pau/projects/pymdsetup/test
for testfile in test/test_*.py;
do
   python $testfile
done
rm \#*
