import os
import sys
import time
import tools.file_utils as fu
import configuration.settings as settings
import gromacs_wrapper.pdb2gmx as pdb2gmx
import gromacs_wrapper.grompp as grompp
import scwrl_wrapper.scwrl as scwrl
import gromacs_wrapper.solvate as solvate
import gromacs_wrapper.editconf as editconf
import gromacs_wrapper.genion as genion
import gromacs_wrapper.mdrun as mdrun
import gromacs_wrapper.make_ndx as make_ndx
import gromacs_wrapper.genrestr as genrestr
import mmb_api.pdb as pdb
import mmb_api.uniprot as uniprot
import gromacs_wrapper.rms as rms
import gnuplot_wrapper.gnuplot as gnuplot
import gromacs_extra.ndx2resttop as ndx2resttop
from pycompss.api.parameter import *
from pycompss.api.task import task
from pycompss.api.constraint import constraint

def main():
    from pycompss.api.api import compss_open
    start_time = time.time()
    yaml_path=sys.argv[1]
    system=sys.argv[2]
    n_mutations=sys.argv[3]

    conf = settings.YamlReader(yaml_path, system)
    workflow_path = conf.properties[system]['workflow_path']
    fu.create_dir(os.path.abspath(workflow_path))
    out_log, _ = fu.get_logs(path=workflow_path, console=True, level='DEBUG')
    paths_glob = conf.get_paths_dic()
    prop_glob = conf.get_prop_dic()

    out_log.info('')
    out_log.info('_______GROMACS FULL WORKFLOW_______')
    out_log.info('')

    out_log.info("Command Executed:")
    out_log.info(" ".join(sys.argv))
    out_log.info('Workflow_path: '+workflow_path)
    out_log.info('Config File: '+yaml_path)
    out_log.info('System: '+system)
    out_log.info('Mutations limit: '+n_mutations)
    if len(sys.argv) >= 5:
        out_log.info('Nodes: '+sys.argv[4])

    out_log.info('')
    out_log.info( 'step1:  mmbpdb -- Get PDB')
    structure = conf.properties[system].get('initial_structure_pdb_path', None)
    if structure is None or not os.path.isfile(structure):
        out_log.info( 22*' '+'Selected PDB code: ' + prop_glob['step1_mmbpdb']['pdb_code'])
        fu.create_dir(prop_glob['step1_mmbpdb']['path'])
        pdb.MmbPdb().get_pdb(prop_glob['step1_mmbpdb']['pdb_code'], paths_glob['step1_mmbpdb']['output_pdb_path'])
        structure = paths_glob['step1_mmbpdb']['output_pdb_path']
    else:
        out_log.info( 22*' '+'Selected PDB structure: ' + structure)

    out_log.info( 'step2:  mmbuniprot -- Get mutations')
    mutations = conf.properties.get('input_mapped_mutations_list', None)
    if mutations is None or len(mutations) < 7:
        mmbuniprot = uniprot.MmbVariants(prop_glob['step1_mmbpdb']['pdb_code'])
        mutations = mmbuniprot.get_pdb_variants()
        if mutations is None or len(mutations) == 0:
            return
        else:
            out_log.info( 22*' '+'Number of obtained mutations: ' + str(len(mutations)))
    else:
        mutations = [m.strip() for m in conf.properties.get('input_mapped_mutations_list').split(',')]
        out_log.info( 22*' '+'Number of mutations in list: ' + str(len(mutations)))

    mutations_limit = min(len(mutations), int(n_mutations))
    out_log.info('')
    out_log.info('Number of mutations to be modelled: ' + str(mutations_limit))

    rms_list = []
    mutations_counter = 0
    for mut in mutations:
        if mutations_counter == mutations_limit: break
        mutations_counter += 1
        mut = mut if not mut.startswith('*') else mut.replace('*', 'ALL')
        paths = conf.get_paths_dic(mut)
        prop = conf.get_prop_dic(mut)

        out_log.info('')
        out_log.info('-------------------------')
        out_log.info(str(mutations_counter) + '/' + str(mutations_limit) + ' ' + mut)
        out_log.info('-------------------------')
        out_log.info('')

        out_log.info('step3: scw ---------- Model mutation')
        fu.create_dir(prop['step3_scw']['path'])
        paths['step3_scw']['input_pdb_path']=structure
        out_log.debug('Paths:\n'+str(paths['step3_scw'])+'\nProperties:\n'+str(prop['step3_scw'])+'\n')
        scwrl_pc(properties=prop['step3_scw'], **paths['step3_scw'])

        out_log.info('step4: p2g ---------- Create gromacs topology')
        fu.create_dir(prop['step4_p2g']['path'])
        out_log.debug('Paths:\n'+str(paths['step4_p2g'])+'\nProperties:\n'+str(prop['step4_p2g'])+'\n')
        pdb2gmx_pc(properties=prop['step4_p2g'], **paths['step4_p2g'])

        out_log.info('step5: ec ----------- Define box dimensions')
        fu.create_dir(prop['step5_ec']['path'])
        out_log.debug('Paths:\n'+str(paths['step5_ec'])+'\nProperties:\n'+str(prop['step5_ec'])+'\n')
        editconf_pc(properties=prop['step5_ec'], **paths['step5_ec'])

        out_log.info('step6: sol ---------- Fill the box with water molecules')
        fu.create_dir(prop['step6_sol']['path'])
        out_log.debug('Paths:\n'+str(paths['step6_sol'])+'\nProperties:\n'+str(prop['step6_sol'])+'\n')
        solvate_pc(properties=prop['step6_sol'], **paths['step6_sol'])

        out_log.info('step7: gppions ------ Preprocessing: Adding monoatomic ions')
        fu.create_dir(prop['step7_gppions']['path'])
        out_log.debug('Paths:\n'+str(paths['step7_gppions'])+'\nProperties:\n'+str(prop['step7_gppions'])+'\n')
        grompp_pc(properties=prop['step7_gppions'], **paths['step7_gppions'])

        out_log.info('step8: gio ---------- Running: Adding monoatomic ions')
        fu.create_dir(prop['step8_gio']['path'])
        out_log.debug('Paths:\n'+str(paths['step8_gio'])+'\nProperties:\n'+str(prop['step8_gio'])+'\n')
        genion_pc(properties=prop['step8_gio'], **paths['step8_gio'])

        out_log.info('Step9: gppndx ------- Preprocessing index creation')
        fu.create_dir(prop['step9_gppndx']['path'])
        out_log.debug('Paths:\n'+str(paths['step9_gppndx'])+'\nProperties:\n'+str(prop['step9_gppndx'])+'\n')
        grompp_pc(properties=prop['step9_gppndx'], **paths['step9_gppndx'])

        out_log.info('Step10: make_ndx ---- Create restrain index')
        fu.create_dir(prop['step10_make_ndx']['path'])
        out_log.debug('Paths:\n'+str(paths['step10_make_ndx'])+'\nProperties:\n'+str(prop['step10_make_ndx'])+'\n')
        make_ndx_pc(properties=prop['step10_make_ndx'], **paths['step10_make_ndx'])

        out_log.info('Step11: ndx2resttop - Create restrain topology')
        fu.create_dir(prop['step11_ndx2resttop']['path'])
        out_log.debug('Paths:\n'+str(paths['step11_ndx2resttop'])+'\nProperties:\n'+str(prop['step11_ndx2resttop'])+'\n')
        ndx2resttop_pc(properties=prop['step11_ndx2resttop'], **paths['step11_ndx2resttop'])

        out_log.info('step12: gppresmin --- Preprocessing: Mutated residue minimization')
        fu.create_dir(prop['step12_gppresmin']['path'])
        out_log.debug('Paths:\n'+str(paths['step12_gppresmin'])+'\nProperties:\n'+str(prop['step12_gppresmin'])+'\n')
        grompp_pc(properties=prop['step12_gppresmin'], **paths['step12_gppresmin'])

        out_log.info('step13: mdresmin ---- Running: Mutated residue minimization')
        fu.create_dir(prop['step13_mdresmin']['path'])
        out_log.debug('Paths:\n'+str(paths['step13_mdresmin'])+'\nProperties:\n'+str(prop['step13_mdresmin'])+'\n')
        mdrun_pc(properties=prop['step13_mdresmin'], **paths['step13_mdresmin'])

        out_log.info('Step14: ndx2resttop - Create restrain topology')
        fu.create_dir(prop['step14_ndx2resttop']['path'])
        out_log.debug('Paths:\n'+str(paths['step14_ndx2resttop'])+'\nProperties:\n'+str(prop['step14_ndx2resttop'])+'\n')
        ndx2resttop_pc(properties=prop['step14_ndx2resttop'], **paths['step14_ndx2resttop'])

        out_log.info('step15: gppmin ------ Preprocessing: minimization')
        fu.create_dir(prop['step15_gppmin']['path'])
        out_log.debug('Paths:\n'+str(paths['step15_gppmin'])+'\nProperties:\n'+str(prop['step15_gppmin'])+'\n')
        grompp_pc(properties=prop['step15_gppmin'], **paths['step15_gppmin'])

        out_log.info('step16: mdmin ------- Running: minimization')
        fu.create_dir(prop['step16_mdmin']['path'])
        out_log.debug('Paths:\n'+str(paths['step16_mdmin'])+'\nProperties:\n'+str(prop['step16_mdmin'])+'\n')
        mdrun_pc(properties=prop['step16_mdmin'], **paths['step16_mdmin'])

        out_log.info('Step17: ndx2resttop - Create restrain topology')
        fu.create_dir(prop['step17_ndx2resttop']['path'])
        out_log.debug('Paths:\n'+str(paths['step17_ndx2resttop'])+'\nProperties:\n'+str(prop['step17_ndx2resttop'])+'\n')
        ndx2resttop_pc(properties=prop['step17_ndx2resttop'], **paths['step17_ndx2resttop'])

        out_log.info('step18: gppsa ------- Preprocessing: simulated annealing')
        fu.create_dir(prop['step18_gppsa']['path'])
        out_log.debug('Paths:\n'+str(paths['step18_gppsa'])+'\nProperties:\n'+str(prop['step18_gppsa'])+'\n')
        grompp_pc(properties=prop['step18_gppsa'], **paths['step18_gppsa'])

        out_log.info('step19: mdsa -------- Running: simulated annealing')
        fu.create_dir(prop['step19_mdsa']['path'])
        out_log.debug('Paths:\n'+str(paths['step19_mdsa'])+'\nProperties:\n'+str(prop['step19_mdsa'])+'\n')
        mdrun_pc_cpt(properties=prop['step19_mdsa'], **paths['step19_mdsa'])

        out_log.info('step20: gppnvt_1000 - Preprocessing: nvt constant number of molecules, volume and temp')
        fu.create_dir(prop['step20_gppnvt_1000']['path'])
        out_log.debug('Paths:\n'+str(paths['step20_gppnvt_1000'])+'\nProperties:\n'+str(prop['step20_gppnvt_1000'])+'\n')
        grompp_pc_cpt(properties=prop['step20_gppnvt_1000'], **paths['step20_gppnvt_1000'])

        out_log.info('step21: mdnvt_1000 -- Running: nvt constant number of molecules, volume and temp')
        fu.create_dir(prop['step21_mdnvt_1000']['path'])
        out_log.debug('Paths:\n'+str(paths['step21_mdnvt_1000'])+'\nProperties:\n'+str(prop['step21_mdnvt_1000'])+'\n')
        mdrun_pc_cpt(properties=prop['step21_mdnvt_1000'], **paths['step21_mdnvt_1000'])

        out_log.info('Step22: ndx2resttop - Create restrain topology')
        fu.create_dir(prop['step22_ndx2resttop']['path'])
        out_log.debug('Paths:\n'+str(paths['step22_ndx2resttop'])+'\nProperties:\n'+str(prop['step22_ndx2resttop'])+'\n')
        ndx2resttop_pc(properties=prop['step22_ndx2resttop'], **paths['step22_ndx2resttop'])

        out_log.info('step23: gppnvt_800 -- Preprocessing: nvt constant number of molecules, volume and temp')
        fu.create_dir(prop['step23_gppnvt_800']['path'])
        out_log.debug('Paths:\n'+str(paths['step23_gppnvt_800'])+'\nProperties:\n'+str(prop['step23_gppnvt_800'])+'\n')
        grompp_pc_cpt(properties=prop['step23_gppnvt_800'], **paths['step23_gppnvt_800'])

        out_log.info('step24: mdnvt_800 --- Running: nvt constant number of molecules, volume and temp')
        fu.create_dir(prop['step24_mdnvt_800']['path'])
        out_log.debug('Paths:\n'+str(paths['step24_mdnvt_800'])+'\nProperties:\n'+str(prop['step24_mdnvt_800'])+'\n')
        mdrun_pc_cpt(properties=prop['step24_mdnvt_800'], **paths['step24_mdnvt_800'])

        out_log.info('Step25: ndx2resttop - Create restrain topology')
        fu.create_dir(prop['step25_ndx2resttop']['path'])
        out_log.debug('Paths:\n'+str(paths['step25_ndx2resttop'])+'\nProperties:\n'+str(prop['step25_ndx2resttop'])+'\n')
        ndx2resttop_pc(properties=prop['step25_ndx2resttop'], **paths['step25_ndx2resttop'])

        out_log.info('step26: gppnpt_500 -- Preprocessing: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step26_gppnpt_500']['path'])
        out_log.debug('Paths:\n'+str(paths['step26_gppnpt_500'])+'\nProperties:\n'+str(prop['step26_gppnpt_500'])+'\n')
        grompp_pc_cpt(properties=prop['step26_gppnpt_500'], **paths['step26_gppnpt_500'])

        out_log.info('step27: mdnpt_500 --- Running: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step27_mdnpt_500']['path'])
        out_log.debug('Paths:\n'+str(paths['step27_mdnpt_500'])+'\nProperties:\n'+str(prop['step27_mdnpt_500'])+'\n')
        mdrun_pc_cpt(properties=prop['step27_mdnpt_500'], **paths['step27_mdnpt_500'])

        out_log.info('Step28: ndx2resttop - Create restrain topology')
        fu.create_dir(prop['step28_ndx2resttop']['path'])
        out_log.debug('Paths:\n'+str(paths['step28_ndx2resttop'])+'\nProperties:\n'+str(prop['step28_ndx2resttop'])+'\n')
        ndx2resttop_pc(properties=prop['step28_ndx2resttop'], **paths['step28_ndx2resttop'])

        out_log.info('step29: gppnpt_300 -- Preprocessing: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step29_gppnpt_300']['path'])
        out_log.debug('Paths:\n'+str(paths['step29_gppnpt_300'])+'\nProperties:\n'+str(prop['step29_gppnpt_300'])+'\n')
        grompp_pc_cpt(properties=prop['step29_gppnpt_300'], **paths['step29_gppnpt_300'])

        out_log.info('step30: mdnpt_300 --- Running: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step30_mdnpt_300']['path'])
        out_log.debug('Paths:\n'+str(paths['step30_mdnpt_300'])+'\nProperties:\n'+str(prop['step30_mdnpt_300'])+'\n')
        mdrun_pc_cpt(properties=prop['step30_mdnpt_300'], **paths['step30_mdnpt_300'])

        out_log.info('Step31: ndx2resttop - Create restrain topology')
        fu.create_dir(prop['step31_ndx2resttop']['path'])
        out_log.debug('Paths:\n'+str(paths['step31_ndx2resttop'])+'\nProperties:\n'+str(prop['step31_ndx2resttop'])+'\n')
        ndx2resttop_pc(properties=prop['step31_ndx2resttop'], **paths['step31_ndx2resttop'])

        out_log.info('step32: gppnpt_200 -- Preprocessing: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step32_gppnpt_200']['path'])
        out_log.debug('Paths:\n'+str(paths['step32_gppnpt_200'])+'\nProperties:\n'+str(prop['step32_gppnpt_200'])+'\n')
        grompp_pc_cpt(properties=prop['step32_gppnpt_200'], **paths['step32_gppnpt_200'])

        out_log.info('step33: mdnpt_200 --- Running: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step33_mdnpt_200']['path'])
        out_log.debug('Paths:\n'+str(paths['step33_mdnpt_200'])+'\nProperties:\n'+str(prop['step33_mdnpt_200'])+'\n')
        mdrun_pc_cpt(properties=prop['step33_mdnpt_200'], **paths['step33_mdnpt_200'])

        out_log.info('Step34: ndx2resttop - Create restrain topology')
        fu.create_dir(prop['step34_ndx2resttop']['path'])
        out_log.debug('Paths:\n'+str(paths['step34_ndx2resttop'])+'\nProperties:\n'+str(prop['step34_ndx2resttop'])+'\n')
        ndx2resttop_pc(properties=prop['step34_ndx2resttop'], **paths['step34_ndx2resttop'])

        out_log.info('step35: gppnpt_100 -- Preprocessing: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step35_gppnpt_100']['path'])
        out_log.debug('Paths:\n'+str(paths['step35_gppnpt_100'])+'\nProperties:\n'+str(prop['step35_gppnpt_100'])+'\n')
        grompp_pc_cpt(properties=prop['step35_gppnpt_100'], **paths['step35_gppnpt_100'])

        out_log.info('step36: mdnpt_100 --- Running: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step36_mdnpt_100']['path'])
        out_log.debug('Paths:\n'+str(paths['step36_mdnpt_100'])+'\nProperties:\n'+str(prop['step36_mdnpt_100'])+'\n')
        mdrun_pc_cpt(properties=prop['step36_mdnpt_100'], **paths['step36_mdnpt_100'])

        out_log.info('Step37: ndx2resttop - Create restrain topology')
        fu.create_dir(prop['step37_ndx2resttop']['path'])
        out_log.debug('Paths:\n'+str(paths['step37_ndx2resttop'])+'\nProperties:\n'+str(prop['step37_ndx2resttop'])+'\n')
        ndx2resttop_pc(properties=prop['step37_ndx2resttop'], **paths['step37_ndx2resttop'])

        out_log.info('step38: gppnpt ------ Preprocessing: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step38_gppnpt']['path'])
        out_log.debug('Paths:\n'+str(paths['step38_gppnpt'])+'\nProperties:\n'+str(prop['step38_gppnpt'])+'\n')
        grompp_pc_cpt(properties=prop['step38_gppnpt'], **paths['step38_gppnpt'])

        out_log.info('step39: mdnpt ------- Running: npt constant number of molecules, pressure and temp')
        fu.create_dir(prop['step39_mdnpt']['path'])
        out_log.debug('Paths:\n'+str(paths['step39_mdnpt'])+'\nProperties:\n'+str(prop['step39_mdnpt'])+'\n')
        mdrun_pc_cpt(properties=prop['step39_mdnpt'], **paths['step39_mdnpt'])

        out_log.info('step40: gppmd ------- Preprocessing: Free Molecular dynamics')
        fu.create_dir(prop['step40_gppmd']['path'])
        out_log.debug('Paths:\n'+str(paths['step40_gppmd'])+'\nProperties:\n'+str(prop['step40_gppmd'])+'\n')
        grompp_pc_cpt(properties=prop['step40_gppmd'], **paths['step40_gppmd'])

        out_log.info('step41: md ---------- Running: Free Molecular dynamics')
        fu.create_dir(prop['step41_md']['path'])
        out_log.debug('Paths:\n'+str(paths['step41_md'])+'\nProperties:\n'+str(prop['step41_md'])+'\n')
        mdrun_pc_cpt(properties=prop['step41_md'], **paths['step41_md'])

        # out_log.info('step42: rmsd -------- Computing RMSD')
        # fu.create_dir(prop['step42_rmsd']['path'])
        # out_log.debug('Paths:')
        # out_log.debug(str(paths['step42_rmsd']))
        # out_log.debug('Properties:')
        # out_log.debug(str(prop['step42_rmsd'])+'\n')
        # rms_list.append(rms_pc(properties=prop['step42_rmsd'], **paths['step42_rmsd']))

    #     fu.remove_temp_files(['#', '.top', '.plotscript', '.edr', '.xtc', '.itp', '.top', '.log', '.pdb', '.cpt', '.mdp', '.xvg', '.seq'])
    #
    #     xvg_dict = reduce(merge_dictionaries, rms_list)
    #
    # out_log.info('')
    # out_log.info('step43: gnuplot ----- Creating RMSD plot')
    # fu.create_dir(prop_glob['step43_gnuplot']['path'])
    # output_png_path = paths_glob['step43_gnuplot']['output_png_path']
    # properties = prop_glob['step43_gnuplot']
    # gnuplot_pc(xvg_dict, output_png_path, properties)
    #
    # png = compss_open(output_png_path)
    elapsed_time = time.time() - start_time

    with open(opj(workflow_path, 'time.txt'), 'a') as time_file:
        out_log.info('')
        out_log.info('')
        out_log.info('Execution sucessful: ')
        out_log.info('  Workflow_path: '+workflow_path)
        out_log.info('  Config File: '+yaml_path)
        out_log.info('  System: '+system)
        if len(sys.argv) >= 5:
            out_log.info('  Nodes: '+sys.argv[4])
        out_log.info('')
        out_log.info('Elapsed time: '+str(elapsed_time)+' seconds')
        out_log.info('')

