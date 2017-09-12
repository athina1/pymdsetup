"""
Gromacs full setup from a pdb

"""
import os
import sys
import time
import shutil
from os.path import join as opj

import tools.file_utils as fu
import configuration.settings as settings
import gromacs_wrapper.pdb2gmx as pdb2gmx
import gromacs_wrapper.grompp as grompp
import scwrl_wrapper.scwrl as scwrl
import gromacs_wrapper.solvate as solvate
import gromacs_wrapper.editconf as editconf
import gromacs_wrapper.genion as genion
import gromacs_wrapper.mdrun as mdrun
import mmb_api.pdb as pdb
import mmb_api.uniprot as uniprot
import gromacs_wrapper.rms as rms
import gnuplot_wrapper.gnuplot as gnuplot
from command_wrapper import cmd_wrapper
from pycompss.api.parameter import *
from pycompss.api.task import task
from pycompss.api.constraint import constraint

def main():
    from pycompss.api.api import barrier
    from pycompss.api.api import compss_wait_on
    start_time = time.time()
    yaml_path=sys.argv[1]
    system=sys.argv[2]
    conf = settings.YamlReader(yaml_path, system)
    workflow_path = conf.properties[system]['workflow_path']
    fu.create_dir(os.path.abspath(workflow_path))
    out_log, err_log = settings.get_logs(workflow_path, console=True)
    paths_glob = conf.get_paths_dic()
    prop_glob = conf.get_prop_dic()

    out_log.info('_______GROMACS FULL WORKFLOW_______')

    # If no PDB structure is provided the structure will be downloaded
    if ( conf.properties[system].get('initial_structure_pdb_path') is None or
         not os.path.isfile(conf.properties[system].get('initial_structure_pdb_path'))):
        out_log.info( 'step1:  mmbpdb -- Get PDB')
        out_log.info( '     Selected PDB code: ' + prop_glob['step1_mmbpdb']['pdb_code'])
        fu.create_dir(prop_glob['step1_mmbpdb']['path'])
        pdb.MmbPdb(prop_glob['step1_mmbpdb']['pdb_code'], paths_glob['step1_mmbpdb']['output_pdb_path']).get_pdb()
        initial_structure_pdb_path = paths_glob['step1_mmbpdb']['output_pdb_path']
    else:
        initial_structure_pdb_path = conf.properties[system].get('initial_structure_pdb_path')

    # If no mapped to pdb structure mutation list is provided the mutation list
    # will be downloaded from the MMB rest API
    if ( conf.properties.get('input_mapped_mutations_list') is None or
         len(conf.properties.get('input_mapped_mutations_list')) < 7 ):
        out_log.info( 'step2:  mmbuniprot -- Get mutations')
        mmbuniprot = uniprot.MmbVariants(prop_glob['step1_mmbpdb']['pdb_code'])
        mutations = mmbuniprot.get_pdb_variants()
        # This is part of the code prints some feedback to the user
        out_log.info( '     Uniprot code: ' + mmbuniprot.get_uniprot())
        if mutations is None or len(mutations) == 0:
            out_log.info( (prop_glob['step1_mmbpdb']['pdb_code'] + " " + mmbuniprot.get_uniprot() + ": No variants"))
            return
        else:
            out_log.info( ('     Found ' + str(len(mmbuniprot.get_variants())) + ' uniprot variants'))
            out_log.info( ('     Mapped to ' + str(len(mutations)) + ' ' + prop_glob['step1_mmbpdb']['pdb_code'] + ' PDB variants'))

    else:
        mutations = [m.strip() for m in conf.properties.get('input_mapped_mutations_list').split(',')]

    # Number of mutations to be modelled
    if ( conf.properties.get('mutations_limit') is None
         or int(conf.properties.get('mutations_limit')) == 0 ):
        mutations_limit = len(mutations)
    else:
        mutations_limit = min(len(mutations), int(prop['mutations_limit']))

    out_log.info('')
    out_log.info('Number of mutations to be modelled: ' + str(mutations_limit))

    rmsd_xvg_path_dict = {}
    mutations_counter = 0
    for mut in mutations:
        if mutations_counter == mutations_limit:
            break
        mutations_counter += 1
        paths = conf.get_paths_dic(mut)
        paths['step3_scw']['input_pdb_path']=initial_structure_pdb_path
        prop = conf.get_prop_dic(mut)

        out_log.info('')
        out_log.info('-------------------------')
        out_log.info(str(mutations_counter) + '/' + str(mutations_limit) + ' ' + mut)
        out_log.info('-------------------------')
        out_log.info('')

        out_log.info('step3:  scw ------ Model mutation')
        fu.create_dir(prop['step3_scw']['path'])
        scwrl_pc(properties=prop['step3_scw'], **paths['step3_scw'])

        out_log.info('step4:  p2g ------ Create gromacs topology')
        fu.create_dir(prop['step4_p2g']['path'])
        pdb2gmx_pc(properties=prop['step4_p2g'], **paths['step4_p2g'])

        out_log.info('step5:  ec ------- Define box dimensions')
        fu.create_dir(prop['step5_ec']['path'])
        editconf_pc(properties=prop['step5_ec'], **paths['step5_ec'])

    #     out_log.info('step6:  sol ------ Fill the box with water molecules')
    #     fu.create_dir(prop['step6_sol']['path'])
    #     solvate_pc(properties=prop['step6_sol'], **paths['step6_sol']).launch()
    #
    #     out_log.info('step7:  gppions -- Preprocessing: Add ions to neutralice the charge')
    #     fu.create_dir(prop['step7_gppions']['path'])
    #     grompp_pc(properties=prop['step7_gppions'], **paths['step7_gppions']).launch()
    #
    #     out_log.info('step8:  gio ------ Running: Add ions to neutralice the charge')
    #     fu.create_dir(prop['step8_gio']['path'])
    #     genion_pc(properties=prop['step8_gio'], **paths['step8_gio']).launch()
    #
    #     out_log.info('step9:  gppmin --- Preprocessing: Energy minimization')
    #     fu.create_dir(prop['step9_gppmin']['path'])
    #     grompp_pc(properties=prop['step9_gppmin'], **paths['step9_gppmin']).launch()
    #
    #     out_log.info('step10: mdmin ---- Running: Energy minimization')
    #     fu.create_dir(prop['step10_mdmin']['path'])
    #     mdrun_pc(properties=prop['step10_mdmin'], **paths['step10_mdmin']).launch()
    #
    #     out_log.info('step11: gppnvt --- Preprocessing: nvt constant number of molecules, volume and temp')
    #     fu.create_dir(prop['step11_gppnvt']['path'])
    #     grompp_pc(properties=prop['step11_gppnvt'], **paths['step11_gppnvt']).launch()
    #
    #     out_log.info('step12: mdnvt ---- Running: nvt constant number of molecules, volume and temp')
    #     fu.create_dir(prop['step12_mdnvt']['path'])
    #     mdrun_pc(properties=prop['step12_mdnvt'], **paths['step12_mdnvt']).launch()
    #
    #     out_log.info('step13: gppnpt --- Preprocessing: npt constant number of molecules, pressure and temp')
    #     fu.create_dir(prop['step13_gppnpt']['path'])
    #     grompp_pc(properties=prop['step13_gppnpt'], **paths['step13_gppnpt']).launch()
    #
    #     out_log.info('step14: mdnpt ---- Running: npt constant number of molecules, pressure and temp')
    #     fu.create_dir(prop['step14_mdnpt']['path'])
    #     mdrun_pc(properties=prop['step14_mdnpt'], **paths['step14_mdnpt']).launch()
    #
    #     out_log.info('step15: gppeq ---- Preprocessing: 1ns Molecular dynamics Equilibration')
    #     fu.create_change_dir(prop['step15_gppeq']['path'])
    #     grompp_pc(properties=prop['step15_gppeq'], **paths['step15_gppeq']).launch()
    #
    #     out_log.info('step16: mdeq ----- Running: 1ns Molecular dynamics Equilibration')
    #     fu.create_dir(prop['step16_mdeq']['path'])
    #     mdrun_pc(properties=prop['step16_mdeq'], **paths['step16_mdeq']).launch()
    #
    #     out_log.info('step17: rmsd ----- Computing RMSD')
    #     fu.create_dir(prop['step17_rmsd']['path'])
    #     rms_list.append(rms_pc(properties=prop['step17_rmsd'], **paths['step17_rmsd']).launch())
    #
    out = reduce(extractValueString, rms_list)
    # out_log.info('step18: gnuplot ----- Creating RMSD plot')
    # fu.create_dir(prop_glob['step18_gnuplot']['path'])
    # gnuplot_pc(input_xvg_path_dict=rmsd_xvg_path_dict, properties=prop_glob['step18_gnuplot'], **paths_glob['step18_gnuplot']).launch()
    # png = compss_wait_on(paths_glob['step18_gnuplot']['output_png_path'])

    elapsed_time = time.time() - start_time
    print "Elapsed time: ", elapsed_time
    with open(opj(workflow_path, 'time.txt'), 'a') as time_file:
        time_file.write('Elapsed time: ')
        time_file.write(str(elapsed_time))
        time_file.write('\n')
        time_file.write('Config File: ')
        time_file.write(sys.argv[1])
        time_file.write('\n')
        time_file.write('Sytem: ')
        time_file.write(sys.argv[2])
        time_file.write('\n')
        if len(sys.argv) >= 4:
            time_file.write('Nodes: ')
            time_file.write(sys.argv[3])
            time_file.write('\n')

