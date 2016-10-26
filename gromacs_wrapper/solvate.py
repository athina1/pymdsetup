"""Python wrapper module for the GROMACS solvate module
"""
import shutil
import os
try:
    from command_wrapper import cmd_wrapper
except ImportError:
    from pymdsetup.command_wrapper import cmd_wrapper


class Solvate512(object):
    """Wrapper for the 5.1.2 version of the GROMACS solvate module

    Args:
        solute_structure_gro_path (str): Path to the input GROMACS GRO file.
        output_gro_path (str): Path to the output GROMACS GRO file.
        input_top_path (str): Path the input GROMACS TOP file.
        output_top_path (str): Path the output GROMACS TOP file.
        solvent_structure_gro_path (str): Path to the GRO file contanining the
                                          structure of the solvent.
        log_path (str): Path to the file where the solvate log will be stored.
        error_path (str): Path to the file where the solvate error log will be
                          stored.
        gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, solute_structure_gro_path, output_gro_path,
                 input_top_path, output_top_path,
                 solvent_structure_gro_path="spc216.gro",
                 log_path='None', error_path='None', gmx_path='None'):
        self.solute_structure_gro_path = solute_structure_gro_path
        self.output_gro_path = output_gro_path
        self.solvent_structure_gro_path = solvent_structure_gro_path
        self.topology_in = input_top_path
        self.topology_out = output_top_path
        self.log_path = log_path
        self.error_path = error_path
        self.gmx_path = gmx_path

    def launch(self):
        """Launches the execution of the GROMACS solvate module.
        """
        shutil.copy(self.topology_in, self.topology_out)
        gmx = "gmx" if self.gmx_path == 'None' else self.gmx_path
        cmd = [gmx, "solvate", "-cp", self.solute_structure_gro_path,
               "-cs", self.solvent_structure_gro_path, "-o",
               self.output_gro_path, "-p", self.topology_out]

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()
        # Remove temp files
        filelist = [f for f in os.listdir(".") if f.startswith("#temp.") and
                    f.endswith("#")]

        for f in filelist:
            os.remove(f)