############################## PyCOMPSs functions #############################
#Minotauro
#computing_units = "0"
#MareNostrum4
#computing_units = "48"


@task(returns=dict)
def merge_dictionaries(a, b):
    return dict(a, **b)

@task(input_pdb_path=FILE_IN, output_pdb_path=FILE_OUT)
def scwrl_pc(input_pdb_path, output_pdb_path, properties, **kwargs):
    scwrl.Scwrl4(input_pdb_path=input_pdb_path, output_pdb_path=output_pdb_path, properties=properties, **kwargs).launch()

@task(input_structure_pdb_path=FILE_IN, output_gro_path=FILE_OUT, output_top_zip_path=FILE_OUT)
def pdb2gmx_pc(input_structure_pdb_path, output_gro_path, output_top_zip_path, properties, **kwargs):
    pdb2gmx.Pdb2gmx(input_structure_pdb_path=input_structure_pdb_path, output_gro_path=output_gro_path, output_top_zip_path=output_top_zip_path, properties=properties, **kwargs).launch()

@task(input_gro_path=FILE_IN, output_gro_path=FILE_OUT)
def editconf_pc(input_gro_path, output_gro_path, properties, **kwargs):
    editconf.Editconf(input_gro_path=input_gro_path, output_gro_path=output_gro_path, properties=properties, **kwargs).launch()

