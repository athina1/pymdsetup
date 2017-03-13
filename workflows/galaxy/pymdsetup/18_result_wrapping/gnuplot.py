#!/usr/bin/env python

# omarin at 20160306
# adapting pymdsetup step 18 to galaxy


import sys
import time
from os import remove
from shutil import move, copy
from pymdsetup.gnuplot_wrapper import gnuplot


def xvg_todict(l):
    d = {}
    ln = len(l)

    for m, n in zip(range(0, ln-1, 2), range(1, ln, 2)):
        d[l[m]] = l[n]

    return d


def run_gnuplot(pngout, plotscrout, gnuplot_path,
        *xvgpaths):

    pngout_tmp = '{}.gro'.format(pngout)
    plot_tmp = '{}.trr'.format(plotscrout)

    xvg_dict = xvg_todict(xvgpaths)

    plot = gnuplot.Gnuplot46(
            input_xvg_path_dict=xvg_dict,
            output_png_path=pngout_tmp,
            output_plotscript_path=plot_tmp,
            gnuplot_path=gnuplot_path)
    plot.launch()

    move(pngout_tmp, pngout)
    move(plot_tmp, plotscrout)
    print(time.time())

if __name__ == '__main__':
    run_gnuplot(*sys.argv[1:])
