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
        out_log.info( '     Selected PDB code: ' + p_mmbpdb["pdb_code"])
        fu.create_dir(paths['path'])
        pdb.MmbPdb(prop['step1_mmbpdb']['pdb_code'], paths['step1_mmbpdb']).get_pdb()
        initial_structure_pdb_path = paths['step1_mmbpdb']["output_pdb_path"]
    else:
        initial_structure_pdb_path = conf.properties[system].get('initial_structure_pdb_path')

    # If no mapped to pdb structure mutation list is provided the mutation list
    # will be downloaded from the MMB rest API
    if ( conf.properties.get('input_mapped_mutations_list') is None or
         len(conf.properties.get('input_mapped_mutations_list')) < 7 ):
        out_log.info( 'step2:  mmbuniprot -- Get mutations')
        mmbuniprot = uniprot.MmbVariants(prop['step1_mmbpdb']['pdb_code'])
        mutations = mmbuniprot.get_pdb_variants()
        # This is part of the code prints some feedback to the user
        out_log.info( '     Uniprot code: ' + mmbuniprot.get_uniprot())
        if mutations is None or len(mutations) == 0:
            out_log.info( (prop['step1_mmbpdb']['pdb_code'] + " " + mmbuniprot.get_uniprot() + ": No variants"))
            return
        else:
            out_log.info( ('     Found ' + str(len(mmbuniprot.get_variants())) + ' uniprot variants'))
            out_log.info( ('     Mapped to ' + str(len(mutations)) + ' ' + prop['step1_mmbpdb']['pdb_code'] + ' PDB variants'))

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
        scwrl.Scwrl4(properties=prop['step3_scw'], **paths['step3_scw']).launch()

        out_log.info('step4:  p2g ------ Create gromacs topology')
        fu.create_dir(prop['step4_p2g']['path'])
        pdb2gmx.Pdb2gmx(properties=prop['step4_p2g'], **paths['step4_p2g']).launch()

        out_log.info('step5:  ec ------- Define box dimensions')
        fu.create_dir(prop['step5_ec']['path'])
        editconf.Editconf(properties=prop['step5_ec'], **paths['step5_ec']).launch()

        out_log.info('step6:  sol ------ Fill the box with water molecules')
        fu.create_dir(prop['step6_sol']['path'])
        solvate.Solvate(properties=prop['step6_sol'], **paths['step6_sol']).launch()

        out_log.info('step7:  gppions -- Preprocessing: Add ions to neutralice the charge')
        fu.create_dir(prop['step7_gppions']['path'])
        grompp.Grompp(properties=prop['step7_gppions'], **paths['step7_gppions']).launch()

        out_log.info('step8:  gio ------ Running: Add ions to neutralice the charge')
        fu.create_dir(prop['step8_gio']['path'])
        genion.Genion(properties=prop['step8_gio'], **paths['step8_gio']).launch()

        out_log.info('step9:  gppmin --- Preprocessing: Energy minimization')
        fu.create_dir(prop['step9_gppmin']['path'])
        grompp.Grompp(properties=prop['step9_gppmin'], **paths['step9_gppmin']).launch()

        out_log.info('step10: mdmin ---- Running: Energy minimization')
        fu.create_dir(prop['step10_mdmin']['path'])
        mdrun.Mdrun(properties=prop['step10_mdmin'], **paths['step10_mdmin']).launch()

        out_log.info('step11: gppnvt --- Preprocessing: nvt constant number of molecules, volume and temp')
        fu.create_dir(prop['step11_gppnvt']['path'])
        grompp.Grompp(properties=prop['step11_gppnvt'], **paths['step11_gppnvt']).launch()

        out_log.info('step12: mdnvt ---- Running: nvt constant number of molecules, volume and temp')
        fu.create_dir(prop['step12_mdnvt']['path'])
        mdrun.Mdrun(properties=prop['step12_mdnvt'], **paths['step12_mdnvt']).launch()

        out_log.info('step13: gppnpt --- Preprocessing: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step13_gppnpt']['path'])
        grompp.Grompp(properties=prop['step13_gppnpt'], **paths['step13_gppnpt']).launch()

        out_log.info('step14: mdnpt ---- Running: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step14_mdnpt']['path'])
        mdrun.Mdrun(properties=prop['step14_mdnpt'], **paths['step14_mdnpt']).launch()

        out_log.info('step15: gppeq ---- Preprocessing: 1ns Molecular dynamics Equilibration')
        fu.create_change_dir(prop['step15_gppeq']['path'])
        grompp.Grompp(properties=prop['step15_gppeq'], **paths['step15_gppeq']).launch()

        out_log.info('step16: mdeq ----- Running: 1ns Molecular dynamics Equilibration')
        fu.create_dir(prop['step16_mdeq']['path'])
        mdrun.Mdrun(properties=prop['step16_mdeq'], **paths['step16_mdeq']).launch()

        out_log.info('step17: rmsd ----- Computing RMSD')
        fu.create_dir(prop['step17_rmsd']['path'])
        rms.Rms(properties=prop['step17_rmsd'], **paths['step17_rmsd']).launch()
        rmsd_xvg_path_dict[mut] = paths['step17_rmsd']['output_xvg_path']

        out_log.info( '***************************************************************')
        out_log.info( '')

    out_log.info('step18: gnuplot ----- Creating RMSD plot')
    fu.create_dir(prop_glob['step18_gnuplot']['path'])
    gnuplot.Gnuplot(input_xvg_path_dict=rmsd_xvg_path_dict, properties=prop_glob['step18_gnuplot'], **paths_glob['step18_gnuplot']).launch()

    elapsed_time = time.time() - start_time
    out_log.info('')
    out_log.info('***********************************')
    out_log.info('Execution sucessful: ')
    out_log.info('Workflow_path: '+workflow_path)
    out_log.info('Config File: '+yaml_path)
    out_log.info('System: '+system)
    if len(sys.argv) >= 4:
        out_log.info('Nodes: '+sys.argv[3])
    out_log.info('Elapsed time: '+str(elapsed_time)+' seconds')
    out_log.info('***********************************')

if __name__ == '__main__':
    main()
