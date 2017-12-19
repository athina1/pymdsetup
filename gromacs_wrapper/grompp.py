#!/usr/bin/env python

"""Python wrapper for the GROMACS grompp module
"""
import sys
import json
from os.path import join as opj
import configuration.settings as settings
from command_wrapper import cmd_wrapper
from tools import file_utils as fu

class Grompp(object):
    """Wrapper for the 5.1.2 version of the GROMACS grompp module.
    The GROMACS preprocessor module needs to be feeded with the input system
    and the molecular dynamics parameter file MDP, to create a portable binary
    run input file TPR.
    Args:
        input_gro_path (str): Path to the input GROMACS structure GRO file.
        input_top_zip_path (str): Path the input GROMACS topology TOP file.
        output_tpr_path (str): Path to the output portable binary run file TPR.
        input_cpt_path (str): Path to the input GROMACS checkpoint file CPT.
        input_mdp_path (str): Path to the input GROMACS parameter input file MDP.
        properties (dic):
            gmx_path (str): Path to the GROMACS executable binary.
    """

    def __init__(self, input_gro_path, input_top_zip_path,
                 output_tpr_path, properties, input_cpt_path=None, **kwargs):
        if isinstance(properties, basestring):
            properties=json.loads(properties)
        self.input_gro_path = input_gro_path
        self.input_top_zip_path = input_top_zip_path
        self.output_tpr_path = output_tpr_path
        self.input_cpt_path = input_cpt_path
        self.input_mdp_path= properties.get('input_mdp_path', None)
        self.output_mdp_path= properties.get('output_mdp_path', None)
        self.gmx_path = properties.get('gmx_path', None)
        self.mutation = properties.get('mutation',None)
        self.step = properties.get('step',None)
        self.path = properties.get('path','')
        self.mpirun = properties.get('mpirun', False)
        self.mpirun_np = properties.get('mpirun_np', None)
        self.mdp = properties.get('mdp', None)

    def create_mdp(self):
        """Creates an MDP file using the properties file settings
        """
        mdp_file_path=fu.create_path(self.path, '.mdp', self.mutation, self.step)
        header="; This mdp file has been created by the pymdsetup.gromacs_wrapper.grompp.create_mdp()"

        # Position restrain
        if md:
            if nvt or npt:
                self.mdp['define'] =  self.mdp.get('define', '-DPOSRES')

        # Run parameters
        self.mdp['nsteps'] =  self.mdp.get('nsteps', '5000')
        if minimization:
            self.mdp['integrator'] =  self.mdp.get('integrator', 'steep')
            self.mdp['emtol'] =  self.mdp.get('emtol', '1000.0')
            self.mdp['emstep'] =  self.mdp.get('emstep', '0.01')
        if md:
            self.mdp['integrator'] =  self.mdp.get('integrator', 'md')
            self.mdp['dt'] =  self.mdp.get('dt', '0.002')

        # Output control
        if md:
            if nvt or npt:
                self.mdp['nstxout']   =  self.mdp.get('nstxout',   '500')
                self.mdp['nstvout']   =  self.mdp.get('nstvout',   '500')
                self.mdp['nstenergy'] =  self.mdp.get('nstenergy', '500')
                self.mdp['nstlog']    =  self.mdp.get('nstlog',    '500')
            if free:
                self.mdp['nstxout']   =  self.mdp.get('nstxout',   '5000')
                self.mdp['nstvout']   =  self.mdp.get('nstvout',   '5000')
                self.mdp['nstenergy'] =  self.mdp.get('nstenergy', '5000')
                self.mdp['nstlog']    =  self.mdp.get('nstlog',    '5000')
                self.mdp['nstxout-compressed'] = self.mdp.get('nstxout-compressed', '5000')
                self.mdp['compressed-x-grps']    =  self.mdp.get('compressed-x-grps', 'System')

        # Bond parameters
        if md:
            self.mdp['constraint_algorithm']   =  self.mdp.get('constraint_algorithm', 'lincs')
            self.mdp['constraints']            =  self.mdp.get('constraints',          'all-bonds')
            self.mdp['lincs_iter']             =  self.mdp.get('lincs_iter',           '1')
            self.mdp['lincs_order']            =  self.mdp.get('lincs_order',          '4')
            if nvt:
                self.mdp['continuation']           =  self.mdp.get('continuation',     'no')
            if npt or free:
                self.mdp['continuation']           =  self.mdp.get('continuation',      'yes')


        # Neighbour searching
        self.mdp['cutoff-scheme'] =  self.mdp.get('cutoff-scheme', 'Verlet')
        self.mdp['ns_type'] =  self.mdp.get('ns_type', 'grid')
        self.mdp['rcoulomb'] =  self.mdp.get('rcoulomb', '1.0')
        self.mdp['rvdw'] =  self.mdp.get('rvdw', '1.0')
        if minimization:
            self.mdp['nstlist'] =  self.mdp.get('nstlist', '1')
        if md:
            self.mdp['nstlist'] =  self.mdp.get('nstlist', '10')

        # Eletrostatics
        self.mdp['coulombtype'] =  self.mdp.get('coulombtype', 'PME')
        if md:
            self.mdp['pme_order'] =  self.mdp.get('pme_order', '4')
            self.mdp['fourierspacing'] =  self.mdp.get('fourierspacing', '0.16')

        # Temperature coupling
        if md:
            self.mdp['tcoupl']  =  self.mdp.get('tcoupl', 'V-rescale')
            self.mdp['tc-grps'] =  self.mdp.get('tc-grps', 'Protein Non-Protein')
            self.mdp['tau_t']   =  self.mdp.get('tau_t', '0.1	  0.1')
            self.mdp['ref_t']   =  self.mdp.get('ref_t', '300 	  300')

        # Pressure coupling
        if md:
            if nvt:
                self.mdp['pcoupl']   =  self.mdp.get('pcoupl', 'no')
            if npt or free:
                self.mdp['pcoupl']   =  self.mdp.get('pcoupl', 'Parrinello-Rahman')
                self.mdp['pcoupltype']   =  self.mdp.get('pcoupltype', 'isotropic')
                self.mdp['tau_p']   =  self.mdp.get('tau_p', '2.0')
                self.mdp['ref_p']   =  self.mdp.get('ref_p', '1.0')
                self.mdp['compressibility']   =  self.mdp.get('compressibility', '4.5e-5')
                if npt:
                    self.mdp['refcoord_scaling']   =  self.mdp.get('refcoord_scaling', 'com')

        # Dispersion correction
        if md:
            self.mdp['DispCorr']   =  self.mdp.get('DispCorr', 'EnerPres')

        # Velocity generation
        if md:
            if nvt:
                self.mdp['gen_vel']    =  self.mdp.get('gen_vel',   'yes')
                self.mdp['gen_temp']   =  self.mdp.get('gen_temp', '300')
                self.mdp['gen_seed']   =  self.mdp.get('gen_seed', '-1')
            if npt or free:
                self.mdp['gen_vel']   =  self.mdp.get('gen_vel',   'no')

        #Periodic boundary conditions
        self.mdp['pbc'] =  self.mdp.get('pbc', 'xyz')

        with open(mdp_file_path, 'w') as mdp:
            mdp.write(header + '\n')
            for key, value in self.mdp.iteritems():
                mdp.write(key + ' = ' + str(value) + '\n')

        return mdp_file_path

    def launch(self):
        """Launches the execution of the GROMACS grompp module.
        """
        out_log, err_log = fu.get_logs(path=self.path, mutation=self.mutation, step=self.step)

        mdp_file_path = self.create_mdp() if self.input_mdp_path is None else self.input_mdp_path
        # Unzip topology in de directory of the output_tpr_path and get the
        # topology path
        topology_path = fu.unzip_top(self.input_top_zip_path)
        gmx = 'gmx' if self.gmx_path is None else self.gmx_path
        cmd = [gmx, 'grompp', '-f', mdp_file_path,
               '-c', self.input_gro_path,
               '-p', topology_path,
               '-o', self.output_tpr_path]

        if self.mpirun_np is not None:
            cmd.insert(0, str(self.mpirun_np))
            cmd.insert(0, '-np')
        if self.mpirun:
            cmd.insert(0, 'mpirun')
        if self.input_cpt_path is not None:
            cmd.append('-t')
            cmd.append(self.input_cpt_path)
        if self.output_mdp_path is not None:
            cmd.append('-po')
            cmd.append(self.output_mdp_path)

        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        return command.launch()

#Creating a main function to be compatible with CWL
def main():
    if len(sys.argv) < 9:
        sys.argv.append(None)
    system=sys.argv[1]
    step=sys.argv[2]
    properties_file=sys.argv[3]
    prop = settings.YamlReader(properties_file, system).get_prop_dic()[step]
    Grompp(input_gro_path = sys.argv[4],
           input_top_zip_path = sys.argv[5],
           input_mdp_path = sys.argv[6],
           output_tpr_path = sys.argv[7],
           input_cpt_path = sys.argv[8],
           properties=prop).launch()

if __name__ == '__main__':
    main()
