#!/usr/bin/env python

# omarin at 20160227
# adapting pymdsetup step 45 to galaxy


import sys
from os import remove
from shutil import move, copy
from os.path import abspath
from pymdsetup.gromacs_wrapper import editconf
from pymdsetup.configuration.settings import str2bool


def create_boxdim(groin, grout, boxtype, distance, centermol,
        gromacs):

    groin_tmp = "{}.gro".format(groin)
    grout_tmp = "{}.gro".format(grout)
    copy(groin, groin_tmp)
    box = editconf.Editconf512(
            input_gro_path=groin_tmp,
            output_gro_path=grout_tmp,
            box_type=boxtype,
            distance_to_molecule=float(distance),
            center_molecule=str2bool(centermol),
            gmx_path=gromacs)

    box.launch()

    move(grout_tmp, grout)
    remove(groin_tmp)


if __name__ == '__main__':
    create_boxdim(*sys.argv[1:])
