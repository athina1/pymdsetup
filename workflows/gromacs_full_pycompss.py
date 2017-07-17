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
    from pycompss.api.api import waitForAllTasks
    from pycompss.api.api import compss_wait_on
    start_time = time.time()
    conf = settings.YamlReader(yaml_path=(sys.argv[1]), system=sys.argv[2])
    workflow_path = fu.get_workflow_path(conf.properties[sys.argv[2]]['workflow_path'])
    fu.create_dir(os.path.abspath(workflow_path))

    print '\n\n','_______GROMACS FULL WORKFLOW_______','\n\n'

    # If no PDB structure is provided the structure will be downloaded
    p_mmbpdb = conf.step_prop_dic('step1_mmbpdb', workflow_path)
    if ( p_mmbpdb.get('initial_structure_pdb_path') is None or
         not os.path.isfile(p_mmbpdb.get('initial_structure_pdb_path')) ):
        print 'step1:  mmbpdb -- Get PDB'
        print '     Selected PDB code: ' + p_mmbpdb["pdb_code"]
        fu.create_dir(p_mmbpdb["path"])
        pdb.MmbPdb(**p_mmbpdb).get_pdb()
        initial_structure_pdb_path = p_mmbpdb["output_pdb_path"]
    else:
        initial_structure_pdb_path = p_mmbpdb.get('initial_structure_pdb_path')

    # If no mapped to pdb structure mutation list is provided the mutation list
    # will be downloaded from the MMB rest API
    p_mmbuniprot = conf.step_prop_dic('step2_mmbuniprot', workflow_path)
    if ( p_mmbuniprot.get('input_mapped_mutations_list') is None or
         len(p_mmbuniprot.get('input_mapped_mutations_list')) < 7 ):
        print 'step2:  mmbuniprot -- Get mutations'
        mmbuniprot = uniprot.MmbVariants(p_mmbuniprot["pdb_code"])
        mutations = mmbuniprot.get_pdb_variants()

        # This is part of the code prints some feedback to the user
        print '     Uniprot code: ' + mmbuniprot.get_uniprot()
        if mutations is None or len(mutations) == 0:
            print (prop['pdb_code'] + " " + mmbuniprot.get_uniprot() + ": No variants")
            return
        else:
            print ('     Found ' + str(len(mmbuniprot.get_variants())) + ' uniprot variants')
            print ('     Mapped to ' + str(len(mutations)) + ' ' + p_mmbuniprot["pdb_code"] + ' PDB variants')

    else:
        mutations = [m.strip() for m in p_mmbuniprot.get('input_mapped_mutations_list').split(',')]

    # Number of mutations to be modelled
    if ( conf.properties.get('mutations_limit') is None
         or int(conf.properties.get('mutations_limit')) == 0 ):
        mutations_limit = len(mutations)
    else:
        mutations_limit = min(len(mutations), int(prop['mutations_limit']))
    print 'Number of mutations to be modelled: ' + str(mutations_limit)

    rmsd_xvg_path_dict = {}
    mutations_counter = 0
    for mut in mutations:
        if mutations_counter == mutations_limit:
            break
        mutations_counter += 1
        print '\n','___________'
        print str(mutations_counter) + '/' + str(mutations_limit) + ' ' + mut
        print '-----------'

        print 'step3:  scw ------ Model mutation'
        p_scw = conf.step_prop_dic('step3_scw', workflow_path, mut)
        p_scw['input_pdb_path']=initial_structure_pdb_path
        scwrl_pc(**p_scw)

    #     print 'step4:  p2g ------ Create gromacs topology'
    #     p_p2g = conf.step_prop('step4_p2g', workflow_path, mut)
    #     pdb2gmxPyCOMPSs(dependency_file_in=opj(p_scw.path, 'step3_scw.task'),
    #                     dependency_file_out=opj(p_p2g.path, 'step4_p2g.task'),
    #                     task_path=p_p2g.path,
    #                     input_structure_pdb_path=p_scw.mut_pdb,
    #                     output_gro_path=p_p2g.gro,
    #                     output_top_path=p_p2g.top,
    #                     output_itp_path=prop['step4_p2g']['paths']['itp'],
    #                     output_top_tar_path=p_p2g.tar,
    #                     water_type=p_p2g.water_type,
    #                     force_field=p_p2g.force_field,
    #                     ignh=settings.str2bool(p_p2g.ignh),
    #                     log_path=p_p2g.out, error_path=p_p2g.err, gmx_path=gmx_path)
    #
    #     print 'step5:  ec ------- Define box dimensions'
    #     p_ec = conf.step_prop('step5_ec', workflow_path, mut)
    #     editconfPyCOMPSs(dependency_file_in=opj(p_p2g.path, 'step4_p2g.task'),
    #                      dependency_file_out=opj(p_ec.path, 'step5_ec.task'),
    #                      task_path=p_ec.path,
    #                      input_gro_path=p_p2g.gro,
    #                      output_gro_path=p_ec.gro,
    #                      distance_to_molecule=float(p_ec.distance_to_molecule),
    #                      box_type=p_ec.box_type,
    #                      center_molecule=settings.str2bool(p_ec.center_molecule),
    #                      log_path=p_ec.out, error_path=p_ec.err, gmx_path=gmx_path)
    #
    #     print 'step6:  sol ------ Fill the box with water molecules'
    #     p_sol = conf.step_prop('step6_sol', workflow_path, mut)
    #     solvatePyCOMPSs(dependency_file_in=opj(p_ec.path, 'step5_ec.task'),
    #                     dependency_file_out=opj(p_sol.path, 'step6_sol.task'),
    #                     task_path=p_sol.path,
    #                     input_solute_gro_path=p_ec.gro,
    #                     output_gro_path=p_sol.gro,
    #                     input_top_tar_path=p_p2g.tar,
    #                     output_top_path=p_sol.top,
    #                     output_top_tar_path=p_sol.tar,
    #                     input_solvent_gro_path=p_sol.input_solvent_gro_path,
    #                     log_path=p_sol.out, error_path=p_sol.err, gmx_path=gmx_path)
    #
    #     print ('step7:  gppions -- Preprocessing: '
    #            'Add ions to neutralice the charge')
    #     p_gppions = conf.step_prop('step7_gppions', workflow_path, mut)
    #     gromppPyCOMPSs(dependency_file_in=opj(p_sol.path, 'step6_sol.task'),
    #                    dependency_file_out=opj(p_gppions.path, 'step7_gppions.task'),
    #                    task_path=p_gppions.path,
    #                    input_mdp_path=opj(mdp_dir, prop['step7_gppions']['paths']['mdp']),
    #                    input_gro_path=p_sol.gro,
    #                    input_top_tar_path=p_sol.tar,
    #                    output_tpr_path=p_gppions.tpr,
    #                    input_cpt_path='None',
    #                    log_path=p_gppions.out, error_path=p_gppions.err, gmx_path=gmx_path)
    #
    #     print 'step8:  gio ------ Running: Add ions to neutralice the charge'
    #     p_gio = conf.step_prop('step8_gio', workflow_path, mut)
    #     genionPyCOMPSs(dependency_file_in=opj(p_gppions.path, 'step7_gppions.task'),
    #                    dependency_file_out=opj(p_gppions.path, 'step8_gio.task'),
    #                    task_path=p_gio.path,
    #                    input_tpr_path=p_gppions.tpr,
    #                    output_gro_path=p_gio.gro,
    #                    input_top_tar_path=p_sol.tar,
    #                    output_top_path=p_gio.top,
    #                    output_top_tar_path=p_gio.tar,
    #                    replaced_group='SOL',
    #                    neutral=settings.str2bool(p_gio.neutral),
    #                    concentration=float(p_gio.concentration),
    #                    seed='None',
    #                    log_path=p_gio.out, error_path=p_gio.err, gmx_path=gmx_path)
    #
    #     print 'step9:  gppmin --- Preprocessing: Energy minimization'
    #     p_gppmin = conf.step_prop('step9_gppmin', workflow_path, mut)
    #     gromppPyCOMPSs(dependency_file_in=opj(p_gppions.path, 'step8_gio.task'),
    #                    dependency_file_out=opj(p_gppmin.path, 'step9_gppmin.task'),
    #                    task_path=p_gppmin.path,
    #                    input_mdp_path=opj(mdp_dir, prop['step9_gppmin']['paths']['mdp']),
    #                    input_gro_path=p_gio.gro,
    #                    input_top_tar_path=p_gio.tar,
    #                    output_tpr_path=p_gppmin.tpr,
    #                    input_cpt_path='None',
    #                    log_path=p_gppmin.out, error_path=p_gppmin.err, gmx_path=gmx_path)
    #
    #     print 'step10: mdmin ---- Running: Energy minimization'
    #     p_mdmin = conf.step_prop('step10_mdmin', workflow_path, mut)
    #     mdrunPyCOMPSs(dependency_file_in=opj(p_gppmin.path, 'step9_gppmin.task'),
    #                   dependency_file_out=opj(p_mdmin.path, 'step10_mdmin.task'),
    #                   task_path=p_mdmin.path,
    #                   input_tpr_path=p_gppmin.tpr,
    #                   output_gro_path=p_mdmin.gro,
    #                   output_trr_path=p_mdmin.trr,
    #                   output_edr_path=p_mdmin.edr,
    #                   output_xtc_path='None',
    #                   output_cpt_path='None',
    #                   log_path=p_mdmin.out, error_path=p_mdmin.err, gmx_path=gmx_path,
    #                   num_threads=p_mdmin.num_threads)
    #
    #     print ('step11: gppnvt --- Preprocessing: nvt '
    #            'constant number of molecules, volume and temp')
    #     p_gppnvt = conf.step_prop('step11_gppnvt', workflow_path, mut)
    #     gromppPyCOMPSs(dependency_file_in=opj(p_mdmin.path, 'step10_mdmin.task'),
    #                    dependency_file_out=opj(p_gppnvt.path, 'step11_gppnvt.task'),
    #                    task_path=p_gppnvt.path,
    #                    input_mdp_path=opj(mdp_dir, prop['step11_gppnvt']['paths']['mdp']),
    #                    input_gro_path=p_mdmin.gro,
    #                    input_top_tar_path=p_gio.tar,
    #                    output_tpr_path=p_gppnvt.tpr,
    #                    input_cpt_path='None',
    #                    log_path=p_gppnvt.out, error_path=p_gppnvt.err, gmx_path=gmx_path)
    #
    #     print ('step12: mdnvt ---- Running: nvt '
    #            'constant number of molecules, volume and temp')
    #     p_mdnvt = conf.step_prop('step12_mdnvt', workflow_path, mut)
    #     mdrunPyCOMPSs(dependency_file_in=opj(p_gppnvt.path, 'step11_gppnvt.task'),
    #                   dependency_file_out=opj(p_mdnvt.path, 'step12_mdnvt.task'),
    #                   task_path=p_mdnvt.path,
    #                   input_tpr_path=p_gppnvt.tpr,
    #                   output_gro_path=p_mdnvt.gro,
    #                   output_trr_path=p_mdnvt.trr,
    #                   output_edr_path=p_mdnvt.edr,
    #                   output_xtc_path=p_mdnvt.xtc,
    #                   output_cpt_path=p_mdnvt.cpt,
    #                   log_path=p_mdnvt.out, error_path=p_mdnvt.err, gmx_path=gmx_path,
    #                   num_threads=p_mdnvt.num_threads)
    #
    #     print ('step13: gppnpt --- Preprocessing: npt '
    #            'constant number of molecules, pressure and temp')
    #     p_gppnpt = conf.step_prop('step13_gppnpt', workflow_path, mut)
    #     gromppPyCOMPSs(dependency_file_in=opj(p_mdnvt.path, 'step12_mdnvt.task'),
    #                    dependency_file_out=opj(p_gppnpt.path, 'step13_gppnpt.task'),
    #                    task_path=p_gppnpt.path,
    #                    input_mdp_path=opj(mdp_dir, prop['step13_gppnpt']['paths']['mdp']),
    #                    input_gro_path=p_mdnvt.gro,
    #                    input_top_tar_path=p_gio.tar,
    #                    output_tpr_path=p_gppnpt.tpr,
    #                    input_cpt_path=p_mdnvt.cpt,
    #                    log_path=p_gppnpt.out, error_path=p_gppnpt.err, gmx_path=gmx_path,)
    #
    #     print ('step14: mdnpt ---- Running: npt '
    #            'constant number of molecules, pressure and temp')
    #     p_mdnpt = conf.step_prop('step14_mdnpt', workflow_path, mut)
    #     mdrunPyCOMPSs(dependency_file_in=opj(p_gppnpt.path, 'step13_gppnpt.task'),
    #                   dependency_file_out=opj(p_mdnpt.path, 'step14_mdnpt.task'),
    #                   task_path=p_mdnpt.path,
    #                   input_tpr_path=p_gppnpt.tpr,
    #                   output_gro_path=p_mdnpt.gro,
    #                   output_trr_path=p_mdnpt.trr,
    #                   output_edr_path=p_mdnpt.edr,
    #                   output_xtc_path=p_mdnpt.xtc,
    #                   output_cpt_path=p_mdnpt.cpt,
    #                   log_path=p_mdnpt.out, error_path=p_mdnpt.err, gmx_path=gmx_path,
    #                   num_threads=p_mdnvt.num_threads)
    #
    #     print ('step15: gppeq ---- '
    #            'Preprocessing: 1ns Molecular dynamics Equilibration')
    #     p_gppeq = conf.step_prop('step15_gppeq', workflow_path, mut)
    #     gromppPyCOMPSs(dependency_file_in=opj(p_mdnpt.path, 'step14_mdnpt.task'),
    #                    dependency_file_out=opj(p_gppeq.path, 'step15_gppeq.task'),
    #                    task_path=p_gppeq.path,
    #                    input_mdp_path=opj(mdp_dir, prop['step15_gppeq']['paths']['mdp']),
    #                    input_gro_path=p_mdnpt.gro,
    #                    input_top_tar_path=p_gio.tar,
    #                    output_tpr_path=p_gppeq.tpr,
    #                    input_cpt_path=p_mdnpt.cpt,
    #                    log_path=p_gppeq.out, error_path=p_gppeq.err, gmx_path=gmx_path)
    #
    #     print ('step16: mdeq ----- '
    #            'Running: 1ns Molecular dynamics Equilibration')
    #     p_mdeq = conf.step_prop('step16_mdeq', workflow_path, mut)
    #     mdrunPyCOMPSs(dependency_file_in=opj(p_gppeq.path, 'step15_gppeq.task'),
    #                   dependency_file_out=opj(p_mdeq.path, 'step16_mdeq.task'),
    #                   task_path=p_mdeq.path,
    #                   input_tpr_path=p_gppeq.tpr,
    #                   output_gro_path=p_mdeq.gro,
    #                   output_trr_path=p_mdeq.trr,
    #                   output_edr_path=p_mdeq.edr,
    #                   output_xtc_path=p_mdeq.xtc,
    #                   output_cpt_path=p_mdeq.cpt,
    #                   log_path=p_mdeq.out, error_path=p_mdeq.err, gmx_path=gmx_path,
    #                   num_threads=p_mdnvt.num_threads)
    #
    #     print ('step17: rmsd ----- Computing RMSD')
    #     p_rmsd = conf.step_prop('step17_rmsd', workflow_path, mut)
    #     rmsdPyCOMPSs(dependency_file_in=opj(p_mdeq.path, 'step16_mdeq.task'),
    #                  dependency_file_out=opj(p_rmsd.path, 'step17_rmsd.task'),
    #                  task_path=p_rmsd.path,
    #                  input_gro_path=p_gio.gro,
    #                  input_trr_path=p_mdeq.trr,
    #                  output_xvg_path=p_rmsd.xvg,
    #                  log_path=p_rmsd.out, error_path=p_rmsd.err, gmx_path=gmx_path)
    #
    #     rmsd_xvg_path_dict[mut] = p_rmsd.xvg
    #
    # waitForAllTasks()
    # print ('step18: gnuplot ----- Creating RMSD plot')
    # p_gnuplot = conf.step_prop('step18_gnuplot', workflow_path)
    # gnuplotPyCOMPSs(dependency_file_out=opj(p_gnuplot.path, 'step18_gnuplot.task'),
    #                 task_path=p_gnuplot.path,
    #                 input_xvg_path_dict=rmsd_xvg_path_dict,
    #                 output_png_path=p_gnuplot.png,
    #                 output_plotscript_path=p_gnuplot.plotscript,
    #                 log_path=p_gnuplot.out, error_path=p_gnuplot.err, gnuplot_path=gnuplot_path)
    # png = compss_wait_on(opj(p_gnuplot.path, 'step18_gnuplot.task'))
    elapsed_time = time.time() - start_time
    print "Elapsed time: ", elapsed_time
    with open(opj(workflow_path, 'time.txt'), 'a') as time_file:
        time_file.write('Elapsed time: ')
        time_file.write(str(elapsed_time))
        time_file.write('\n')
        time_file.write('Config File: ')
        time_file.write(conf_file_path)
        time_file.write('\n')
        time_file.write('Sytem: ')
        time_file.write(sys_paths)
        time_file.write('\n')
        if len(sys.argv) >= 4:
            time_file.write('Nodes: ')
            time_file.write(sys.argv[3])
            time_file.write('\n')

