"""Python wrapper for the GROMACS genion module
"""
import sys
try:
    from command_wrapper import cmd_wrapper
    from tools import file_utils as fu
except ImportError:
    from pymdsetup.command_wrapper import cmd_wrapper
    from pymdsetup.tools import file_utils as fu


class Genion512(object):
    """Wrapper for the 5.1.2 version of the genion module

    Args:
        input_tpr_path (str): Path to the input portable run input TPR file.
        output_gro_path (str): Path to the input structure GRO file.
        input_top_tar_path (str): Path the input TOP topology in TAR format.
        output_top_path (str): Path the output topology TOP file.
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

    def __init__(self, input_tpr_path, output_gro_path, input_top_tar_path,
                 output_top_path, output_top_tar_path, replaced_group='SOL',
                 neutral=False, concentration=0.05, seed=None,
                 log_path=None, error_path=None, gmx_path=None, **kwargs):
        self.input_tpr_path = input_tpr_path
        self.output_gro_path = output_gro_path
        self.input_top_tar_path = input_top_tar_path
        self.output_top_path = output_top_path
        self.output_top_tar_path = output_top_tar_path
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
        # Untar topology to topology_out
        fu.untar_top(self.input_top_tar_path, top_file=self.output_top_path)

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

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()

        # Tar new_topology
        fu.tar_top(self.output_top_path, self.output_top_tar_path)

#Creating a main function to be compatible with CWL
def main():
    if len(sys.argv) < 13:
        sys.argv.append(None)
    Genion512(input_tpr_path = sys.argv[1],
              output_gro_path = sys.argv[2],
              input_top_tar_path = sys.argv[3],
              output_top_path = sys.argv[4],
              output_top_tar_path = sys.argv[5],
              replaced_group = sys.argv[6],
              neutral = sys.argv[7],
              concentration = sys.argv[8],
              gmx_path = sys.argv[9],
              log_path = sys.argv[10],
              error_path = sys.argv[11],
              seed = sys.argv[12]).launch()

if __name__ == '__main__':
    main()
