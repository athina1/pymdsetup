#!/usr/bin/env python

# omarin at 20160228
# adapting pymdsetup step 8 to galaxy


import sys
from os import remove
from shutil import move, copy
from pymdsetup.gromacs_wrapper import genion


def fill_ions(tprin, grout, topin, topout, tarout,
        neutral, concentration, gromacs):

    grout_tmp = '{}.gro'.format(grout)
    tpr_tmp = '{}.tpr'.format(tprin)
    topout_tmp = '{}.top'.format(topout)
    intar = '{}.tar'.format(topin)

    copy(topin, intar)
    copy(grout, grout_tmp)
    copy(tprin, tpr_tmp)

    ions = genion.Genion512(
            input_tpr_path=tpr_tmp,
            output_gro_path=grout_tmp,
            input_top_tar_path=intar,
            output_top_path=topout_tmp,
            output_top_tar_path=tarout,
            neutral=neutral,
            concentration=concentration,
            gmx_path=gromacs)
    ions.launch()

    remove(tpr_tmp)
    remove(intar)
    move(grout_tmp, grout)
    move(topout_tmp, topout)

if __name__ == '__main__':
    fill_ions(*sys.argv[1:])
