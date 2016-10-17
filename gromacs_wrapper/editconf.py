"""Python wrapper module for the GROMACS editconf module
"""
import os
try:
    import tools.file_utils as fu
    from command_wrapper import cmd_wrapper
    from pycompss.api.task import task
    from pycompss.api.parameter import *
    from pycompss.api.task import task
    from pycompss.api.constraint import constraint
except ImportError:
    from pymdsetup.tools import file_utils as fu
    from pymdsetup.command_wrapper import cmd_wrapper
    from pymdsetup.dummies_pycompss.task import task
    from pymdsetup.dummies_pycompss.constraint import constraint
    from pymdsetup.dummies_pycompss.parameter import *


class Editconf512(object):
    """Wrapper for the 5.1.2 version of the editconf module

    Args:
        structure_gro_path (str): Path to the input GROMACS GRO file.
        output_gro_path (str): Path to the output GROMACS GRO file.
        distance_to_molecule (float): Distance of the box from the outermost
                                      atom in nm. ie 1.0nm = 10 Angstroms.
        box_type (str): Geometrical shape of the solvent box.
                        Available box types: octahedron, cubic, etc.
        center_molecule (bool): Center molecule in the box.
    """

    def __init__(self, structure_gro_path, output_gro_path,
                 distance_to_molecule=1.0, box_type='octahedron',
                 center_molecule=True, log_path='None', error_path='None',
                 gmx_path='None'):
        self.structure_gro_path = structure_gro_path
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
        gmx = "gmx" if self.gmx_path == 'None' else self.gmx_path
        cmd = [gmx, "editconf", "-f", self.structure_gro_path,
               "-o", self.output_gro_path, "-d",
               str(self.distance_to_molecule), "-bt", self.box_type]
        if self.center_molecule:
            cmd.append("-c")

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()


@task(structure_gro_path=FILE_IN, output_gro_path=FILE_OUT,
      distance_to_molecule=IN, box_type=IN, center_molecule=IN,
      log_path=FILE_OUT, error_path=FILE_OUT, gmx_path=IN)
def launchPyCOMPSs(structure_gro_path, output_gro_path,
                   distance_to_molecule=1.0, box_type='octahedron',
                   center_molecule=True, log_path='None', error_path='None',
                   gmx_path='None'):
    """Launches the GROMACS editconf module using the PyCOMPSs library.

    Args:
        gro_path (str): Path to the input GROMACS GRO structure.
    """
    os.symlink(structure_gro_path, "structure.gro")
    os.symlink(output_gro_path, "structureout.gro")
    ec = Editconf512("structure.gro", "structureout.gro", distance_to_molecule,
                     box_type, center_molecule, log_path, error_path, gmx_path)
    ec.launch()
    os.remove("structure.gro")
    os.remove("structureout.gro")
