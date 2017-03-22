#!/usr/bin/env python

# omarin at 20160303
# adapting pymdsetup step 17 to galaxy


import sys
from os import remove
from shutil import move, copy
from pymdsetup.gromacs_wrapper import rms


def run_intrarmsd(groin, trrin, xvgout,
        gromacs):

    groin_tmp = '{}.gro'.format(groin)
    trrin_tmp = '{}.trr'.format(trrin)
    xvgout_tmp = '{}.xvg'.format(xvgout)

    copy(groin, groin_tmp)
    copy(trrin, trrin_tmp)

    rmsd = rms.Rms512(
            input_gro_path=groin_tmp,
            input_trr_path=trrin_tmp,
            output_xvg_path=xvgout_tmp,
            gmx_path=gromacs)
    rmsd.launch()

    remove(groin_tmp)
    remove(trrin_tmp)
    move(xvgout_tmp, xvgout)

if __name__ == '__main__':
    run_intrarmsd(*sys.argv[1:])