############################## PyCOMPSs functions #############################
@task(input_pdb_path=FILE_IN, output_pdb_path=FILE_OUT)
def scwrlPyCOMPSs(input_pdb_path, output_pdb_path, mutation=None,
                  log_path=None, error_path=None, scwrl4_path=None,
                  path='./', config_string=None, **kwargs):
    """ Launches SCWRL 4 using the PyCOMPSs library."""
    scwrl.Scwrl4(input_pdb_path, output_pdb_path, mutation,
                 log_path, error_path, scwrl4_path,
                 path, config_string, **kwargs).launch()

@task(dependency_file_in=FILE_IN, dependency_file_out=FILE_OUT, task_path=IN,
      input_structure_pdb_path=IN,
      output_gro_path=IN,
      output_top_path=IN,
      output_itp_path=IN,
      output_top_tar_path=IN,
      water_type=IN,
      force_field=IN,
      ignh=IN,
      log_path=IN, error_path=IN, gmx_path=IN)
def pdb2gmxPyCOMPSs(dependency_file_in, dependency_file_out, task_path,
                    input_structure_pdb_path,
                    output_gro_path,
                    output_top_path,
                    output_itp_path,
                    output_top_tar_path,
                    water_type,
                    force_field,
                    ignh,
                    log_path, error_path, gmx_path):
    """Launches the GROMACS pdb2gmx module using the PyCOMPSs library."""
    fu.create_change_dir(task_path)
    pdb2gmx.Pdb2gmx512(input_structure_pdb_path,
                       output_gro_path,
                       output_top_path,
                       output_itp_path,
                       output_top_tar_path,
                       water_type,
                       force_field,
                       ignh,
                       log_path, error_path, gmx_path).launch()

    open(dependency_file_out, 'a').close()


