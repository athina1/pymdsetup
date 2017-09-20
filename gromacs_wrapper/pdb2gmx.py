"""Python wrapper module for the GROMACS pdb2gmx module
"""
import os
import sys
import json
import configuration.settings as settings
from command_wrapper import cmd_wrapper
from tools import file_utils as fu
from os.path import join as opj

class Pdb2gmx(object):
    """Wrapper class for the 5.1.2 version of the GROMACS pdb2gmx module.
    Args:
        input_structure_pdb_path (str): Path to the input PDB file.
        output_gro_path (str): Path to the output GRO file.
        output_top_tar_path (str): Path the output TOP topology in TAR format.
        properties (dic):
            output_top_path (str): Path the output TOP file.
            output_itp_path (str): Path the output itp file.
            water_type (str): Water molecule type.
                Valid values: tip3p, spce, etc.
            force_field (str): Force field to be used during the conversion.
                Valid values: amber99sb-ildn, oplsaa, etc.
            ignh (bool): Should pdb2gmx ignore the hidrogens in the original
                structure.
            gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, input_structure_pdb_path, output_gro_path,
                 output_top_tar_path, properties, **kwargs):
        if isinstance(properties, basestring):
            properties=json.loads(properties)
        self.input_structure_pdb_path = input_structure_pdb_path
        self.output_gro_path = output_gro_path
        self.output_top_tar_path = output_top_tar_path
        self.output_top_path = properties.get('output_top_path','p2g.top')
        self.output_itp_path = properties.get('output_itp_path',None)
        self.water_type = properties.get('water_type','spce')
        self.force_field = properties.get('force_field','amber99sb-ildn')
        self.ignh = properties.get('ignh',False)
        self.gmx_path = properties.get('gmx_path',None)
        self.mutation = properties.get('mutation','')
        self.path = properties.get('path','')

    def launch(self):
        """Launches the execution of the GROMACS pdb2gmx module.
        """
        out_log, err_log = settings.get_logs(self.path)
        gmx = "gmx" if self.gmx_path is None else self.gmx_path
        cmd = [gmx, "pdb2gmx", "-f", self.input_structure_pdb_path,
               "-o", self.output_gro_path, "-p", self.mutation+self.output_top_path,
               "-water", self.water_type, "-ff", self.force_field]

        if self.output_itp_path is not None:
            cmd.append("-i")
            cmd.append(self.mutation+self.output_itp_path)
        if self.ignh:
            cmd.append("-ignh")

        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        command.launch()

        #Remove comment (first line) from gro file
        with open(self.output_gro_path, 'r') as fin:
            data = fin.read().splitlines(True)
            data[0] = 'Created with pdb2gmx building block\n'
        with open(self.output_gro_path, 'w') as fout:
            fout.writelines(data)

        # Tar topology
        fu.tar_top(self.mutation+self.output_top_path, self.output_top_tar_path)

#Creating a main function to be compatible with CWL
def main():
    step=sys.argv[4]
    prop=sys.argv[5]
    step, system = step.split(':')
    prop = settings.YamlReader(prop, system).get_prop_dic()[step]
    prop['path']=''
    Pdb2gmx(input_structure_pdb_path=sys.argv[1],
            output_gro_path=sys.argv[2],
            output_top_tar_path=sys.argv[3],
            step=step,
            properties=prop).launch()

if __name__ == '__main__':
    main()
