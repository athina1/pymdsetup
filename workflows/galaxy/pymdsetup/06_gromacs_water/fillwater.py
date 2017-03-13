#!/usr/bin/env python

# omarin at 20160227
# adapting pymdsetup step 6 to galaxy


import sys
from os import remove
from shutil import move, copy
from pymdsetup.gromacs_wrapper import solvate


def fill_waters(groin, topin, input_solvent, grout, topout, tarout,
        gromacs):

    groin_tmp = "{}.gro".format(groin)
    grout_tmp = "{}.gro".format(grout)
    topout_tmp = "{}.top".format(topout)
    intar = "{}.tar".format(topin)

    copy(topin, intar)
    copy(groin, groin_tmp)
    copy(topout, topout_tmp)

    waters = solvate.Solvate512(
            input_solute_gro_path=groin_tmp,
            output_gro_path=grout_tmp,
            input_top_tar_path=intar,
            output_top_path=topout_tmp,
            output_top_tar_path=tarout,
            input_solvent_gro_path=input_solvent,
            gmx_path=gromacs)
    waters.launch()

    move(grout_tmp, grout)
    remove(groin_tmp)
    move(topout_tmp, topout)
    remove(intar)

if __name__ == '__main__':
    fill_waters(*sys.argv[1:])
