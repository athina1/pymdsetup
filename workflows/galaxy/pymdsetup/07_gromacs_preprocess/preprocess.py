#!/usr/bin/env python

# omarin at 20160228
# adapting pymdsetup step 7 to galaxy


import sys
from os import remove
from shutil import move, copy
from pymdsetup.gromacs_wrapper import grompp


def create_mdp_file(arglist, basepath):
    outpath = '{}.mdp'.format(basepath)
    with open(outpath, 'w') as f:
        f.write('integrator = {}\n'.format(arglist[0]))
        f.write('emtol = {}\n'.format(arglist[1]))
        f.write('emstep = {}\n'.format(arglist[2]))
        f.write('nsteps = {}\n\n'.format(arglist[3]))
        f.write('nstlist= {}\n'.format(arglist[4]))
        f.write('cutoff-scheme = {}\n'.format(arglist[5]))
        f.write('ns_type = {}\n'.format(arglist[6]))
        f.write('coulombtype = {}\n'.format(arglist[7]))
        f.write('rcoulomb = {}\n'.format(arglist[8]))
        f.write('rvdw = {}\n'.format(arglist[9]))
        f.write('pbc = {}\n'.format(arglist[10]))

    return outpath


def preprocess_ions(groin, topin, tprout, gromacs,
        *stuff):
        #integrator, emtol, emstep, nsteps,
        #nstlist, cutoff-scheme, ns_type, coulombtype, rcoulomb,
        #rvdw, pbc):

    groin_tmp = '{}.gro'.format(groin)
    tpr_tmp = '{}.tpr'.format(tprout)
    intar = '{}.tar'.format(topin)

    mdp_path = create_mdp_file(stuff, groin)
    copy(topin, intar)
    copy(groin, groin_tmp)

    ions = grompp.Grompp512(
            input_mdp_path=mdp_path,
            input_gro_path=groin_tmp,
            input_top_tar_path=intar,
            output_tpr_path=tpr_tmp,
            gmx_path=gromacs)
    ions.launch()

    remove(groin_tmp)
    remove(mdp_path)
    remove(intar)
    move(tpr_tmp, tprout)

if __name__ == '__main__':
    preprocess_ions(*sys.argv[1:])