@task(returns=list)
def extractValueString(a,b):
    return a.append(b)

############################## PyCOMPSs functions #############################
@task(input_pdb_path=FILE_IN, output_pdb_path=FILE_OUT)
def scwrl_pc(input_pdb_path, output_pdb_path, properties, **kwargs):
    """ Launches SCWRL 4 using the PyCOMPSs library."""
    scwrl.Scwrl4(input_pdb_path, output_pdb_path, properties, **kwargs).launch()

@task(input_structure_pdb_path=FILE_IN, output_gro_path=FILE_OUT, output_top_tar_path=FILE_OUT)
def pdb2gmx_pc(input_structure_pdb_path, output_gro_path, output_top_tar_path,
               properties, **kwargs):
    """Launches the GROMACS pdb2gmx module using the PyCOMPSs library."""
    pdb2gmx.Pdb2gmx(input_structure_pdb_path, output_gro_path, output_top_tar_path,
                    properties, **kwargs).launch()

@task(input_gro_path=FILE_IN, output_gro_path=FILE_OUT)
def editconf_pc(input_gro_path, output_gro_path, properties, **kwargs):
    """Launches the GROMACS editconf module using the PyCOMPSs library."""
    editconf.Editconf(input_gro_path, output_gro_path, properties, **kwargs).launch()

