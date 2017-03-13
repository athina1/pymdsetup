#!/usr/bin/env python

# omarin at 20160209
# adapting pymdsetup step 2 to galaxy


import sys
from os import remove
from os.path import abspath
from pymdsetup.scwrl_wrapper import scwrl


def model_mutations(pdb, mutpath, scwrlpath, out):

    with open(mutpath) as f:
        mut = f.readline().strip()
    scw = scwrl.Scwrl4(input_pdb_path=pdb,
            output_pdb_path=out,
            mutation=mut,
            scwrl_path=abspath(scwrlpath))

    scw.launch()
    tmpout = "{}.scwrl4.prepared.pdb".format(out)
    remove(tmpout)


if __name__ == '__main__':
    model_mutations(*sys.argv[1:])