@task(input_solute_gro_path=FILE_IN, output_gro_path=FILE_OUT, input_top_zip_path=FILE_IN, output_top_zip_path=FILE_OUT)
def solvate_pc(input_solute_gro_path, output_gro_path, input_top_zip_path, output_top_zip_path, properties, **kwargs):
    solvate.Solvate(input_solute_gro_path=input_solute_gro_path, output_gro_path=output_gro_path, input_top_zip_path=input_top_zip_path, output_top_zip_path=output_top_zip_path, properties=properties, **kwargs).launch()

@task(input_gro_path=FILE_IN, input_top_zip_path=FILE_IN, output_tpr_path=FILE_OUT,  input_cpt_path=FILE_IN)
def grompp_pc_cpt(input_gro_path, input_top_zip_path, output_tpr_path, properties, input_cpt_path, **kwargs):
    grompp.Grompp(input_gro_path=input_gro_path, input_top_zip_path=input_top_zip_path, output_tpr_path=output_tpr_path, properties=properties, input_cpt_path=input_cpt_path, **kwargs).launch()

@task(input_gro_path=FILE_IN, input_top_zip_path=FILE_IN, output_tpr_path=FILE_OUT)
def grompp_pc(input_gro_path, input_top_zip_path, output_tpr_path, properties, **kwargs):
    grompp.Grompp(input_gro_path=input_gro_path, input_top_zip_path=input_top_zip_path, output_tpr_path=output_tpr_path, properties=properties, **kwargs).launch()

