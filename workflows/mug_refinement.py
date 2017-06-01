"""
Gromacs full setup from a PDB code
"""


import os
import sys
import time
import shutil
from os.path import join as opj
from command_wrapper import cmd_wrapper

try:
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
except ImportError:
    from pymdsetup.tools import file_utils as fu
    from pymdsetup.configuration import settings
    from pymdsetup.gromacs_wrapper import pdb2gmx
    from pymdsetup.gromacs_wrapper import editconf
    from pymdsetup.gromacs_wrapper import solvate
    from pymdsetup.gromacs_wrapper import grompp
    from pymdsetup.gromacs_wrapper import genion
    from pymdsetup.gromacs_wrapper import mdrun
    from pymdsetup.gromacs_wrapper import rms
    from pymdsetup.mmb_api import pdb
    from pymdsetup.mmb_api import uniprot
    from pymdsetup.scwrl_wrapper import scwrl
    from pymdsetup.gnuplot_wrapper import gnuplot


def main():
    start_time = time.time()
    sys_paths = 'open_nebula'
    structure_pdb_path = sys.argv[1]
    root_dir = os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))
    conf_file_path = os.path.join(root_dir, 'conf_test.yaml')
    conf = settings.YamlReader(yaml_path=(conf_file_path))
    prop = conf.properties
    mdp_dir = prop[sys_paths]['mdp_path']
    gmx_path = prop[sys_paths]['gmx_path']
    scwrl_path = prop[sys_paths]['scwrl4_path']
    gnuplot_path = prop[sys_paths]['gnuplot_path']
    input_pdb_code = prop['pdb_code']
    workflow_path = fu.get_workflow_path(prop[sys_paths]['workflow_path'])
    fu.create_dir(os.path.abspath(workflow_path))

    print ''
    print ''
    print '_______MUG REFINEMENT_______'
    print ''
    print ''

    print 'step:  in ------- Get PDB structure'
    p_mmbpdb = conf.step_prop('step1_mmbpdb', workflow_path)
    fu.create_dir(p_mmbpdb.path)
    mmbpdb = pdb.MmbPdb(input_pdb_code, p_mmbpdb.pdb)
    shutil.copy(structure_pdb_path, p_mmbpdb.pdb)

    print 'step:  sed ------ Replacing atom names'
    sed_path = opj(workflow_path, 'step2_sed')
    fu.create_dir(sed_path)
    cmd = ['sed', '-i', "'s/  O1P  /  OP1  /g'", p_mmbpdb.pdb]
    command = cmd_wrapper.CmdWrapper(cmd, opj(sed_path,'sed1.log'), opj(sed_path,'sed1.err'))
    command.launch()

    cmd = ['sed', '-i', "'s/  O2P  /  OP2  /g'", p_mmbpdb.pdb]
    command = cmd_wrapper.CmdWrapper(cmd, opj(sed_path,'sed2.log'), opj(sed_path,'sed2.err'))
    command.launch()


    # print 'step:  scw ------ Model mutation'
    # p_scw = conf.step_prop('step3_scw', workflow_path)
    # fu.create_change_dir(p_scw.path)
    # scw = scwrl.Scwrl4(input_pdb_path=p_mmbpdb.pdb,
    #                    output_pdb_path=p_scw.mut_pdb,
    #                    mutation=None,
    #                    error_path=p_scw.err, log_path=p_scw.out, scwrl_path=scwrl_path)
    # scw.launch()

    print 'step:  p2g ------ Create gromacs topology'
    p_p2g = conf.step_prop('step4_p2g', workflow_path)
    fu.create_change_dir(p_p2g.path)
    # p2g = pdb2gmx.Pdb2gmx512(input_structure_pdb_path=p_scw.mut_pdb,
    p2g = pdb2gmx.Pdb2gmx512(input_structure_pdb_path=p_mmbpdb.pdb,
                             output_gro_path=p_p2g.gro,
                             output_top_path=p_p2g.top,
                             output_itp_path=None,
                             output_top_tar_path=p_p2g.tar,
                             water_type=p_p2g.water_type,
                             force_field=p_p2g.force_field,
                             ignh=settings.str2bool(p_p2g.ignh),
                             gmx_path=gmx_path,
                             log_path=p_p2g.out, error_path=p_p2g.err)
    p2g.launch()

    print 'step:  ec ------- Define box dimensions'
    p_ec = conf.step_prop('step5_ec', workflow_path)
    fu.create_change_dir(p_ec.path)
    ec = editconf.Editconf512(input_gro_path=p_p2g.gro,
                              output_gro_path=p_ec.gro,
                              box_type=p_ec.box_type,
                              distance_to_molecule=float(p_ec.distance_to_molecule),
                              center_molecule=settings.str2bool(p_ec.center_molecule),
                              log_path=p_ec.out, error_path=p_ec.err, gmx_path=gmx_path,)
    ec.launch()

    print 'step:  sol ------ Fill the box with water molecules'
    p_sol = conf.step_prop('step6_sol', workflow_path)
    fu.create_change_dir(p_sol.path)
    sol = solvate.Solvate512(input_solute_gro_path=p_ec.gro,
                             output_gro_path=p_sol.gro,
                             input_top_tar_path=p_p2g.tar,
                             output_top_path=p_sol.top,
                             output_top_tar_path=p_sol.tar,
                             input_solvent_gro_path=p_sol.input_solvent_gro_path,
                             log_path=p_sol.out, error_path=p_sol.err, gmx_path=gmx_path,)
    sol.launch()

    print ('step:  gppions -- Preprocessing: '
           'Add ions to neutralice the charge')
    p_gppions = conf.step_prop('step7_gppions', workflow_path)
    fu.create_change_dir(p_gppions.path)
    gppions = grompp.Grompp512(input_mdp_path=opj(mdp_dir, prop['step7_gppions']['paths']['mdp']),
                               input_gro_path=p_sol.gro,
                               input_top_tar_path=p_sol.tar,
                               output_tpr_path=p_gppions.tpr,
                               log_path=p_gppions.out, error_path=p_gppions.err, gmx_path=gmx_path)
    gppions.launch()

    print 'step:  gio ------ Running: Add ions to neutralice the charge'
    p_gio = conf.step_prop('step8_gio', workflow_path)
    fu.create_change_dir(p_gio.path)
    gio = genion.Genion512(input_tpr_path=p_gppions.tpr,
                           output_gro_path=p_gio.gro,
                           input_top_tar_path=p_sol.tar,
                           output_top_path=p_gio.top,
                           output_top_tar_path=p_gio.tar,
                           neutral=settings.str2bool(p_gio.neutral),
                           concentration=float(p_gio.concentration),
                           log_path=p_gio.out, error_path=p_gio.err, gmx_path=gmx_path)
    gio.launch()

    print 'step:  gppmin --- Preprocessing: Energy minimization'
    p_gppmin = conf.step_prop('step9_gppmin', workflow_path)
    fu.create_change_dir(p_gppmin.path)
    gppmin = grompp.Grompp512(input_mdp_path=opj(mdp_dir, prop['step9_gppmin']['paths']['mdp']),
                              input_gro_path=p_gio.gro,
                              input_top_tar_path=p_gio.tar,
                              output_tpr_path=p_gppmin.tpr,
                              log_path=p_gppmin.out, error_path=p_gppmin.err, gmx_path=gmx_path)
    gppmin.launch()

    print 'step:  mdmin ---- Running: Energy minimization'
    p_mdmin = conf.step_prop('step10_mdmin', workflow_path)
    fu.create_change_dir(p_mdmin.path)
    mdmin = mdrun.Mdrun512(input_tpr_path=p_gppmin.tpr,
                           output_trr_path=p_mdmin.trr,
                           output_gro_path=p_mdmin.gro,
                           output_edr_path=p_mdmin.edr,
                           log_path=p_mdmin.out, error_path=p_mdmin.err, gmx_path=gmx_path)
    mdmin.launch()

    print ('step:  gppnvt --- Preprocessing: nvt '
           'constant number of molecules, volume and temp')
    p_gppnvt = conf.step_prop('step11_gppnvt', workflow_path)
    fu.create_change_dir(p_gppnvt.path)
    gppnvt = grompp.Grompp512(input_mdp_path=opj(mdp_dir, prop['step11_gppnvt']['paths']['mdp']),
                              input_gro_path=p_mdmin.gro,
                              input_top_tar_path=p_gio.tar,
                              output_tpr_path=p_gppnvt.tpr,
                              log_path=p_gppnvt.out, error_path=p_gppnvt.err, gmx_path=gmx_path)
    gppnvt.launch()

    print ('step:  mdnvt ---- Running: nvt '
           'constant number of molecules, volume and temp')
    p_mdnvt = conf.step_prop('step12_mdnvt', workflow_path)
    fu.create_change_dir(p_mdnvt.path)
    mdnvt = mdrun.Mdrun512(input_tpr_path=p_gppnvt.tpr,
                           output_trr_path=p_mdnvt.trr,
                           output_gro_path=p_mdnvt.gro,
                           output_edr_path=p_mdnvt.edr,
                           output_cpt_path=p_mdnvt.cpt,
                           log_path=p_mdnvt.out, error_path=p_mdnvt.err, gmx_path=gmx_path)
    mdnvt.launch()

    print ('step:  gppnpt --- Preprocessing: npt '
           'constant number of molecules, pressure and temp')
    p_gppnpt = conf.step_prop('step13_gppnpt', workflow_path)
    fu.create_change_dir(p_gppnpt.path)
    gppnpt = grompp.Grompp512(input_mdp_path=opj(mdp_dir, prop['step13_gppnpt']['paths']['mdp']),
                              input_gro_path=p_mdnvt.gro,
                              input_top_tar_path=p_gio.tar,
                              output_tpr_path=p_gppnpt.tpr,
                              input_cpt_path=p_mdnvt.cpt,
                              log_path=p_gppnpt.out, error_path=p_gppnpt.err, gmx_path=gmx_path)
    gppnpt.launch()

    print ('step:  mdnpt ---- Running: npt '
           'constant number of molecules, pressure and temp')
    p_mdnpt = conf.step_prop('step14_mdnpt', workflow_path)
    fu.create_change_dir(p_mdnpt.path)
    mdnpt = mdrun.Mdrun512(input_tpr_path=p_gppnpt.tpr,
                           output_trr_path=p_mdnpt.trr,
                           output_gro_path=p_mdnpt.gro,
                           output_edr_path=p_mdnpt.edr,
                           output_cpt_path=p_mdnpt.cpt,
                           log_path=p_mdnpt.out, error_path=p_mdnpt.err, gmx_path=gmx_path)
    mdnpt.launch()

    print ('step:  gppeq ---- Preprocessing:'
           ' 1ns Molecular dynamics Equilibration')
    p_gppeq = conf.step_prop('step15_gppeq', workflow_path)
    fu.create_change_dir(p_gppeq.path)
    gppeq = grompp.Grompp512(input_mdp_path=opj(mdp_dir, prop['step15_gppeq']['paths']['mdp']),
                             input_gro_path=p_mdnpt.gro,
                             input_top_tar_path=p_gio.tar,
                             output_tpr_path=p_gppeq.tpr,
                             input_cpt_path=p_mdnpt.cpt,
                             log_path=p_gppeq.out, error_path=p_gppeq.err, gmx_path=gmx_path)
    gppeq.launch()

    print ('step:  mdeq ----- Running:'
           ' 1ns Molecular dynamics Equilibration')
    p_mdeq = conf.step_prop('step16_mdeq', workflow_path)
    fu.create_change_dir(p_mdeq.path)
    mdeq = mdrun.Mdrun512(input_tpr_path=p_gppeq.tpr,
                          output_trr_path=p_mdeq.trr,
                          output_xtc_path=p_mdeq.xtc,
                          output_gro_path=p_mdeq.gro,
                          output_edr_path=p_mdeq.edr,
                          output_cpt_path=p_mdeq.cpt,
                          log_path=p_mdeq.out, error_path=p_mdeq.err, gmx_path=gmx_path)
    mdeq.launch()

    print 'step:  trjconv -- Extract last snapshot'
    fu.create_change_dir(opj(workflow_path,'step17_trjconv'))
    refined_structure = sys.argv[2]
    os.system('printf "\\"Protein\\" | \\"DNA\\" \nq\n" | '+gmx_path+' make_ndx -f '+p_mdeq.gro+' > make_ndx.out 2> make_ndx.err')

    cmd = ['echo', 'Protein_DNA', '|',
           gmx_path, "trjconv",
           "-s", p_gppeq.tpr,
           "-f", p_mdeq.xtc,
           "-o", refined_structure,
           "-n", "index.ndx",
           "-dump", '1']

    command = cmd_wrapper.CmdWrapper(cmd, 'trjconv.out', 'trjconv.err')
    command.launch()

    elapsed_time = time.time() - start_time
    print "Elapsed time: ", elapsed_time
    with open(opj(workflow_path, 'time.txt'), 'a') as time_file:
        time_file.write(str(elapsed_time))

if __name__ == '__main__':
    main()
