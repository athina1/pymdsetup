"""Python wrapper module for the GROMACS solvate module
"""

try:
    from command_wrapper import cmd_wrapper
    from tools import file_utils as fu
except ImportError:
    from pymdsetup.command_wrapper import cmd_wrapper
    from pymdsetup.tools import file_utils as fu


class Solvate512(object):
    """Wrapper for the 5.1.2 version of the GROMACS solvate module

    Args:
        input_solute_gro_path (str): Path to the input GRO file.
        output_gro_path (str): Path to the output GRO file.
        input_top_tar_path (str): Path the input TOP topology in TAR format.
        output_top_path (str): Path the output TOP file.
        output_top_tar_path (str): Path the output topology in TAR format.
        intput_solvent_gro_path (str): Path to the GRO file contanining the
                                       structure of the solvent.
        log_path (str): Path to the file where the solvate log will be stored.
        error_path (str): Path to the file where the solvate error log will be
                          stored.
        gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, input_solute_gro_path, output_gro_path,
                 input_top_tar_path, output_top_path, output_top_tar_path,
                 input_solvent_gro_path='spc216.gro',
                 log_path=None, error_path=None, gmx_path=None):
        self.input_solute_gro_path = input_solute_gro_path
        self.output_gro_path = output_gro_path
        self.input_top_tar_path = input_top_tar_path
        self.output_top_path = output_top_path
        self.output_top_tar_path = output_top_tar_path
        self.input_solvent_gro_path = input_solvent_gro_path
        self.log_path = log_path
        self.error_path = error_path
        self.gmx_path = gmx_path

    def launch(self):
        """Launches the execution of the GROMACS solvate module.
        """
        # Untar topology to topology_out
        fu.untar_top(self.input_top_tar_path, top_file=self.output_top_path)

        gmx = 'gmx' if self.gmx_path is None else self.gmx_path
        cmd = [gmx, 'solvate', '-cp', self.input_solute_gro_path,
               '-cs', self.input_solvent_gro_path,
               '-o',  self.output_gro_path,
               '-p', self.output_top_path]

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()

        # Tar new_topology
        fu.tar_top(self.output_top_path, self.output_top_tar_path)

        # Remove temp files
        fu.rm_hash_bakup()

#Creating a main function to be compatible with CWL
def main():
    Solvate512(input_solute_gro_path=sys.argv[1],
                output_gro_path=sys.argv[2],
                input_top_tar_path=sys.argv[3],
                output_top_path=sys.argv[4],
                output_top_tar_path=sys.argv[5],
                input_solvent_gro_path=sys.argv[6],
                gmx_path=sys.argv[7],
                log_path=sys.argv[8],
                error_path=sys.argv[9]).launch()

if __name__ == '__main__':
    main()
