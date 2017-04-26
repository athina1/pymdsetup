"""Python wrapper module for the GROMACS editconf module
"""
import sys
try:
    from command_wrapper import cmd_wrapper
    import configuration.settings as settings
except ImportError:
    from pymdsetup.command_wrapper import cmd_wrapper
    from pymdsetup.configuration import settings

class Editconf512(object):
    """Wrapper for the 5.1.2 version of the editconf module

    Args:
        input_gro_path (str): Path to the input GRO file.
        output_gro_path (str): Path to the output GRO file.
        distance_to_molecule (float): Distance of the box from the outermost
                                      atom in nm. ie 1.0nm = 10 Angstroms.
        box_type (str): Geometrical shape of the solvent box.
                        Available box types: octahedron, cubic, etc.
        center_molecule (bool): Center molecule in the box.
    """

    def __init__(self, input_gro_path, output_gro_path,
                 distance_to_molecule=1.0, box_type='octahedron',
                 center_molecule=True,
                 log_path=None, error_path=None, gmx_path=None):
        self.input_gro_path = input_gro_path
        self.output_gro_path = output_gro_path
        self.distance_to_molecule = distance_to_molecule
        self.box_type = box_type
        self.center_molecule = center_molecule
        self.log_path = log_path
        self.error_path = error_path
        self.gmx_path = gmx_path

    def launch(self):
        """Launches the execution of the GROMACS editconf module.
        """
        gmx = 'gmx' if self.gmx_path is None else self.gmx_path
        cmd = [gmx, 'editconf', '-f', self.input_gro_path,
               '-o', self.output_gro_path,
               '-d', str(self.distance_to_molecule),
               '-bt', self.box_type]
        if self.center_molecule:
            cmd.append('-c')

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()

#Creating a main function to be compatible with CWL
def main():
    Editconf512(input_gro_path=sys.argv[1],
                output_gro_path=sys.argv[2],
                box_type=sys.argv[3],
                distance_to_molecule=float(sys.argv[4]),
                center_molecule=settings.str2bool(sys.argv[5]),
                gmx_path=sys.argv[6],
                log_path=sys.argv[7],
                error_path=sys.argv[8]).launch()

if __name__ == '__main__':
    main()
