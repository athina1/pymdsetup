"""Python wrapper for the GROMACS genion module
"""
import os
import sys
import json
import configuration.settings as settings
from command_wrapper import cmd_wrapper
from tools import file_utils as fu
from os.path import join as opj

class Genion(object):
    """Wrapper for the 5.1.2 version of the genion module
    Args:
        input_tpr_path (str): Path to the input portable run input TPR file.
        output_gro_path (str): Path to the input structure GRO file.
        input_top_tar_path (str): Path the input TOP topology in TAR format.
        output_top_tar_path (str): Path the output topology TOP and ITP files
                                   tarball.
        properties (dic):
            output_top_path (str): Path the output topology TOP file.
            replaced_group (str): Group of molecules that will be replaced by the
                                solvent.
            neutral (bool): Neutralize the charge of the system.
            concentration (float): Concentration of the ions in (mol/liter).
            seed (int): Seed for random number generator.
            gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, input_tpr_path, output_gro_path, input_top_tar_path,
                 output_top_tar_path, properties, **kwargs):
        if isinstance(properties, basestring):
            properties=json.loads(properties)
        self.input_tpr_path = input_tpr_path
        self.output_gro_path = output_gro_path
        self.input_top_tar_path = input_top_tar_path
        self.output_top_tar_path = output_top_tar_path
        self.output_top_path = properties.get('output_top_path','gio.top')
        self.replaced_group = properties.get('replaced_group','SOL')
        self.neutral = properties.get('neutral',False)
        self.concentration = properties.get('concentration',0.05)
        self.seed = properties.get('seed',1993)
        self.gmx_path = properties.get('gmx_path',None)
        self.mutation = properties.get('mutation',None)
        self.step = properties.get('step',None)
        self.path = properties.get('path','')
        
    def launch(self):
        """Launches the execution of the GROMACS genion module.
        """
        out_log, err_log = fu.get_logs(path=self.path, mutation=self.mutation, step=self.step)
        self.output_top_path = self.output_top_path if self.step is None else self.step+'_'+self.output_top_path
        self.output_top_path = self.output_top_path if self.mutation is None else self.mutation+'_'+self.output_top_path
        # Untar topology to topology_out
        fu.untar_top(tar_file=self.input_top_tar_path, top_file=self.output_top_path)
        gmx = 'gmx' if self.gmx_path is None else self.gmx_path
        cmd = ['echo', self.replaced_group, '|', gmx, 'genion',
               '-s', self.input_tpr_path,
               '-o', self.output_gro_path,
               '-p', self.output_top_path]

        if self.neutral:
            cmd.append('-neutral')
        elif self.concentration:
            cmd.append('-conc')
            cmd.append(str(self.concentration))

        if self.seed is not None:
            cmd.append('-seed')
            cmd.append(str(self.seed))

        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        command.launch()

        # Tar new_topology
        fu.tar_top(self.output_top_path, self.output_top_tar_path)

#Creating a main function to be compatible with CWL
def main():
    step=sys.argv[5]
    prop=sys.argv[6]
    step, system = step.split(':')
    prop = settings.YamlReader(prop, system).get_prop_dic()[step]
    prop['path']=''
    Genion(input_tpr_path = sys.argv[1],
           output_gro_path = sys.argv[2],
           input_top_tar_path = sys.argv[3],
           output_top_tar_path = sys.argv[4],
           step=step,
           properties=prop).launch()

if __name__ == '__main__':
    main()
