"""Python wrapper module for SCWRL
"""
import os
import sys
import json
from os.path import join as opj
import configuration.settings as settings
from command_wrapper import cmd_wrapper
from tools import file_utils as fu

class Gnuplot(object):
    """Wrapper class for the 4.6 version of GNUPLOT.
    Args:
        input_xvg_path_dict (dict): Dict where keys are mutations (str) and
                                    values are paths (str) to xvg rmsd files.
        output_png_path (srt): Path to the output png chart file.
        properties (dic):
            output_plotscript_path (str): Path to the output GNUPLOT script file.
            gnuplot_path (str): Path to the GNUPLOT executable binary.
    """
    def __init__(self, input_xvg_path_dict, output_png_path,
                 properties, **kwargs):
        if isinstance(properties, basestring):
            properties=json.loads(properties)
        self.input_xvg_path_dict = input_xvg_path_dict
        self.output_png_path = output_png_path
        self.output_plotscript_path = opj(properties.get('path',''), properties['output_plotscript_path'])
        self.gnuplot_path = properties['gnuplot_path']
        self.path = properties.get('path','')

    def launch(self):
        """Launches the execution of the GNUPLOT binary.
        """
        out_log, err_log = settings.get_logs(self.path)
        # Create the input script for gnuplot
        lb = os.linesep
        with open(self.output_plotscript_path, 'w') as ps:
            ps.write('set term png'+lb)
            ps.write('set output "' + self.output_png_path + '"'+lb)
            ps.write('plot')
            for k, v in self.input_xvg_path_dict.iteritems():
                ps.write(' "' + v + '" u 1:2 w lp t "' + k + '",')

        gplot = 'gnuplot' if self.gnuplot_path is None else self.gnuplot_path
        cmd = [gplot, self.output_plotscript_path]

        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        command.launch()

#Creating a main function to be compatible with CWL
def main():
    Gnuplot(input_xvg_path_dict={'mutation':sys.argv[1]},
            output_png_path=sys.argv[2],
            properties=sys.argv[3]).launch()

if __name__ == '__main__':
    main()
