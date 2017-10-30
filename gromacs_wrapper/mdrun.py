"""Python wrapper for the GROMACS mdrun module
"""
import os
import sys
import json
import configuration.settings as settings
from os.path import join as opj
from command_wrapper import cmd_wrapper
from tools import file_utils as fu

class Mdrun(object):
    """Wrapper for the 5.1.2 version of the mdrun module
    Args:
        input_tpr_path (str): Path to the portable binary run input file TPR.
        output_trr_path (str): Path to the GROMACS uncompressed raw trajectory file TRR.
        output_gro_path (str): Path to the output GROMACS structure GRO file.
        properties (dic):
            output_edr_path (str): Path to the output GROMACS portable energy file EDR.
            output_xtc_path (str): Path to the GROMACS compressed trajectory file XTC.
            num_threads (str): The number of threads that is going to be used.
            gmx_path (str): Path to the GROMACS executable binary.
        output_cpt_path (str): Path to the output GROMACS checkpoint file CPT.
    """

    def __init__(self, input_tpr_path, output_trr_path, output_gro_path,
                 properties, output_cpt_path=None, **kwargs):
        if isinstance(properties, basestring):
            properties=json.loads(properties)
        self.input_tpr_path = input_tpr_path
        self.output_trr_path = output_trr_path
        self.output_gro_path = output_gro_path
        self.output_cpt_path = output_cpt_path
        self.output_edr_path = properties.get('output_edr_path',None)
        self.output_xtc_path = properties.get('output_xtc_path',None)
        self.num_threads = properties.get('num_threads',None)
        self.ntmpi = properties.get('ntmpi', None)
        self.ntomp = properties.get('ntomp', None)
        self.gpu_id = properties.get('gpu_id', None)
        self.gmx_path = properties.get('gmx_path',None)
        self.mutation = properties.get('mutation',None)
        self.step = properties.get('step',None)
        self.path = properties.get('path','')
        self.mpirun = properties.get('mpirun', False)
        self.mpirun_np = properties.get('mpirun_np', None)

    def launch(self):
        """Launches the execution of the GROMACS mdrun module.
        """
        out_log, err_log = fu.get_logs(path=self.path, mutation=self.mutation, step=self.step)
        gmx = 'gmx' if self.gmx_path is None else self.gmx_path
        cmd = [gmx, 'mdrun', '-s', self.input_tpr_path,
               '-o', self.output_trr_path, '-c', self.output_gro_path,
               '-g', 'md.log']

        if self.mpirun_np is not None:
            cmd.insert(0, str(self.mpirun_np))
            cmd.insert(0, '-np')
        if self.mpirun:
            cmd.insert(0, 'mpirun')
        if not self.output_xtc_path is None:
            self.output_xtc_path = self.output_xtc_path if self.step is None else self.step+'_'+self.output_xtc_path
            self.output_xtc_path = self.output_xtc_path if self.mutation is None else self.mutation+'_'+self.output_xtc_path
            cmd.append('-x')
            cmd.append(self.output_xtc_path)
        if not self.output_edr_path is None:
            self.output_edr_path = self.output_edr_path if self.step is None else self.step+'_'+self.output_edr_path
            self.output_edr_path = self.output_edr_path if self.mutation is None else self.mutation+'_'+self.output_edr_path
            cmd.append('-e')
            cmd.append(self.output_edr_path)
        if not self.output_cpt_path is None:
            cmd.append('-cpo')
            cmd.append(self.output_cpt_path)
        #Number of threads to run (0 is guess)
        if not self.num_threads is None:
            cmd.append('-nt')
            cmd.append(str(self.num_threads))
        if not self.ntmpi is None:
            cmd.append('-ntmpi')
            cmd.append(str(self.ntmpi))
        if not self.ntomp is None:
            cmd.append('-ntomp')
            cmd.append(str(self.ntomp))
        if not self.gpu_id is None:
            cmd.append('-gpu_id')
            cmd.append(str(self.gpu_id))

        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        return command.launch()

#Creating a main function to be compatible with CWL
def main():
    if len(sys.argv) < 7:
        sys.argv.append(None)
    step=sys.argv[4]
    prop=sys.argv[5]
    step, system = step.split(':')
    prop = settings.YamlReader(prop, system).get_prop_dic()[step]
    prop['path']=''
    Mdrun(input_tpr_path = sys.argv[1],
          output_trr_path = sys.argv[2],
          output_gro_path = sys.argv[3],
          step=step,
          properties=prop,
          output_cpt_path = sys.argv[6]).launch()

if __name__ == '__main__':
    main()
