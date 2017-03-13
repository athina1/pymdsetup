#!/usr/bin/env python

# omarin at 20160208
# call step 1 of pymdsetup


import sys
import time

from mmb_api import pdb


def step_1(pdb_name_file, path):
    print(time.time())
    with open(pdb_name_file) as f:
        pdb_name = f.readline().strip()
    mmbpdb = pdb.MmbPdb(pdb_name, path)
    mmbpdb.get_pdb()


if __name__ == '__main__':
    step_1(sys.argv[1], sys.argv[2])
