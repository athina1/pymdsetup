"""Python wrapper for the GROMACS rms module
"""
import sys
import json
import configuration.settings as settings
from command_wrapper import cmd_wrapper

class Rms(object):
    """Wrapper for the 5.1.2 version of the rms module
    Args:
        input_gro_path (str): Path to the original (before launching the trajectory) GROMACS structure file GRO.
        input_trr_paht (str): Path to the GROMACS uncompressed raw trajectory file TRR.
        output_xvg_path (str): Path to the simple xmgrace plot file XVG.
        properties (dic):
            gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, input_gro_path, input_trr_path, output_xvg_path,
                 properties, **kwargs):
        if isinstance(properties, basestring):
            properties=json.loads(properties)
        self.input_gro_path = input_gro_path
        self.input_trr_path = input_trr_path
        self.output_xvg_path = output_xvg_path
        self.gmx_path = properties['gmx_path']
        self.path = properties.get('path','')

    def launch(self):
        """Launches the execution of the GROMACS rms module.
        """
        out_log, err_log = settings.get_logs(self.path)
        gmx = 'gmx' if self.gmx_path is 'None' else self.gmx_path
        cmd = ['echo', '0 0', '|', gmx, 'rms',
               '-s', self.input_gro_path,
               '-f', self.input_trr_path,
               '-o', self.output_xvg_path,
               '-xvg', 'none']

        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        command.launch()

#Creating a main function to be compatible with CWL
def main():
    step=sys.argv[4]
    prop=sys.argv[5]
    step, system = step.split(':')
    prop = settings.YamlReader(prop, system).get_prop_dic()[step]
    prop['path']=''
    Rms(input_gro_path=sys.argv[1],
        input_trr_path=sys.argv[2],
        output_xvg_path=sys.argv[3],
        step=step,
        properties=prop).launch()

if __name__ == '__main__':
    main()
