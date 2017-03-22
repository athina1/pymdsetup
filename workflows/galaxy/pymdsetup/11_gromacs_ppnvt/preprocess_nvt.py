#!/usr/bin/env python

# omarin at 20160302
# adapting pymdsetup step 11 to galaxy


import sys
from os import remove
from shutil import move, copy
from pymdsetup.gromacs_wrapper import grompp


def create_mdp_file_nvt(arglist, basepath):
    outpath = '{}.mdp'.format(basepath)
    d = ['title', 'define', 'integrator', 'nsteps', 'dt', 'nstxout', 'nstvout', 'nstenergy', 'nstlog',
            'continuation', 'constraint_algorithm', 'constraints', 'lincs_iter', 'lincs_order',
            'cutoff-scheme', 'ns_type', 'nstlist', 'rcoulomb', 'rvdw', 'coulombtype', 'pme_order',
            'fourierspacing', 'tcoupl', 'tc-grps', 'tau_t', 'ref_t', 'pcoupl', 'pbc', 'DispCorr',
            'gen_vel', 'gen_temp', 'gen_seed']

    with open(outpath, 'w') as f:
        for a, b in zip(d, arglist):
            f.write('{} = {}\n'.format(a, b))

    return outpath


def preprocess_nvt(groin, topin, tprout, gromacs,
        *stuff):
        #integrator, emtol, emstep, nsteps,
        #nstlist, cutoff-scheme, ns_type, coulombtype, rcoulomb,
        #rvdw, pbc):
    groin_tmp = '{}.gro'.format(groin)
    tpr_tmp = '{}.tpr'.format(tprout)
    intar = '{}.tar'.format(topin)

    mdp_path = create_mdp_file_nvt(stuff, groin)
    copy(topin, intar)
    copy(groin, groin_tmp)

    constants = grompp.Grompp512(
            input_mdp_path=mdp_path,
            input_gro_path=groin_tmp,
            input_top_tar_path=intar,
            output_tpr_path=tpr_tmp,
            gmx_path=gromacs)
    constants.launch()

    remove(groin_tmp)
    remove(mdp_path)
    remove(intar)
    move(tpr_tmp, tprout)

if __name__ == '__main__':
    preprocess_nvt(*sys.argv[1:])
