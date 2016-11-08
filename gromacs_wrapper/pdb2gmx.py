"""Python wrapper module for the GROMACS pdb2gmx module
"""
try:
    from command_wrapper import cmd_wrapper
    from tools import file_utils as fu
except ImportError:
    from pymdsetup.command_wrapper import cmd_wrapper
    from pymdsetup.tools import file_utils as fu


class Pdb2gmx512(object):
    """Wrapper class for the 5.1.2 version of the GROMACS pdb2gmx module

    Args:
        structure_pdb_path (str): Path to the input PDB file.
        output_gro_path (str): Path to the output GRO file.
        output_top_path (str): Path the output TOP file.
        output_top_tar_path (str): Path the output TOP topology in TAR format.
        water_type (str): Water molecule type.
            Valid values: tip3p, spce, etc.
        force_field (str): Force field to be used during the conversion.
            Valid values: amber99sb-ildn, oplsaa, etc.
        ignh (bool): Should pdb2gmx ignore the hidrogens in the original
            structure.
        log_path (str): Path to the file where the pdb2gmx log will be stored.
        error_path (str): Path to the file where the pdb2gmx error log will be
                          stored.
        gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, structure_pdb_path, output_gro_path, output_top_path,
                 output_top_tar_path, water_type='tip3p',
                 force_field='amber99sb-ildn', ignh=False,
                 log_path=None, error_path=None, gmx_path=None):
        self.structure_pdb_path = structure_pdb_path
        self.output_gro_path = output_gro_path
        self.output_top_path = output_top_path
        self.output_top_tar_path = output_top_tar_path
        self.water_type = water_type
        self.force_field = force_field
        self.ignh = ignh
        self.log_path = log_path
        self.error_path = error_path
        self.gmx_path = gmx_path

    def launch(self):
        """Launches the execution of the GROMACS pdb2gmx module.
        """

        gmx = "gmx" if self.gmx_path is None else self.gmx_path
        cmd = [gmx, "pdb2gmx", "-f", self.structure_pdb_path,
               "-o", self.output_gro_path, "-p", self.output_top_path,
               "-water", self.water_type, "-ff", self.force_field]

        if self.ignh:
            cmd.append("-ignh")

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()

        # Tar topology
        fu.tar_top(self.output_top_path, self.output_top_tar_path)