@task(input_tpr_path=FILE_IN, output_gro_path=FILE_OUT, input_top_zip_path=FILE_IN, output_top_zip_path=FILE_OUT)
def genion_pc(input_tpr_path, output_gro_path, input_top_zip_path, output_top_zip_path, properties, **kwargs):
    genion.Genion(input_tpr_path=input_tpr_path, output_gro_path=output_gro_path, input_top_zip_path=input_top_zip_path, output_top_zip_path=output_top_zip_path, properties=properties, **kwargs).launch()

#@constraint(ComputingUnits=computing_units)
@task(input_tpr_path=FILE_IN, output_trr_path=FILE_OUT, output_gro_path=FILE_OUT, output_cpt_path=FILE_OUT)
def mdrun_pc_cpt(input_tpr_path, output_trr_path, output_gro_path, properties, output_cpt_path, **kwargs):
    mdrun.Mdrun(input_tpr_path=input_tpr_path, output_trr_path=output_trr_path, properties=properties, output_gro_path=output_gro_path, output_cpt_path=output_cpt_path, **kwargs).launch()

#@constraint(ComputingUnits=computing_units)
@task(input_tpr_path=FILE_IN, output_trr_path=FILE_OUT, output_gro_path=FILE_OUT)
def mdrun_pc(input_tpr_path, output_trr_path, output_gro_path, properties, **kwargs):
    mdrun.Mdrun(input_tpr_path=input_tpr_path, output_trr_path=output_trr_path, properties=properties, output_gro_path=output_gro_path, **kwargs).launch()

