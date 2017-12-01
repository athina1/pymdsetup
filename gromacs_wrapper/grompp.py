#!/usr/bin/env python

"""Python wrapper for the GROMACS grompp module
"""
import sys
import json
import configuration.settings as settings
from command_wrapper import cmd_wrapper
from tools import file_utils as fu

class Grompp(object):
    """Wrapper for the 5.1.2 version of the GROMACS grompp module.
    The GROMACS preprocessor module needs to be feeded with the input system
    and the molecular dynamics parameter file MDP, to create a portable binary
    run input file TPR.
    Args:
        input_gro_path (str): Path to the input GROMACS structure GRO file.
        input_top_zip_path (str): Path the input GROMACS topology TOP file.
        output_tpr_path (str): Path to the output portable binary run file TPR.
        input_cpt_path (str): Path to the input GROMACS checkpoint file CPT.
        input_mdp_path (str): Path to the input GROMACS parameter input file MDP.
        properties (dic):
            gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, input_gro_path, input_top_zip_path, input_mdp_path,
                 output_tpr_path, properties, input_cpt_path=None, **kwargs):
        if isinstance(properties, basestring):
            properties=json.loads(properties)
        self.input_gro_path = input_gro_path
        self.input_top_zip_path = input_top_zip_path
        self.output_tpr_path = output_tpr_path
        self.input_cpt_path = input_cpt_path
        self.input_mdp_path=input_mdp_path
        self.output_mdp_path= properties.get('output_mdp_path', None)
        self.gmx_path = properties.get('gmx_path', None)
        self.mutation = properties.get('mutation',None)
        self.step = properties.get('step',None)
        self.path = properties.get('path','')
        self.mpirun = properties.get('mpirun', False)
        self.mpirun_np = properties.get('mpirun_np', None)

    def launch(self):
        """Launches the execution of the GROMACS grompp module.
        """
        out_log, err_log = fu.get_logs(path=self.path, mutation=self.mutation, step=self.step)
        # Unzip topology in de directory of the output_tpr_path and get the
        # topology path
        topology_path = fu.unzip_top(self.input_top_zip_path)
        gmx = 'gmx' if self.gmx_path is None else self.gmx_path
        cmd = [gmx, 'grompp', '-f', self.input_mdp_path,
               '-c', self.input_gro_path,
               '-p', topology_path,
               '-o', self.output_tpr_path]

        if self.mpirun_np is not None:
            cmd.insert(0, str(self.mpirun_np))
            cmd.insert(0, '-np')
        if self.mpirun:
            cmd.insert(0, 'mpirun')
        if self.input_cpt_path is not None:
            cmd.append('-t')
            cmd.append(self.input_cpt_path)
        if self.output_mdp_path is not None:
            cmd.append('-po')
            cmd.append(self.output_mdp_path)

        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        return command.launch()

#Creating a main function to be compatible with CWL
def main():
    if len(sys.argv) < 9:
        sys.argv.append(None)
    system=sys.argv[1]
    step=sys.argv[2]
    properties_file=sys.argv[3]
    prop = settings.YamlReader(properties_file, system).get_prop_dic()[step]
    Grompp(input_gro_path = sys.argv[4],
           input_top_zip_path = sys.argv[5],
           input_mdp_path = sys.argv[6],
           output_tpr_path = sys.argv[7],
           input_cpt_path = sys.argv[8],
           properties=prop).launch()

if __name__ == '__main__':
    main()
