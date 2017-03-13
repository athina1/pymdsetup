#!/usr/bin/env python

# omarin at 20160228
# adapting pymdsetup step 7 to galaxy


import sys
from os import remove
from shutil import move, copy
from pymdsetup.gromacs_wrapper import grompp


def create_mdp_file(arglist, basepath):
    argnames = ['title', 'integrator', 'nsteps', 'dt', 'nstxout', 'nstvout', 'nstenergy',
            'nstlog', 'nstxout-compressed', 'compressed-x-grps', 'continuation', 'constraint_algorithm',
            'constraints', 'lincs_iter', 'lincs_order', 'cutoff-scheme', 'ns_type',
            'nstlist', 'rcoulomb', 'rvdw', 'coulombtype', 'pme_order', 'fourierspacing',
            'tcoupl', 'tc-grps', 'tau_t', 'ref_t', 'pcoupl', 'pcoupltype', 'tau_p', 'ref_p',
            'compressibility', 'pbc', 'DispCorr', 'gen_vel'
            ]
    outpath = '{}.mdp'.format(basepath)
    with open(outpath, 'w') as f:
        for n in range(len(argnames)):
            f.write('{} = {}\n'.format(argnames[n], arglist[n]))
    return outpath


def preprocess_npt(groin, topin, cptin, tprout, gromacs,
        *stuff):
        #integrator, emtol, emstep, nsteps,
        #nstlist, cutoff-scheme, ns_type, coulombtype, rcoulomb,
        #rvdw, pbc):

    groin_tmp = '{}.gro'.format(groin)
    tpr_tmp = '{}.tpr'.format(tprout)
    intar = '{}.tar'.format(topin)
    cptin_tmp = '{}.cpt'.format(cptin)

    mdp_path = create_mdp_file(stuff, groin)
    copy(topin, intar)
    copy(cptin, cptin_tmp)
    copy(groin, groin_tmp)

    pp_eq = grompp.Grompp512(
            input_mdp_path=mdp_path,
            input_gro_path=groin_tmp,
            input_top_tar_path=intar,
            input_cpt_path=cptin_tmp,
            output_tpr_path=tpr_tmp,
            gmx_path=gromacs)
    pp_eq.launch()

    remove(groin_tmp)
    remove(mdp_path)
    remove(cptin_tmp)
    remove(intar)
    move(tpr_tmp, tprout)

if __name__ == '__main__':
    preprocess_npt(*sys.argv[1:])
