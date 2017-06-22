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
        fu.create_change_dir(p_scw['path'])
        p_scw['input_pdb_path']=initial_structure_pdb_path
        scwrl.Scwrl4(**p_scw).launch()

        print 'step4:  p2g ------ Create gromacs topology'
        p_p2g = conf.step_prop_dic('step4_p2g', workflow_path, mut)
        fu.create_change_dir(p_p2g['path'])
        pdb2gmx.Pdb2gmx512(**p_p2g).launch()

        print 'step5:  ec ------- Define box dimensions'
        p_ec = conf.step_prop_dic('step5_ec', workflow_path, mut)
        fu.create_change_dir(p_ec['path'])
        editconf.Editconf512(**p_ec).launch()

        print 'step6:  sol ------ Fill the box with water molecules'
        p_sol = conf.step_prop_dic('step6_sol', workflow_path, mut)
        fu.create_change_dir(p_sol['path'])
        solvate.Solvate512(**p_sol).launch()

        print ('step7:  gppions -- Preprocessing: '
               'Add ions to neutralice the charge')
        p_gppions = conf.step_prop_dic('step7_gppions', workflow_path, mut)
        fu.create_change_dir(p_gppions['path'])
        grompp.Grompp512(**p_gppions).launch()

        print 'step8:  gio ------ Running: Add ions to neutralice the charge'
        p_gio = conf.step_prop_dic('step8_gio', workflow_path, mut)
        fu.create_change_dir(p_gio['path'])
        genion.Genion512(**p_gio).launch()

        print 'step9:  gppmin --- Preprocessing: Energy minimization'
        p_gppmin = conf.step_prop_dic('step9_gppmin', workflow_path, mut)
        fu.create_change_dir(p_gppmin['path'])
        grompp.Grompp512(**p_gppmin).launch()

        print 'step10: mdmin ---- Running: Energy minimization'
        p_mdmin = conf.step_prop_dic('step10_mdmin', workflow_path, mut)
        fu.create_change_dir(p_mdmin['path'])
        mdrun.Mdrun512(**p_mdmin).launch()

        print ('step11: gppnvt --- Preprocessing: nvt '
               'constant number of molecules, volume and temp')
        p_gppnvt = conf.step_prop_dic('step11_gppnvt', workflow_path, mut)
        fu.create_change_dir(p_gppnvt['path'])
        grompp.Grompp512(**p_gppnvt).launch()

        print ('step12: mdnvt ---- Running: nvt '
               'constant number of molecules, volume and temp')
        p_mdnvt = conf.step_prop_dic('step12_mdnvt', workflow_path, mut)
        fu.create_change_dir(p_mdnvt['path'])
        mdrun.Mdrun512(**p_mdnvt).launch()

        print ('step13: gppnpt --- Preprocessing: npt '
               'constant number of molecules, pressure and temp')
        p_gppnpt = conf.step_prop_dic('step13_gppnpt', workflow_path, mut)
        fu.create_change_dir(p_gppnpt['path'])
        grompp.Grompp512(**p_gppnpt).launch()

        print ('step14: mdnpt ---- Running: npt '
               'constant number of molecules, pressure and temp')
        p_mdnpt = conf.step_prop_dic('step14_mdnpt', workflow_path, mut)
        fu.create_change_dir(p_mdnpt['path'])
        mdnpt = mdrun.Mdrun512(**p_mdnpt).launch()

        print ('step15: gppeq ---- '
               'Preprocessing: 1ns Molecular dynamics Equilibration')
        p_gppeq = conf.step_prop_dic('step15_gppeq', workflow_path, mut)
        fu.create_change_dir(p_gppeq['path'])
        gppeq = grompp.Grompp512(**p_gppeq).launch()

        print ('step16: mdeq ----- '
               'Running: 1ns Molecular dynamics Equilibration')
        p_mdeq = conf.step_prop_dic('step16_mdeq', workflow_path, mut)
        fu.create_change_dir(p_mdeq['path'])
        mdeq = mdrun.Mdrun512(**p_mdeq).launch()

        print ('step17: rmsd ----- Computing RMSD')
        p_rmsd = conf.step_prop_dic('step17_rmsd', workflow_path, mut)
        fu.create_change_dir(p_rmsd['path'])
        rms.Rms512(**p_rmsd).launch()
        rmsd_xvg_path_dict[mut] = p_rmsd['output_xvg_path']

        print '***************************************************************'
        print ''

    print ('step18: gnuplot ----- Creating RMSD plot')
    p_gnuplot = conf.step_prop_dic('step18_gnuplot', workflow_path)
    p_gnuplot['input_xvg_path_dict']=rmsd_xvg_path_dict
    fu.create_change_dir(p_gnuplot['path'])
    gnuplot.Gnuplot46(**p_gnuplot).launch()

    elapsed_time = time.time() - start_time
    print '\n\n'
    print '***********************************'
    print 'Execution sucessful: '
    print "Workflow_path: ", workflow_path
    print "Elapsed time: ", elapsed_time, " seconds"
    print '***********************************'
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

if __name__ == '__main__':
    main()
