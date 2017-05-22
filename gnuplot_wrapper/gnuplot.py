"""Python wrapper module for SCWRL
"""
import os
import sys
try:
    from command_wrapper import cmd_wrapper
    from tools import file_utils as fu
except ImportError:
    from pymdsetup.command_wrapper import cmd_wrapper
    from pymdsetup.tools import file_utils as fu


class Gnuplot46(object):
    """Wrapper class for the 4.6 version of GNUPLOT.

    Args:
        input_xvg_path_dict (dict): Dict where keys are mutations (str) and
                                    values are paths (str) to xvg rmsd files.
        output_png_path (srt): Path to the output png chart file.
        output_plotscript_path (str): Path to the output GNUPLOT script file.
        log_path (str): Path to the file where the log will be stored.
        error_path (str): Path to the file where the error log will be stored.
        gnuplot_path (str): Path to the GNUPLOT executable binary.
    """

    def __init__(self, input_xvg_path_dict, output_png_path,
                 output_plotscript_path,
                 log_path=None, error_path=None, gnuplot_path=None):
        self.input_xvg_path_dict = input_xvg_path_dict
        self.output_png_path = output_png_path
        self.output_plotscript_path = output_plotscript_path
        self.log_path = log_path
        self.error_path = error_path
        self.gnuplot_path = gnuplot_path

    def launch(self):
        """Launches the execution of the GNUPLOT binary.
        """

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

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()

#Creating a main function to be compatible with CWL
def main():
    mutation = sys.argv[1]
    xvg_file_path = sys.argv[2]
    Gnuplot46(input_xvg_path_dict={mutation:xvg_file_path},
               output_png_path=sys.argv[3],
               output_plotscript_path=sys.argv[4],
               gnuplot_path=sys.argv[5],
               log_path=sys.argv[6],
               error_path=sys.argv[7]).launch()

if __name__ == '__main__':
    main()
