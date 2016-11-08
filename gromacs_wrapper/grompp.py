"""Python wrapper for the GROMACS grompp module
"""
try:
    from command_wrapper import cmd_wrapper
    from tools import file_utils as fu
except ImportError:
    from pymdsetup.command_wrapper import cmd_wrapper
    from pymdsetup.tools import file_utils as fu


class Grompp512(object):
    """Wrapper for the 5.1.2 version of the GROMACS grompp module.
    The GROMACS preprocessor module needs to be feeded with the input system
    and the molecular dynamics parameter file MDP, to create a portable binary
    run input file TPR.

    Args:
        mdp_path (str): Path to the input GROMACS parameter input file MDP.
        gro_path (str): Path to the input GROMACS structure GRO file.
        top_path (str): Path the input GROMACS topology TOP file.
        output_tpr_path (str): Path to the output portable binary run file TPR.
        cpt_path (str): Path to the input GROMACS checkpoint file CPT.
        log_path (str): Path to the file where the grompp log will be stored.
        error_path (str): Path to the file where the grompp error log will be
                          stored.
        gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, input_mdp_path, input_gro_path, input_top_tar_path,
                 output_tpr_path, input_cpt_path=None,
                 log_path=None, error_path=None, gmx_path=None):
        self.input_mdp_path = input_mdp_path
        self.input_gro_path = input_gro_path
        self.input_top_tar_path = input_top_tar_path
        self.output_tpr_path = output_tpr_path
        self.input_cpt_path = input_cpt_path
        self.log_path = log_path
        self.error_path = error_path
        self.gmx_path = gmx_path

    def launch(self):
        """Launches the execution of the GROMACS grompp module.
        """
        # Untar topology in de directory of the output_tpr_path and get the
        # topology path
        topology_path = fu.untar_top(self.input_top_tar_path, dest_dir=self.output_tpr_path)

        gmx = 'gmx' if self.gmx_path is None else self.gmx_path
        cmd = [gmx, 'grompp', '-f', self.input_mdp_path,
               '-c', self.input_gro_path,
               '-p', topology_path,
               '-o', self.output_tpr_path]
        if self.input_cpt_path is not None:
            cmd.append('-t')
            cmd.append(self.input_cpt_path)

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()
