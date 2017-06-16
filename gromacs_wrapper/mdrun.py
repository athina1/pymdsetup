"""Python wrapper for the GROMACS mdrun module
"""
import sys
try:
    from command_wrapper import cmd_wrapper
except ImportError:
    from pymdsetup.command_wrapper import cmd_wrapper


class Mdrun512(object):
    """Wrapper for the 5.1.2 version of the mdrun module

    Args:
        input_tpr_path (str): Path to the portable binary run input file TPR.
        output_trr_path (str): Path to the GROMACS uncompressed raw trajectory file TRR.
        output_gro_path (str): Path to the output GROMACS structure GRO file.
        output_edr_path (str): Path to the output GROMACS portable energy file EDR.
        output_xtc_path (str): Path to the GROMACS compressed trajectory file XTC.
        output_cpt_path (str): Path to the output GROMACS checkpoint file CPT.
        log_path (str): Path to the file where the mdrun log will be stored.
        error_path (str): Path to the file where the mdrun error log will be stored.
        gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, input_tpr_path, output_trr_path, output_gro_path,
                 output_edr_path, output_xtc_path=None,
                 output_cpt_path=None, num_threads=None,
                 log_path=None, error_path=None, gmx_path=None, **kwargs):
        self.input_tpr_path = input_tpr_path
        self.output_gro_path = output_gro_path
        self.output_trr_path = output_trr_path
        self.output_edr_path = output_edr_path
        self.output_xtc_path = output_xtc_path
        self.output_cpt_path = output_cpt_path
        self.num_threads = num_threads
        self.log_path = log_path
        self.error_path = error_path
        self.gmx_path = gmx_path

    def launch(self):
        """Launches the execution of the GROMACS mdrun module.
        """
        gmx = 'gmx' if self.gmx_path is None else self.gmx_path
        cmd = [gmx, 'mdrun', '-s', self.input_tpr_path,
               '-o', self.output_trr_path]

        if not self.output_xtc_path is None:
            cmd.append('-x')
            cmd.append(self.output_xtc_path)
        if not self.output_cpt_path is None:
            cmd.append('-cpo')
            cmd.append(self.output_cpt_path)
        cmd += ['-c', self.output_gro_path, '-e', self.output_edr_path]

        #JUST FOR TESTING PURPOSES number of threads to run (0 is guess)
        if not self.num_threads is None:
            cmd.append('-nt')
            cmd.append(str(self.num_threads))

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()

#Creating a main function to be compatible with CWL
def main():
    Mdrun512(input_tpr_path = sys.argv[1],
              output_gro_path = sys.argv[2],
              output_trr_path = sys.argv[3],
              output_edr_path = sys.argv[4],
              output_xtc_path = sys.argv[5],
              output_cpt_path = sys.argv[6],
              gmx_path = sys.argv[7],
              log_path = sys.argv[8],
              error_path = sys.argv[9]).launch()

if __name__ == '__main__':
    main()
