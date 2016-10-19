"""Python wrapper for the GROMACS mdrun module
"""
import os
import os.path as op
import random

try:
    from command_wrapper import cmd_wrapper
    from pycompss.api.task import task
    from pycompss.api.parameter import *
    from pycompss.api.constraint import constraint
except ImportError:
    from pymdsetup.command_wrapper import cmd_wrapper
    from pymdsetup.dummies_pycompss.task import task
    from pymdsetup.dummies_pycompss.constraint import constraint
    from pymdsetup.dummies_pycompss.parameter import *


class Mdrun512(object):
    """Wrapper for the 5.1.2 version of the mdrun module

    Args:
        tpr_path (str): Path to the portable binary run input file TPR.
        output_trr_path (str): Path to the GROMACS uncompressed raw trajectory file TRR.
        output_gro_path (str): Path to the output GROMACS structure GRO file.
        output_edr_path (str): Path to the output GROMACS portable energy file EDR.
        output_xtc_path (str): Path to the GROMACS compressed trajectory file XTC.
        output_cpt_path (str): Path to the output GROMACS checkpoint file CPT.
        log_path (str): Path to the file where the mdrun log will be stored.
        error_path (str): Path to the file where the mdrun error log will be stored.
        gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, tpr_path, output_trr_path, output_gro_path,
                 output_edr_path, output_xtc_path='None',
                 output_cpt_path='None', log_path='None',
                 error_path='None', gmx_path='None'):
        self.tpr_path = tpr_path
        self.output_gro_path = output_gro_path
        self.output_trr_path = output_trr_path
        self.output_edr_path = output_edr_path
        self.output_xtc_path = output_xtc_path
        self.output_cpt_path = output_cpt_path
        self.log_path = log_path
        self.error_path = error_path
        self.gmx_path = gmx_path

    def launch(self):
        """Launches the execution of the GROMACS mdrun module.
        """
        gmx = "gmx" if self.gmx_path == 'None' else self.gmx_path
        cmd = [gmx, "mdrun", "-s", self.tpr_path, "-o", self.output_trr_path]

        if not self.output_xtc_path == 'None':
            cmd.append("-x")
            cmd.append(self.output_xtc_path)
        if not self.output_cpt_path == 'None':
            cmd.append("-cpo")
            cmd.append(self.output_cpt_path)
        cmd.append("-c")
        cmd.append(self.output_gro_path)
        cmd.append("-e")
        cmd.append(self.output_edr_path)
        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()
        #command.move_file_output("md.log", op.dirname(self.output_trr_path))

@task(tpr_path=FILE_IN, output_trr_path=FILE_OUT, output_gro_path=FILE_OUT,
      output_edr_path=FILE_OUT, output_xtc_path=IN, output_cpt_path=IN,
      log_path=FILE_OUT, error_path=FILE_OUT, gmx_path=IN)
def mdrunPyCOMPSs(tpr_path, output_trr_path, output_gro_path, output_edr_path,
                   output_xtc_path, output_cpt_path,
                   log_path='None', error_path='None', gmx_path='None'):
    """Launches the GROMACS mdrun module using the PyCOMPSs library.
    Args:
        tpr (str): Path to the portable binary run input file TPR.
    """
    inputtpr = "input" + str(random.randint(0,1000000)) +".tpr"
    os.symlink(tpr_path, inputtpr)

    outputtrr = "output" + str(random.randint(0,1000000)) +".trr"
    os.symlink(output_trr_path, outputtrr)

    outputgro = "output" + str(random.randint(0,1000000)) +".gro"
    os.symlink(output_gro_path, outputgro)

    outputedr = "output" + str(random.randint(0,1000000)) +".edr"
    os.symlink(output_edr_path, outputedr)

    # outputxtc = "output" + str(random.randint(0,1000000)) +".xtc"
    # os.symlink(output_xtc_path, outputxtc)
    #
    # outputcpt = "output" + str(random.randint(0,1000000)) +".cpt"
    # os.symlink(output_cpt_path, outputcpt)

    mdr = Mdrun512(tpr_path=inputtpr,
                   output_trr_path=outputtrr,
                   output_gro_path=outputgro,
                   output_edr_path=outputedr,
                   output_xtc_path=output_xtc_path,
                   output_cpt_path=output_cpt_path,
                   log_path=log_path,
                   error_path=error_path,
                   gmx_path=gmx_path)
    mdr.launch()
