#!/usr/bin/env python

# omarin at 20160302
# adapting pymdsetup step 10 to galaxy


import sys
from os import remove
from shutil import move, copy
from pymdsetup.gromacs_wrapper import mdrun


def run_md_energy(tprin, grout, trrout, edrout,
        gromacs):

    grout_tmp = '{}.gro'.format(grout)
    trrout_tmp = '{}.trr'.format(trrout)
    edrout_tmp = '{}.edr'.format(edrout)
    tpr_tmp = '{}.tpr'.format(tprin)

    copy(tprin, tpr_tmp)

    energymin = mdrun.Mdrun512(
            input_tpr_path=tpr_tmp,
            output_gro_path=grout_tmp,
            output_trr_path=trrout_tmp,
            output_edr_path=edrout_tmp,
            gmx_path=gromacs)
    energymin.launch()

    remove(tpr_tmp)
    move(grout_tmp, grout)
    move(trrout_tmp, trrout)
    move(edrout_tmp, edrout)

if __name__ == '__main__':
    run_md_energy(*sys.argv[1:])
