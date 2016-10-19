"""Python wrapper for the GROMACS genion module
"""
import shutil
import tempfile
import os
import random

try:
    import tools.file_utils as fu
    from command_wrapper import cmd_wrapper
    from pycompss.api.task import task
    from pycompss.api.parameter import *
    from pycompss.api.constraint import constraint
except ImportError:
    from pymdsetup.tools import file_utils as fu
    from pymdsetup.command_wrapper import cmd_wrapper
    from pymdsetup.dummies_pycompss.task import task
    from pymdsetup.dummies_pycompss.constraint import constraint
    from pymdsetup.dummies_pycompss.parameter import *


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


@task(tpr_path=FILE_IN, output_gro_path=FILE_OUT, input_top=FILE_IN,
      output_top=FILE_OUT, itp_path=IN, curr_path=IN, replaced_group=IN,
      neutral=IN, concentration=IN, seed=IN, log_path=FILE_OUT,
      error_path=FILE_OUT, gmx_path=IN)
def genionPyCOMPSs(tpr_path, output_gro_path, input_top, output_top, itp_path,
                   curr_path, replaced_group="SOL", neutral=False,
                   concentration=0.05, seed='None', log_path='None',
                   error_path='None', gmx_path='None'):
    """Launches the GROMACS genion module using the PyCOMPSs library.
    """
    fu.copy_ext(itp_path, curr_path, 'itp')
    shutil.copy(input_top, output_top)
    tempdir = tempfile.mkdtemp()
    temptop = os.path.join(tempdir, "gio.top")
    shutil.copy(output_top, temptop)

    inputtpr = "input" + str(random.randint(0,1000000)) +".tpr"
    os.symlink(tpr_path, inputtpr)

    outputgro = "output" + str(random.randint(0,1000000)) +".gro"
    os.symlink(output_gro_path, outputgro)

    gmx = "gmx" if gmx_path == 'None' else gmx_path
    cmd = ["echo", replaced_group, "|", gmx, "genion", "-s",
           inputtpr, "-o", outputgro,
           "-p", temptop]

    if neutral:
        cmd.append('-neutral')
    elif concentration:
        cmd.append('-conc')
        cmd.append(str(concentration))

    if seed != 'None':
        cmd.append('-seed')
        cmd.append(str(seed))

    command = cmd_wrapper.CmdWrapper(cmd, log_path, error_path)
    command.launch()
    shutil.copy(temptop, output_top)
    shutil.rmtree(tempdir)
    os.remove(inputtpr)
    os.remove(outputgro)