@task(dependency_file_in=FILE_IN, dependency_file_out=FILE_OUT, task_path=IN,
      input_gro_path=IN,
      output_gro_path=IN,
      distance_to_molecule=IN,
      box_type=IN,
      center_molecule=IN,
      log_path=IN, error_path=IN, gmx_path=IN)
def editconfPyCOMPSs(dependency_file_in, dependency_file_out, task_path,
                     input_gro_path,
                     output_gro_path,
                     distance_to_molecule,
                     box_type,
                     center_molecule,
                     log_path, error_path, gmx_path):
    """Launches the GROMACS editconf module using the PyCOMPSs library."""
    fu.create_change_dir(task_path)
    editconf.Editconf512(input_gro_path,
                         output_gro_path,
                         distance_to_molecule,
                         box_type,
                         center_molecule,
                         log_path, error_path, gmx_path).launch()

    open(dependency_file_out, 'a').close()


@task(dependency_file_in=FILE_IN, dependency_file_out=FILE_OUT, task_path=IN,
      input_solute_gro_path=IN,
      output_gro_path=IN,
      input_top_tar_path=IN,
      output_top_path=IN,
      output_top_tar_path=IN,
      input_solvent_gro_path=IN,
      log_path=IN, error_path=IN, gmx_path=IN)
