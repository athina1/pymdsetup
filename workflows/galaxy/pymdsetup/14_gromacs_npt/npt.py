#!/usr/bin/env python

# omarin at 20160302
# adapting pymdsetup step 14 to galaxy


import sys
from os import remove
from shutil import move, copy
from pymdsetup.gromacs_wrapper import mdrun


def run_md_npt(tprin, grout, trrout, edrout, cptout,
        gromacs):

    grout_tmp = '{}.gro'.format(grout)
    trrout_tmp = '{}.trr'.format(trrout)
    edrout_tmp = '{}.edr'.format(edrout)
    tpr_tmp = '{}.tpr'.format(tprin)
    cptout_tmp = '{}.cpt'.format(cptout)

    copy(tprin, tpr_tmp)

    mdnpt = mdrun.Mdrun512(
            input_tpr_path=tpr_tmp,
            output_gro_path=grout_tmp,
            output_trr_path=trrout_tmp,
            output_edr_path=edrout_tmp,
            output_cpt_path=cptout_tmp,
            gmx_path=gromacs)
    mdnpt.launch()

    remove(tpr_tmp)
    move(grout_tmp, grout)
    move(trrout_tmp, trrout)
    move(edrout_tmp, edrout)
    move(cptout_tmp, cptout)

if __name__ == '__main__':
    run_md_npt(*sys.argv[1:])
