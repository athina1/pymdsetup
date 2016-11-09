"""Python wrapper for the GROMACS rms module
"""

try:
    from command_wrapper import cmd_wrapper
except ImportError:
    from pymdsetup.command_wrapper import cmd_wrapper


class Rms512(object):
    """Wrapper for the 5.1.2 version of the rms module

    Args:
        input_ref_struct (str): Path to the original (before launching the trajectory) GROMACS structure file GRO.
        input_traj (str): Path to the GROMACS uncompressed raw trajectory file TRR.
        output_xvg (str): Path to the simple xmgrace plot file XVG.
        log_path (str): Path to the file where the rms log will be stored.
        error_path (str): Path to the file where the rms error log will be stored.
        gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, input_gro_path, input_trr_path, output_xvg_path,
                 log_path=None, error_path=None, gmx_path=None):
        self.input_gro_path = input_gro_path
        self.input_trr_path = input_trr_path
        self.output_xvg_path = output_xvg_path
        self.log_path = log_path
        self.error_path = error_path
        self.gmx_path = gmx_path

    def launch(self):
        """Launches the execution of the GROMACS rms module.
        """
        gmx = 'gmx' if self.gmx_path is 'None' else self.gmx_path
        cmd = ['echo', '0 0', '|', gmx, 'rms',
               '-s', self.input_gro_path,
               '-f', self.input_trr_path,
               '-o', self.output_xvg_path,
               '-xvg', 'none']

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()
