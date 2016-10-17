"""Python wrapper module for the GROMACS solvate module
"""
import shutil
import os
import tempfile

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
        #shutil.copy(self.toplogy_in, self.topology_out)
        os.system('cp ' + self.topology_in + ' ' + self.topology_out)
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


@task(solute_structure_gro_path=FILE_IN, output_gro_path=FILE_OUT,
      input_top_path=FILE_IN, output_top_path=FILE_OUT,
      solvent_structure_gro_path=IN, log_path=FILE_OUT, error_path=FILE_OUT,
      gmx_path=IN)
def launchPyCOMPSs(solute_structure_gro_path, output_gro_path, input_top_path,
                   output_top_path, solvent_structure_gro_path="spc216.gro",
                   log_path='None', error_path='None', gmx_path='None'):
    """Launches the GROMACS solvate module using the PyCOMPSs library.

    Args:
        top (str): Path to the TOP file output from the PyCOMPSs
                   execution of pdb2gmx.
        gro (str): Path to the GRO file output from the PyCOMPSs
                   execution of pdb2gmx.
        topin (str): Path the input GROMACS TOP file.
        topout (str): Path the output GROMACS TOP file.
    """
    #os.symlink(solute_structure_gro_path, "solutestructure.gro")
    #os.symlink(output_gro_path, "output.gro")

    #tempdir = tempfile.mkdtemp()
    #temptop = os.path.join(tempdir, "sol.top")
    #temptop2 = os.path.join(tempdir, "sol2.top")
    #shutil.copy(input_top_path, temptop)
    temptop="/home/compss/pymdsetup/topology.top"
    temptop2="/home/compss/pymdsetup/topology2.top"
    #shutil.copy(input_top_path, temptop)
    os.system('cp ' + input_top_path + ' ' + temptop)
    sol_path = "/home/compss/pymdsetup/solute.gro"
    os.system('cp ' + solute_structure_gro_path + ' ' + sol_path)

    print "Input.top : ",input_top_path
    print "Output.top: ",output_top_path

    sol = Solvate512(sol_path, "/home/compss/pymdsetup/output.gro",
                     temptop, temptop2,
                     solvent_structure_gro_path="spc216.gro", log_path='None',
                     error_path='None', gmx_path='None')

    #sol.launch()

    gmx = "/usr/local/gromacs/bin/gmx"
    cmd = [gmx, "solvate", "-cp", sol_path,
           "-cs", "spc216.gro", "-o",
           "/home/compss/pymdsetup/output.gro", "-p", temptop]
    command = cmd_wrapper.CmdWrapper(cmd, "/home/compss/pymdsetup/sol.log", "/home/compss/pymdsetup/sol.err")
    command.launch()

    shutil.copy(temptop, output_top_path)
    #shutil.rmtree(tempdir)

    #os.remove("solutestructure.gro")
    #os.remove("output.gro")
