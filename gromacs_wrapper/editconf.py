"""Python wrapper module for the GROMACS editconf module
"""
import sys
import json
from command_wrapper import cmd_wrapper
import configuration.settings as settings

class Editconf(object):
    """Wrapper for the 5.1.2 version of the editconf module
    Args:
        input_gro_path (str): Path to the input GRO file.
        output_gro_path (str): Path to the output GRO file.
        properties (dic):
            distance_to_molecule (float): Distance of the box from the outermost
                                          atom in nm. ie 1.0nm = 10 Angstroms.
            box_type (str): Geometrical shape of the solvent box.
                            Available box types: octahedron, cubic, etc.
            center_molecule (bool): Center molecule in the box.
    """

    def __init__(self, input_gro_path, output_gro_path, properties, **kwargs):
        if isinstance(properties, basestring):
            properties=json.loads(properties)
        self.input_gro_path = input_gro_path
        self.output_gro_path = output_gro_path
        self.distance_to_molecule = properties['distance_to_molecule']
        self.box_type = properties['box_type']
        self.center_molecule = properties['center_molecule']
        self.gmx_path = properties['gmx_path']
        self.path = properties.get('path','')

    def launch(self):
        """Launches the execution of the GROMACS editconf module.
        """
        out_log, err_log = settings.get_logs(self.path)
        gmx = 'gmx' if self.gmx_path is None else self.gmx_path
        cmd = [gmx, 'editconf', '-f', self.input_gro_path,
               '-o', self.output_gro_path,
               '-d', str(self.distance_to_molecule),
               '-bt', self.box_type]
        if self.center_molecule:
            cmd.append('-c')

        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        command.launch()

#Creating a main function to be compatible with CWL
def main():
    Editconf(input_gro_path=sys.argv[1],
            output_gro_path=sys.argv[2],
            properties=sys.argv[3]).launch()

if __name__ == '__main__':
    main()