def solvatePyCOMPSs(dependency_file_in, dependency_file_out, task_path,
                    input_solute_gro_path,
                    output_gro_path,
                    input_top_tar_path,
                    output_top_path,
                    output_top_tar_path,
                    input_solvent_gro_path,
                    log_path, error_path, gmx_path):
    """Launches the GROMACS solvate module using the PyCOMPSs library."""
    fu.create_change_dir(task_path)
    solvate.Solvate512(input_solute_gro_path,
                       output_gro_path,
                       input_top_tar_path,
                       output_top_path,
                       output_top_tar_path,
                       input_solvent_gro_path,
                       log_path, error_path, gmx_path).launch()

    open(dependency_file_out, 'a').close()


@task(dependency_file_in=FILE_IN, dependency_file_out=FILE_OUT, task_path=IN,
      input_mdp_path=IN,
      input_gro_path=IN,
      input_top_tar_path=IN,
      output_tpr_path=IN,
      input_cpt_path=IN,
      log_path=IN, error_path=IN, gmx_path=IN)
def gromppPyCOMPSs(dependency_file_in, dependency_file_out, task_path,
                   input_mdp_path,
                   input_gro_path,
                   input_top_tar_path,
                   output_tpr_path,
                   input_cpt_path,
                   log_path, error_path, gmx_path):
    """Launches the GROMACS grompp module using the PyCOMPSs library."""
    input_cpt_path = None if input_cpt_path.lower() == 'none' else input_cpt_path
    fu.create_change_dir(task_path)
    grompp.Grompp512(input_mdp_path,
                     input_gro_path,
                     input_top_tar_path,
                     output_tpr_path,
                     input_cpt_path,
                     log_path, error_path, gmx_path).launch()
    open(dependency_file_out, 'a').close()


