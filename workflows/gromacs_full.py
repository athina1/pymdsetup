"""
Gromacs full setup from a PDB code
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


def main():
    start_time = time.time()
    conf_file_path = sys.argv[1]
    sys_paths = sys.argv[2]
    conf = settings.YamlReader(yaml_path=(conf_file_path))
    prop = conf.properties
    mdp_dir = prop[sys_paths]['mdp_path']
    gmx_path = prop[sys_paths]['gmx_path']
    scwrl_path = prop[sys_paths]['scwrl4_path']
    gnuplot_path = prop[sys_paths]['gnuplot_path']
    input_structure_pdb_path = prop[sys_paths].get('input_structure_pdb_path')
    input_mapped_mutations_list = prop.get('input_mapped_mutations_list')
    workflow_path = fu.get_workflow_path(prop[sys_paths]['workflow_path'])
    fu.create_dir(os.path.abspath(workflow_path))

    print ''
    print ''
    print '_______GROMACS FULL WORKFLOW_______'
    print ''
    print ''

    # If no PDB structure is provided the structure will be downloaded
    if ( input_structure_pdb_path is None or
         not os.path.isfile(input_structure_pdb_path) ):
        print 'step1:  mmbpdb -- Get PDB'
        p_mmbpdb = conf.step_prop_dic('step1_mmbpdb', workflow_path)
        print '     Selected PDB code: ' + p_mmbpdb["pdb_code"]
        fu.create_dir(p_mmbpdb["path"])
        mmbpdb = pdb.MmbPdb(**p_mmbpdb)
        mmbpdb.get_pdb()
        input_structure_pdb_path = p_mmbpdb["pdb_code"]

    # If no mapped to pdb structure mutation list is provided the mutation list
    # will be downloaded from the MMB rest API
    if ( input_mapped_mutations_list is None or
         len(input_mapped_mutations_list) < 7 ):
        print 'step2:  mmbuniprot -- Get mutations'
        p_mmbuniprot = conf.step_prop_dic('step2_mmbuniprot', workflow_path)
        mmbuniprot = uniprot.MmbVariants(p_mmbuniprot["pdb_code"])
        mutations = mmbuniprot.get_pdb_variants()

        # This is part of the code prints some feedback to the user
        print '     Uniprot code: ' + mmbuniprot.get_uniprot()
        if mutations is None or len(mutations) == 0:
            print (prop['pdb_code'] +
                   " " + mmbuniprot.get_uniprot() + ": No variants")
            return
        else:
            print ('     Found ' + str(len(mmbuniprot.get_variants())) +
                   ' uniprot variants')
            print ('     Mapped to ' + str(len(mutations)) + ' ' +
                   p_mmbuniprot["pdb_code"] + ' PDB variants')

    else:
        mutations = [m.strip() for m in input_mapped_mutations_list.split(',')]

    # Number of mutations to be modelled
    if prop['mutations_limit'] is None or int(prop['mutations_limit']) == 0:
        mutations_limit = len(mutations)
    else:
        mutations_limit = min(len(mutations), int(prop['mutations_limit']))
    print 'Number of mutations to be modelled: ' + str(mutations_limit)

    rmsd_xvg_path_dict = {}
    mutations_counter = 0
    # for mut in mutations:
    #     if mutations_counter == mutations_limit:
    #         break
    #     mutations_counter += 1
    #     print ''
    #     print '___________'
    #     print str(mutations_counter) + '/' + str(mutations_limit) + ' ' + mut
    #     print '-----------'
    #
    #     print 'step3:  scw ------ Model mutation'
    #     p_scw = conf.step_prop_obj('step3_scw', workflow_path, mut)
    #     fu.create_change_dir(p_scw.path)
    #     scw = scwrl.Scwrl4(input_pdb_path=input_structure_pdb_path,
    #                        output_pdb_path=p_scw.mut_pdb,
    #                        mutation=mut,
    #                        error_path=p_scw.err, log_path=p_scw.out, scwrl_path=scwrl_path)
    #     scw.launch()
    #
    #     print 'step4:  p2g ------ Create gromacs topology'
    #     p_p2g = conf.step_prop_obj('step4_p2g', workflow_path, mut)
    #     fu.create_change_dir(p_p2g.path)
    #     p2g = pdb2gmx.Pdb2gmx512(input_structure_pdb_path=p_scw.mut_pdb,
    #                              output_gro_path=p_p2g.gro,
    #                              output_top_path=p_p2g.top,
    #                              output_itp_path=prop['step4_p2g']['paths']['itp'],
    #                              output_top_tar_path=p_p2g.tar,
    #                              water_type=p_p2g.water_type,
    #                              force_field=p_p2g.force_field,
    #                              ignh=settings.str2bool(p_p2g.ignh),
    #                              gmx_path=gmx_path,
    #                              log_path=p_p2g.out, error_path=p_p2g.err)
    #     p2g.launch()
    #
    #     print 'step5:  ec ------- Define box dimensions'
    #     p_ec = conf.step_prop_obj('step5_ec', workflow_path, mut)
    #     fu.create_change_dir(p_ec.path)
    #     ec = editconf.Editconf512(input_gro_path=p_p2g.gro,
    #                               output_gro_path=p_ec.gro,
    #                               box_type=p_ec.box_type,
    #                               distance_to_molecule=float(p_ec.distance_to_molecule),
    #                               center_molecule=settings.str2bool(p_ec.center_molecule),
    #                               log_path=p_ec.out, error_path=p_ec.err, gmx_path=gmx_path)
    #     ec.launch()
    #
    #     print 'step6:  sol ------ Fill the box with water molecules'
    #     p_sol = conf.step_prop_obj('step6_sol', workflow_path, mut)
    #     fu.create_change_dir(p_sol.path)
    #     sol = solvate.Solvate512(input_solute_gro_path=p_ec.gro,
    #                              output_gro_path=p_sol.gro,
    #                              input_top_tar_path=p_p2g.tar,
    #                              output_top_path=p_sol.top,
    #                              output_top_tar_path=p_sol.tar,
    #                              input_solvent_gro_path=p_sol.input_solvent_gro_path,
    #                              log_path=p_sol.out, error_path=p_sol.err, gmx_path=gmx_path,)
    #     sol.launch()
    #
    #     print ('step7:  gppions -- Preprocessing: '
    #            'Add ions to neutralice the charge')
    #     p_gppions = conf.step_prop_obj('step7_gppions', workflow_path, mut)
    #     fu.create_change_dir(p_gppions.path)
    #     gppions = grompp.Grompp512(input_mdp_path=opj(mdp_dir, prop['step7_gppions']['paths']['mdp']),
    #                                input_gro_path=p_sol.gro,
    #                                input_top_tar_path=p_sol.tar,
    #                                output_tpr_path=p_gppions.tpr,
    #                                log_path=p_gppions.out, error_path=p_gppions.err, gmx_path=gmx_path)
    #     gppions.launch()
    #
    #     print 'step8:  gio ------ Running: Add ions to neutralice the charge'
    #     p_gio = conf.step_prop_obj('step8_gio', workflow_path, mut)
    #     fu.create_change_dir(p_gio.path)
    #     gio = genion.Genion512(input_tpr_path=p_gppions.tpr,
    #                            output_gro_path=p_gio.gro,
    #                            input_top_tar_path=p_sol.tar,
    #                            output_top_path=p_gio.top,
    #                            output_top_tar_path=p_gio.tar,
    #                            neutral=settings.str2bool(p_gio.neutral),
    #                            concentration=float(p_gio.concentration),
    #                            log_path=p_gio.out, error_path=p_gio.err, gmx_path=gmx_path)
    #     gio.launch()
    #
    #     print 'step9:  gppmin --- Preprocessing: Energy minimization'
    #     p_gppmin = conf.step_prop_obj('step9_gppmin', workflow_path, mut)
    #     fu.create_change_dir(p_gppmin.path)
    #     gppmin = grompp.Grompp512(input_mdp_path=opj(mdp_dir, prop['step9_gppmin']['paths']['mdp']),
    #                               input_gro_path=p_gio.gro,
    #                               input_top_tar_path=p_gio.tar,
    #                               output_tpr_path=p_gppmin.tpr,
    #                               log_path=p_gppmin.out, error_path=p_gppmin.err, gmx_path=gmx_path)
    #     gppmin.launch()
    #
    #     print 'step10: mdmin ---- Running: Energy minimization'
    #     p_mdmin = conf.step_prop_obj('step10_mdmin', workflow_path, mut)
    #     fu.create_change_dir(p_mdmin.path)
    #     mdmin = mdrun.Mdrun512(input_tpr_path=p_gppmin.tpr,
    #                            output_trr_path=p_mdmin.trr,
    #                            output_gro_path=p_mdmin.gro,
    #                            output_edr_path=p_mdmin.edr,
    #                            log_path=p_mdmin.out, error_path=p_mdmin.err, gmx_path=gmx_path,
    #                            num_threads=p_mdmin.num_threads)
    #     mdmin.launch()
    #
    #     print ('step11: gppnvt --- Preprocessing: nvt '
    #            'constant number of molecules, volume and temp')
    #     p_gppnvt = conf.step_prop_obj('step11_gppnvt', workflow_path, mut)
    #     fu.create_change_dir(p_gppnvt.path)
    #     gppnvt = grompp.Grompp512(input_mdp_path=opj(mdp_dir, prop['step11_gppnvt']['paths']['mdp']),
    #                               input_gro_path=p_mdmin.gro,
    #                               input_top_tar_path=p_gio.tar,
    #                               output_tpr_path=p_gppnvt.tpr,
    #                               log_path=p_gppnvt.out, error_path=p_gppnvt.err, gmx_path=gmx_path)
    #     gppnvt.launch()
    #
    #     print ('step12: mdnvt ---- Running: nvt '
    #            'constant number of molecules, volume and temp')
    #     p_mdnvt = conf.step_prop_obj('step12_mdnvt', workflow_path, mut)
    #     fu.create_change_dir(p_mdnvt.path)
    #     mdnvt = mdrun.Mdrun512(input_tpr_path=p_gppnvt.tpr,
    #                            output_trr_path=p_mdnvt.trr,
    #                            output_gro_path=p_mdnvt.gro,
    #                            output_edr_path=p_mdnvt.edr,
    #                            output_cpt_path=p_mdnvt.cpt,
    #                            log_path=p_mdnvt.out, error_path=p_mdnvt.err, gmx_path=gmx_path,
    #                            num_threads=p_mdnvt.num_threads)
    #     mdnvt.launch()
    #
    #     print ('step13: gppnpt --- Preprocessing: npt '
    #            'constant number of molecules, pressure and temp')
    #     p_gppnpt = conf.step_prop_obj('step13_gppnpt', workflow_path, mut)
    #     fu.create_change_dir(p_gppnpt.path)
    #     gppnpt = grompp.Grompp512(input_mdp_path=opj(mdp_dir, prop['step13_gppnpt']['paths']['mdp']),
    #                               input_gro_path=p_mdnvt.gro,
    #                               input_top_tar_path=p_gio.tar,
    #                               output_tpr_path=p_gppnpt.tpr,
    #                               input_cpt_path=p_mdnvt.cpt,
    #                               log_path=p_gppnpt.out, error_path=p_gppnpt.err, gmx_path=gmx_path)
    #     gppnpt.launch()
    #
    #     print ('step14: mdnpt ---- Running: npt '
    #            'constant number of molecules, pressure and temp')
    #     p_mdnpt = conf.step_prop_obj('step14_mdnpt', workflow_path, mut)
    #     fu.create_change_dir(p_mdnpt.path)
    #     mdnpt = mdrun.Mdrun512(input_tpr_path=p_gppnpt.tpr,
    #                            output_trr_path=p_mdnpt.trr,
    #                            output_gro_path=p_mdnpt.gro,
    #                            output_edr_path=p_mdnpt.edr,
    #                            output_cpt_path=p_mdnpt.cpt,
    #                            log_path=p_mdnpt.out, error_path=p_mdnpt.err, gmx_path=gmx_path,
    #                            num_threads=p_mdnpt.num_threads)
    #     mdnpt.launch()
    #
    #     print ('step15: gppeq ---- '
    #            'Preprocessing: 1ns Molecular dynamics Equilibration')
    #     p_gppeq = conf.step_prop_obj('step15_gppeq', workflow_path, mut)
    #     fu.create_change_dir(p_gppeq.path)
    #     gppeq = grompp.Grompp512(input_mdp_path=opj(mdp_dir, prop['step15_gppeq']['paths']['mdp']),
    #                              input_gro_path=p_mdnpt.gro,
    #                              input_top_tar_path=p_gio.tar,
    #                              output_tpr_path=p_gppeq.tpr,
    #                              input_cpt_path=p_mdnpt.cpt,
    #                              log_path=p_gppeq.out, error_path=p_gppeq.err, gmx_path=gmx_path)
    #     gppeq.launch()
    #
    #     print ('step16: mdeq ----- '
    #            'Running: 1ns Molecular dynamics Equilibration')
    #     p_mdeq = conf.step_prop_obj('step16_mdeq', workflow_path, mut)
    #     fu.create_change_dir(p_mdeq.path)
    #     mdeq = mdrun.Mdrun512(input_tpr_path=p_gppeq.tpr,
    #                           output_trr_path=p_mdeq.trr,
    #                           output_gro_path=p_mdeq.gro,
    #                           output_edr_path=p_mdeq.edr,
    #                           output_cpt_path=p_mdeq.cpt,
    #                           log_path=p_mdeq.out, error_path=p_mdeq.err, gmx_path=gmx_path,
    #                           num_threads=p_mdeq.num_threads)
    #     mdeq.launch()
    #
    #     print ('step17: rmsd ----- Computing RMSD')
    #     p_rmsd = conf.step_prop_obj('step17_rmsd', workflow_path, mut)
    #     fu.create_change_dir(p_rmsd.path)
    #     rmsd = rms.Rms512(input_gro_path=p_gio.gro,
    #                       input_trr_path=p_mdeq.trr,
    #                       output_xvg_path=p_rmsd.xvg,
    #                       log_path=p_rmsd.out, error_path=p_rmsd.err, gmx_path=gmx_path)
    #     rmsd.launch()
    #     rmsd_xvg_path_dict[mut] = p_rmsd.xvg
    #
    #     print '***************************************************************'
    #     print ''
    #
    # print ('step18: gnuplot ----- Creating RMSD plot')
    # p_gnuplot = conf.step_prop_obj('step18_gnuplot', workflow_path)
    # fu.create_change_dir(p_gnuplot.path)
    # gplot = gnuplot.Gnuplot46(input_xvg_path_dict=rmsd_xvg_path_dict,
    #                           output_png_path=p_gnuplot.png,
    #                           output_plotscript_path=p_gnuplot.plotscript,
    #                           log_path=p_gnuplot.out, error_path=p_gnuplot.err, gnuplot_path=gnuplot_path)
    # gplot.launch()

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

if __name__ == '__main__':
    main()
