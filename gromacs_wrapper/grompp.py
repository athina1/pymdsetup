"""Python wrapper for the GROMACS grompp module
"""
import sys
import json
import os
import configuration.settings as settings
from command_wrapper import cmd_wrapper
from tools import file_utils as fu
from os.path import join as opj

class Grompp(object):
    """Wrapper for the 5.1.2 version of the GROMACS grompp module.
    The GROMACS preprocessor module needs to be feeded with the input system
    and the molecular dynamics parameter file MDP, to create a portable binary
    run input file TPR.
    Args:
        input_gro_path (str): Path to the input GROMACS structure GRO file.
        input_top_tar_path (str): Path the input GROMACS topology TOP file.
        output_tpr_path (str): Path to the output portable binary run file TPR.
        input_cpt_path (str): Path to the input GROMACS checkpoint file CPT.
        input_mdp_path (str): Path to the input GROMACS parameter input file MDP.
        properties (dic):
            gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, input_gro_path, input_top_tar_path, input_mdp_path,
                 output_tpr_path, properties, input_cpt_path=None, **kwargs):
        if isinstance(properties, basestring):
            properties=json.loads(properties)
        self.input_gro_path = input_gro_path
        self.input_top_tar_path = input_top_tar_path
        self.output_tpr_path = output_tpr_path
        self.input_cpt_path = input_cpt_path
        if os.path.isfile(input_mdp_path):
            self.input_mdp_path=input_mdp_path
        else:
            self.input_mdp_path = opj(properties['mdp_path'], input_mdp_path)
        self.gmx_path = properties['gmx_path']
        self.path = properties.get('path','')

    def launch(self):
        """Launches the execution of the GROMACS grompp module.
        """
        out_log, err_log = settings.get_logs(self.path)
        # Untar topology in de directory of the output_tpr_path and get the
        # topology path
        topology_path = fu.untar_top(self.input_top_tar_path, dest_dir=self.output_tpr_path)
        gmx = 'gmx' if self.gmx_path is None else self.gmx_path
        cmd = [gmx, 'grompp', '-f', self.input_mdp_path,
               '-c', self.input_gro_path,
               '-p', topology_path,
               '-o', self.output_tpr_path,
               '-po', opj(self.path, 'mdout.mdp')]
        if self.input_cpt_path is not None:
            cmd.append('-t')
            cmd.append(self.input_cpt_path)

        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        command.launch()

#Creating a main function to be compatible with CWL
def main():
    if len(sys.argv) < 7:
        sys.argv.append(None)
    step=sys.argv[4]
    prop=sys.argv[5]
    step, system = step.split(':')
    prop = settings.YamlReader(prop, system).get_prop_dic()[step]
    prop['path']=''
    Grompp(input_gro_path = sys.argv[1],
              input_top_tar_path = sys.argv[2],
              output_tpr_path = sys.argv[3],
              step=step,
              properties=prop,
              input_cpt_path = sys.argv[6]).launch()

if __name__ == '__main__':
    main()