@task(dependency_file_in=FILE_IN, dependency_file_out=FILE_OUT, task_path=IN,
      input_tpr_path=IN,
      output_gro_path=IN,
      input_top_tar_path=IN,
      output_top_path=IN,
      output_top_tar_path=IN,
      replaced_group=IN,
      neutral=IN,
      concentration=IN,
      seed=IN,
      log_path=IN, error_path=IN, gmx_path=IN)
def genionPyCOMPSs(dependency_file_in, dependency_file_out, task_path,
                   input_tpr_path,
                   output_gro_path,
                   input_top_tar_path,
                   output_top_path,
                   output_top_tar_path,
                   replaced_group,
                   neutral,
                   concentration,
                   seed,
                   log_path, error_path, gmx_path):
    """Launches the GROMACS genion module using the PyCOMPSs library."""
    seed = None if seed.lower() == 'none' else seed
    fu.create_change_dir(task_path)
    genion.Genion512(input_tpr_path,
                     output_gro_path,
                     input_top_tar_path,
                     output_top_path,
                     output_top_tar_path,
                     replaced_group,
                     neutral,
                     concentration,
                     seed,
                     log_path, error_path, gmx_path).launch()
    open(dependency_file_out, 'a').close()


#@constraint(ComputingUnits="16")
@task(dependency_file_in=FILE_IN, dependency_file_out=FILE_OUT, task_path=IN,
      input_tpr_path=IN,
      output_gro_path=IN,
      output_trr_path=IN,
      output_edr_path=IN,
      output_xtc_path=IN,
      output_cpt_path=IN,
      log_path=IN, error_path=IN, gmx_path=IN,
      num_threads=IN)