@task(input_gro_path=FILE_IN, input_xtc_path=FILE_IN, output_xvg_path=FILE_OUT, returns=dict)
def rms_pc(input_gro_path, input_xtc_path, output_xvg_path, properties, **kwargs):
    return rms.Rms(input_gro_path=input_gro_path, input_xtc_path=input_xtc_path, output_xvg_path=output_xvg_path, properties=properties, **kwargs).launch()

@task(output_png_path=FILE_OUT)
def gnuplot_pc(input_xvg_path_dict, output_png_path, properties, **kwargs):
    gnuplot.Gnuplot(input_xvg_path_dict=input_xvg_path_dict, output_png_path=output_png_path, properties=properties, **kwargs).launch()

@task(input_ndx_path=FILE_IN, input_top_zip_path=FILE_IN, output_top_zip_path=FILE_OUT)
def ndx2resttop_pc(input_ndx_path, input_top_zip_path, output_top_zip_path, properties, **kwargs):
    ndx2resttop.Ndx2resttop(input_ndx_path=input_ndx_path, input_top_zip_path=input_top_zip_path, output_top_zip_path=output_top_zip_path, properties=properties, **kwargs).launch()

@task(input_structure_path=FILE_IN, output_ndx_path=FILE_OUT)
def make_ndx_pc(input_structure_path, output_ndx_path, properties, **kwargs):
    make_ndx.MakeNdx(input_structure_path=input_structure_path, output_ndx_path=output_ndx_path, properties=properties, **kwargs).launch()



if __name__ == '__main__':
    main()
