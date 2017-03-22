#!/usr/bin/env python

# omarin at 20160227
# adapting pymdsetup step 4 to galaxy


import sys
from os import remove, getcwd
from shutil import move, copy
from os.path import abspath
from pymdsetup.gromacs_wrapper import pdb2gmx
from pymdsetup.configuration.settings import str2bool


def read_mut(path):
    print(path)
    with open(path) as f:
        line = f.readline()
        print(line)
        return line.strip()

def create_topology(pdb, water, forcefield, ignh, mutpath, gromacs,
        out_topology, out_tar, out_gro):

    pdbtmp = "{}.pdb".format(pdb)
    out_grotmp = "{}.gro".format(out_gro)
    out_topologytmp = "{}.top".format(out_topology)
    mut = read_mut(mutpath)
    out_itp = "{}.itp".format(mut)
    copy(pdb, pdbtmp)
    p2g = pdb2gmx.Pdb2gmx512(input_structure_pdb_path=pdbtmp,
            output_gro_path=out_grotmp,
            output_top_path=out_topologytmp,
            output_top_tar_path=out_tar,
            output_itp_path=out_itp,
            water_type=water,
            force_field=forcefield,
            ignh=str2bool(ignh),
            gmx_path=gromacs)

    p2g.launch()

    move(out_grotmp, out_gro)
    move(out_topologytmp, out_topology)
    remove(pdbtmp)


if __name__ == '__main__':
    create_topology(*sys.argv[1:])