def mdrunPyCOMPSs(dependency_file_in, dependency_file_out, task_path,
                  input_tpr_path,
                  output_gro_path,
                  output_trr_path,
                  output_edr_path,
                  output_xtc_path,
                  output_cpt_path,
                  log_path, error_path, gmx_path,
                  num_threads):
    """Launches the GROMACS mdrun module using the PyCOMPSs library."""
    output_xtc_path = None if output_xtc_path.lower() == 'none' else output_xtc_path
    output_cpt_path = None if output_cpt_path.lower() == 'none' else output_cpt_path
    fu.create_change_dir(task_path)
    mdrun.Mdrun512(input_tpr_path=input_tpr_path,
                   output_gro_path=output_gro_path,
                   output_trr_path=output_trr_path,
                   output_edr_path=output_edr_path,
                   output_xtc_path=output_xtc_path,
                   output_cpt_path=output_cpt_path,
                   log_path=log_path, error_path=error_path, gmx_path=gmx_path,
                   num_threads=num_threads).launch()

    open(dependency_file_out, 'a').close()


@task(dependency_file_in=FILE_IN, dependency_file_out=FILE_OUT, task_path=IN,
      input_gro_path=IN,
      input_trr_path=IN,
      output_xvg_path=IN,
      log_path=IN, error_path=IN, gmx_path=IN)
def rmsdPyCOMPSs(dependency_file_in, dependency_file_out, task_path,
                 input_gro_path,
                 input_trr_path,
                 output_xvg_path,
                 log_path, error_path, gmx_path):
    fu.create_change_dir(task_path)
    rms.Rms512(input_gro_path=input_gro_path,
               input_trr_path=input_trr_path,
               output_xvg_path=output_xvg_path,
               log_path=log_path, error_path=error_path, gmx_path=gmx_path).launch()
    open(dependency_file_out, 'a').close()


@task(dependency_file_out=FILE_OUT,
      task_path=IN,
      input_xvg_path_dict=IN,
      output_png_path=IN,
      output_plotscript_path=IN,
      log_path=IN, error_path=IN, gnuplot_path=IN)
def gnuplotPyCOMPSs(dependency_file_out,
                    task_path,
                    input_xvg_path_dict,
                    output_png_path,
                    output_plotscript_path,
                    log_path, error_path, gnuplot_path):
    fu.create_change_dir(task_path)
    gnuplot.Gnuplot46(input_xvg_path_dict=input_xvg_path_dict,
                      output_png_path=output_png_path,
                      output_plotscript_path=output_plotscript_path,
                      log_path=log_path, error_path=error_path, gnuplot_path=gnuplot_path).launch()
    open(dependency_file_out, 'a').close()

##############################################################################


if __name__ == '__main__':
    main()
