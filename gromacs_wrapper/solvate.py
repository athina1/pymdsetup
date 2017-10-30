"""Python wrapper module for the GROMACS solvate module
"""
import os
import sys
import json
import configuration.settings as settings
from command_wrapper import cmd_wrapper
from tools import file_utils as fu
from os.path import join as opj
from tools import file_utils as fu

class Solvate(object):
    """Wrapper for the 5.1.2 version of the GROMACS solvate module
    Args:
        input_solute_gro_path (str): Path to the input GRO file.
        output_gro_path (str): Path to the output GRO file.
        input_top_zip_path (str): Path the input TOP topology in zip format.
        output_top_zip_path (str): Path the output topology in zip format.
        properties (dic):
            output_top_path (str): Path the output TOP file.
            intput_solvent_gro_path (str): Path to the GRO file contanining the
                                           structure of the solvent.
            gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, input_solute_gro_path, output_gro_path,
                 input_top_zip_path, output_top_zip_path, properties, **kwargs):
        if isinstance(properties, basestring):
            properties=json.loads(properties)
        self.input_solute_gro_path = input_solute_gro_path
        self.output_gro_path = output_gro_path
        self.input_top_zip_path = input_top_zip_path
        self.output_top_zip_path = output_top_zip_path
        self.output_top_path = properties.get('output_top_path','sol.top')
        self.input_solvent_gro_path = properties.get('input_solvent_gro_path','spc216.gro')
        self.gmx_path = properties.get('gmx_path',None)
        self.mutation = properties.get('mutation',None)
        self.step = properties.get('step',None)
        self.path = properties.get('path','')
        self.mpirun = properties.get('mpirun', False)
        self.mpirun_np = properties.get('mpirun_np', None)

    def launch(self):
        """Launches the execution of the GROMACS solvate module.
        """
        out_log, err_log = fu.get_logs(path=self.path, mutation=self.mutation, step=self.step)
        self.output_top_path = self.output_top_path if self.step is None else self.step+'_'+self.output_top_path
        self.output_top_path = self.output_top_path if self.mutation is None else self.mutation+'_'+self.output_top_path
        # Unzip topology to topology_out
        fu.unzip_top(zip_file=self.input_top_zip_path, top_file=self.output_top_path)

        gmx = 'gmx' if self.gmx_path is None else self.gmx_path
        cmd = [gmx, 'solvate',
               '-cp', self.input_solute_gro_path,
               '-cs', self.input_solvent_gro_path,
               '-o',  self.output_gro_path,
               '-p',  self.output_top_path]

        if self.mpirun_np is not None:
            cmd.insert(0, str(self.mpirun_np))
            cmd.insert(0, '-np')
        if self.mpirun:
            cmd.insert(0, 'mpirun')
        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        returncode = command.launch()

        with open(self.output_top_path) as topology_file:
            out_log.info('Last 5 lines of new top file: ')
            lines = topology_file.readlines()
            for index in [-i for i in range(5,0,-1)]:
                out_log.info(lines[index])


        # zip new_topology
        fu.zip_top(self.output_top_path, self.output_top_zip_path)
        return returncode

#Creating a main function to be compatible with CWL
def main():
    step=sys.argv[5]
    prop=sys.argv[6]
    step, system = step.split(':')
    prop = settings.YamlReader(prop, system).get_prop_dic()[step]
    prop['path']=''
    Solvate(input_solute_gro_path=sys.argv[1],
            output_gro_path=sys.argv[2],
            input_top_zip_path=sys.argv[3],
            output_top_zip_path=sys.argv[4],
            step=step,
            properties=prop).launch()

if __name__ == '__main__':
    main()