# @task(input_solute_gro_path=FILE_IN, output_gro_path=FILE_OUT, input_top_tar_path=FILE_IN,
#       output_top_path=IN,
#       output_top_tar_path=IN,
#       input_solvent_gro_path=IN,
#       log_path=IN, error_path=IN, gmx_path=IN)
# def solvatePyCOMPSs(dependency_file_in, dependency_file_out, task_path,
#                     input_solute_gro_path,
#                     output_gro_path,
#                     input_top_tar_path,
#                     output_top_path,
#                     output_top_tar_path,
#                     input_solvent_gro_path,
#                     log_path, error_path, gmx_path):
#     """Launches the GROMACS solvate module using the PyCOMPSs library."""
#     fu.create_change_dir(task_path)
#     solvate.Solvate512(input_solute_gro_path,
#                        output_gro_path,
#                        input_top_tar_path,
#                        output_top_path,
#                        output_top_tar_path,
#                        input_solvent_gro_path,
#                        log_path, error_path, gmx_path).launch()
#
#     open(dependency_file_out, 'a').close()
#
#
# @task(dependency_file_in=FILE_IN, dependency_file_out=FILE_OUT, task_path=IN,
#       input_mdp_path=IN,
#       input_gro_path=IN,
#       input_top_tar_path=IN,
#       output_tpr_path=IN,
#       input_cpt_path=IN,
#       log_path=IN, error_path=IN, gmx_path=IN)
# def gromppPyCOMPSs(dependency_file_in, dependency_file_out, task_path,
#                    input_mdp_path,
#                    input_gro_path,
#                    input_top_tar_path,
#                    output_tpr_path,
#                    input_cpt_path,
#                    log_path, error_path, gmx_path):
#     """Launches the GROMACS grompp module using the PyCOMPSs library."""
#     input_cpt_path = None if input_cpt_path.lower() == 'none' else input_cpt_path
#     fu.create_change_dir(task_path)
#     grompp.Grompp512(input_mdp_path,
#                      input_gro_path,
#                      input_top_tar_path,
#                      output_tpr_path,
#                      input_cpt_path,
#                      log_path, error_path, gmx_path).launch()
#     open(dependency_file_out, 'a').close()
#
#
# @task(dependency_file_in=FILE_IN, dependency_file_out=FILE_OUT, task_path=IN,
#       input_tpr_path=IN,
#       output_gro_path=IN,
#       input_top_tar_path=IN,
#       output_top_path=IN,
#       output_top_tar_path=IN,
#       replaced_group=IN,
#       neutral=IN,
#       concentration=IN,
#       seed=IN,
#       log_path=IN, error_path=IN, gmx_path=IN)
# def genionPyCOMPSs(dependency_file_in, dependency_file_out, task_path,
#                    input_tpr_path,
#                    output_gro_path,
#                    input_top_tar_path,
#                    output_top_path,
#                    output_top_tar_path,
#                    replaced_group,
#                    neutral,
#                    concentration,
#                    seed,
#                    log_path, error_path, gmx_path):
#     """Launches the GROMACS genion module using the PyCOMPSs library."""
#     seed = None if seed.lower() == 'none' else seed
#     fu.create_change_dir(task_path)
#     genion.Genion512(input_tpr_path,
#                      output_gro_path,
#                      input_top_tar_path,
#                      output_top_path,
#                      output_top_tar_path,
#                      replaced_group,
#                      neutral,
#                      concentration,
#                      seed,
#                      log_path, error_path, gmx_path).launch()
#     open(dependency_file_out, 'a').close()
#
#
# #@constraint(ComputingUnits="16")
# @task(dependency_file_in=FILE_IN, dependency_file_out=FILE_OUT, task_path=IN,
#       input_tpr_path=IN,
#       output_gro_path=IN,
#       output_trr_path=IN,
#       output_edr_path=IN,
#       output_xtc_path=IN,
#       output_cpt_path=IN,
#       log_path=IN, error_path=IN, gmx_path=IN,
#       num_threads=IN)
# def mdrunPyCOMPSs(dependency_file_in, dependency_file_out, task_path,
#                   input_tpr_path,
#                   output_gro_path,
#                   output_trr_path,
#                   output_edr_path,
#                   output_xtc_path,
#                   output_cpt_path,
#                   log_path, error_path, gmx_path,
#                   num_threads):
#     """Launches the GROMACS mdrun module using the PyCOMPSs library."""
#     output_xtc_path = None if output_xtc_path.lower() == 'none' else output_xtc_path
#     output_cpt_path = None if output_cpt_path.lower() == 'none' else output_cpt_path
#     fu.create_change_dir(task_path)
#     mdrun.Mdrun512(input_tpr_path=input_tpr_path,
#                    output_gro_path=output_gro_path,
#                    output_trr_path=output_trr_path,
#                    output_edr_path=output_edr_path,
#                    output_xtc_path=output_xtc_path,
#                    output_cpt_path=output_cpt_path,
#                    log_path=log_path, error_path=error_path, gmx_path=gmx_path,
#                    num_threads=num_threads).launch()
#
#     open(dependency_file_out, 'a').close()
#
#
# @task(dependency_file_in=FILE_IN, dependency_file_out=FILE_OUT, task_path=IN,
#       input_gro_path=IN,
#       input_trr_path=IN,
#       output_xvg_path=IN,
#       log_path=IN, error_path=IN, gmx_path=IN)
# def rmsdPyCOMPSs(dependency_file_in, dependency_file_out, task_path,
#                  input_gro_path,
#                  input_trr_path,
#                  output_xvg_path,
#                  log_path, error_path, gmx_path):
#     fu.create_change_dir(task_path)
#     rms.Rms512(input_gro_path=input_gro_path,
#                input_trr_path=input_trr_path,
#                output_xvg_path=output_xvg_path,
#                log_path=log_path, error_path=error_path, gmx_path=gmx_path).launch()
#     open(dependency_file_out, 'a').close()
#
# @task(output_png_path=FILE_OUT)
# def gnuplot_pc(input_xvg_path_dict, output_png_path, properties, **kwargs):
#     gnuplot.Gnuplot(input_xvg_path_dict, output_png_path, properties, **kwargs).launch()

##############################################################################


if __name__ == '__main__':
    main()
