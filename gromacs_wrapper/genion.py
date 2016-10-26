"""Python wrapper for the GROMACS genion module
"""
import shutil
try:
    from command_wrapper import cmd_wrapper
except ImportError:
    from pymdsetup.command_wrapper import cmd_wrapper


class Genion512(object):
    """Wrapper for the 5.1.2 version of the genion module

    Args:
        tpr_path (str): Path to the input GROMACS portable run input TPR file.
        output_gro_path (str): Path to the input GROMACS structure GRO file.
        input_top (str): Path the input GROMACS topology TOP file.
        output_top (str): Path the output GROMACS topology TOP file.
        replaced_group (str): Group of molecules that will be replaced by the
                              solvent.
        neutral (bool): Neutralize the charge of the system.
        concentration (float): Concentration of the ions in (mol/liter).
        seed (int): Seed for random number generator.
        log_path (str): Path to the file where the genion log will be stored.
        error_path (str): Path to the file where the genion error log will be
                          stored.
        gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, tpr_path, output_gro_path, input_top, output_top,
                 replaced_group="SOL", neutral=False, concentration=0.05,
                 seed='None', log_path='None', error_path='None',
                 gmx_path='None'):
        self.tpr_path = tpr_path
        self.output_gro_path = output_gro_path
        self.input_top = input_top
        self.output_top = output_top
        self.replaced_group = replaced_group
        self.neutral = neutral
        self.concentration = concentration
        self.seed = seed
        self.log_path = log_path
        self.error_path = error_path
        self.gmx_path = gmx_path

    def launch(self):
        """Launches the execution of the GROMACS genion module.
        """
        shutil.copy(self.input_top, self.output_top)
        gmx = "gmx" if self.gmx_path == 'None' else self.gmx_path
        cmd = ["echo", self.replaced_group, "|", gmx, "genion", "-s",
               self.tpr_path, "-o", self.output_gro_path,
               "-p", self.output_top]

        if self.neutral:
            cmd.append('-neutral')
        elif self.concentration:
            cmd.append('-conc')
            cmd.append(str(self.concentration))

        if self.seed != 'None':
            cmd.append('-seed')
            cmd.append(str(self.seed))

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()
