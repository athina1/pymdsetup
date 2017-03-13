#!/usr/bin/env python

# omarin at 20160209
# adapting pymdsetup step 2 to galaxy


import sys
from os import mkdir
from pymdsetup.mmb_api import uniprot


def get_mutations(pdbfilename, n):
    with open(pdbfilename) as f:
        pdbcode = f.readline().strip()
    up = uniprot.MmbVariants(pdbcode)
    mutations = up.get_pdb_variants()

    if len(mutations) > n:
        mutations = mutations[:n]

    path="./output_getmutations"
    mkdir(path)
    for mut in mutations:
    #    mut = "-".join(mut.split("."))
        with open('{}/{}.txt'.format(path, mut), 'w') as f:
            f.write(mut)

if __name__ == '__main__':
    get_mutations(sys.argv[1], int(sys.argv[2]))
