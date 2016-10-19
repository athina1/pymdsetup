# -*- coding: utf-8 -*-
"""Gromacs full setup from a pdb


"""
import os
import shutil
import tempfile
from os.path import join as opj
import random

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
except ImportError:
    from pymdsetup.tools import file_utils as fu
    from pymdsetup.configuration import settings
    from pymdsetup.gromacs_wrapper import pdb2gmx
    from pymdsetup.gromacs_wrapper import grompp
    from pymdsetup.scwrl_wrapper import scwrl
    from pymdsetup.gromacs_wrapper import solvate
    from pymdsetup.gromacs_wrapper import editconf
    from pymdsetup.gromacs_wrapper import genion
    from pymdsetup.gromacs_wrapper import mdrun
    from pymdsetup.mmb_api import pdb
    from pymdsetup.mmb_api import uniprot
    from pymdsetup.gromacs_wrapper import rms


def main():
    # COMPSS VM
    conf = settings.YamlReader(yaml_path=('/home/compss'
                                          '/pymdsetup/workflows/conf.yaml'))

    prop = conf.properties
    mdp_dir = prop['mdp_path']
    gmx_path = prop['gmx_path']
    scwrl_path = prop['scwrl4_path']
    input_pdb_code = prop['pdb_code']
    fu.create_dir(os.path.abspath(prop['workflow_path']))

    # Testing purposes: Remove last Test
    shutil.rmtree(prop['workflow_path'])

    print ''
    print ''
    print '_______GROMACS FULL WORKFLOW_______'
    print ''
    print ''
    print 'step1:  mmbpdb -- Get PDB'
    print '     Selected PDB code: ' + input_pdb_code
    p_mmbpdb = conf.step_prop('step1_mmbpdb')
    fu.create_dir(p_mmbpdb.path)
    mmbpdb = pdb.MmbPdb(input_pdb_code, p_mmbpdb.pdb)
    mmbpdb.get_pdb()

    print 'step2:  mmbuniprot -- Get mutations'
    mmbuniprot = uniprot.MmbVariants(input_pdb_code)

    #if it is a Demo.
    if mmbuniprot.get_uniprot() != 'P00698':
        mutations = mmbuniprot.get_pdb_variants()
        print '     Uniprot code: ' + mmbuniprot.get_uniprot()

        if mutations is None or len(mutations) == 0:
            print (prop['pdb_code'] +
                   " " + mmbuniprot.get_uniprot() + ": No variants")
            return
        else:
            print ('     Found ' + str(len(mmbuniprot.get_variants())) +
                   ' uniprot variants')
            print ('     Mapped to ' + str(len(mutations)) + ' ' +
                   input_pdb_code + ' PDB variants')

    # Demo purposes
    ########################################################################
    else:
            mutations = ['A.VAL2GLY']
            #mutations = ['A.VAL2GLY', 'A.GLY4VAL', 'A.CYS6VAL']

    ########################################################################

    for mut in mutations:
        print ''
        print '___________'
        print mut
        print '-----------'
        print 'step3:  scw ------ Model mutation'
        p_scw = conf.step_prop('step3_scw', mut)
        fu.create_dir(p_scw.path)
        scwrl.scwrlPyCOMPSs(pdb_path=p_mmbpdb.pdb,
                             output_pdb_path=p_scw.mut_pdb,
                             mutation=mut,
                             log_path=p_scw.out,
                             error_path=p_scw.err,
                             scwrl_path=scwrl_path)

        print 'step4:  p2g ------ Create gromacs topology'
        p_p2g = conf.step_prop('step4_p2g', mut)
        fu.create_dir(p_p2g.path)
        pdb2gmx.pdb2gmxPyCOMPSs(structure_pdb_path=p_scw.mut_pdb,
                               output_path=p_p2g.gro,
                               output_top_path=p_p2g.top,
                               water_type=p_p2g.water_type,
                               force_field=p_p2g.force_field,
                               ignh=settings.str2bool(p_p2g.ignh),
                               log_path=p_p2g.out,
                               error_path=p_p2g.err,
                               gmx_path=gmx_path)

        print 'step5:  ec ------- Define box dimensions'
        p_ec = conf.step_prop('step5_ec', mut)
        fu.create_dir(p_ec.path)
        editconf.editconfPyCOMPSs(structure_gro_path=p_p2g.gro,
                                output_gro_path=p_ec.gro,
                                distance_to_molecule=float(p_ec.distance_to_molecule),
                                box_type=p_ec.box_type,
                                center_molecule=settings.str2bool(p_ec.center_molecule),
                                log_path=p_ec.out,
                                error_path=p_ec.err,
                                gmx_path=gmx_path)

        print 'step6:  sol ------ Fill the box with water molecules'
        p_sol = conf.step_prop('step6_sol', mut)
        fu.create_dir(p_sol.path)
        solvate.solvatePyCOMPSs(p_ec.gro, p_sol.gro, p_p2g.top, p_sol.top,
                               log_path=p_sol.out, error_path=p_sol.err,
                               gmx_path=gmx_path)

        print ('step7:  gppions -- Preprocessing: '
               'Add ions to neutralice the charge')
        p_gppions = conf.step_prop('step7_gppions', mut)
        fu.create_dir(p_gppions.path)
        dummy_cpt_path = opj(p_gppions.path,
                             'dummy' + str(random.randint(0,1000000)) + '.cpt')
        with open(dummy_cpt_path, 'w+') as dummy_file:
            dummy_file.write('Useless file. Please, remove it')

        shutil.copy(opj(mdp_dir, prop['step7_gppions']['paths']['mdp']), p_gppions.mdp)
        grompp.gromppPyCOMPSs(mdp_path=p_gppions.mdp,
                              gro_path=p_sol.gro,
                              top_path=p_sol.top,
                              output_tpr_path=p_gppions.tpr,
                              use_cpt=False,
                              cpt_path=dummy_cpt_path,
                              log_path=p_gppions.out,
                              error_path=p_gppions.err,
                              gmx_path=gmx_path,
                              mdp_dir=mdp_dir)

        print 'step8:  gio -- Running: Add ions to neutralice the charge'
        p_gio = conf.step_prop('step8_gio', mut)
        fu.create_dir(p_gio.path)
        genion.genionPyCOMPSs(tpr_path=p_gppions.tpr,
                              output_gro_path=p_gio.gro,
                              input_top=p_sol.top,
                              output_top=p_gio.top,
                              itp_path=p_p2g.path,
                              curr_path=p_gio.path,
                              replaced_group='SOL',
                              neutral=False,
                              concentration=0.05,
                              seed='None',
                              log_path=p_gio.out,
                              error_path=p_gio.err,
                              gmx_path=gmx_path)

        print 'step9:  gppmin --- Preprocessing: Energy minimization'
        p_gppmin = conf.step_prop('step9_gppmin', mut)
        fu.create_dir(p_gppmin.path)
        dummy_cpt_path = opj(p_gppmin.path,
                             'dummy' + str(random.randint(0,1000000)) + '.cpt')
        with open(dummy_cpt_path, 'w+') as dummy_file:
            dummy_file.write('Useless file. Please, remove it')
        shutil.copy(opj(mdp_dir, prop['step9_gppmin']['paths']['mdp']), p_gppmin.mdp)
        grompp.gromppPyCOMPSs(mdp_path=p_gppmin.mdp,
                              gro_path=p_gio.gro,
                              top_path=p_gio.top,
                              output_tpr_path=p_gppmin.tpr,
                              use_cpt=False,
                              cpt_path=dummy_cpt_path,
                              gmx_path=gmx_path,
                              log_path=p_gppmin.out,
                              error_path=p_gppmin.err,
                              mdp_dir=mdp_dir)

        print 'step10: mdmin ---- Running: Energy minimization'
        p_mdmin = conf.step_prop('step10_mdmin', mut)
        fu.create_dir(p_mdmin.path)
        mdrun.mdrunPyCOMPSs(tpr_path=p_gppmin.tpr,
                             output_trr_path=p_mdmin.trr,
                             output_gro_path=p_mdmin.gro,
                             output_edr_path=p_mdmin.edr,
                             output_xtc_path='None',
                             output_cpt_path='None',
                             log_path=p_mdmin.out,
                             error_path=p_mdmin.err,
                             gmx_path=gmx_path)

        print ('step11: gppnvt --- Preprocessing: nvt '
               'constant number of molecules, volume and temp')
        p_gppnvt = conf.step_prop('step11_gppnvt', mut)
        fu.create_dir(p_gppnvt.path)
        dummy_cpt_path = opj(p_gppmin.path,
                             'dummy' + str(random.randint(0,1000000)) + '.cpt')
        with open(dummy_cpt_path, 'w+') as dummy_file:
            dummy_file.write('Useless file. Please, remove it')
        shutil.copy(opj(mdp_dir, prop['step11_gppnvt']['paths']['mdp']), p_gppnvt.mdp)
        grompp.gromppPyCOMPSs(mdp_path=p_gppnvt.mdp,
                              gro_path=p_mdmin.gro,
                              top_path=p_gio.top,
                              output_tpr_path=p_gppnvt.tpr,
                              use_cpt=False,
                              cpt_path=dummy_cpt_path,
                              gmx_path=gmx_path,
                              log_path=p_gppnvt.out,
                              error_path=p_gppnvt.err,
                              mdp_dir=mdp_dir)


        print ('step12: mdnvt ---- Running: nvt '
               'constant number of molecules, volume and temp')
        p_mdnvt = conf.step_prop('step12_mdnvt', mut)
        fu.create_dir(p_mdnvt.path)
        mdrun.mdrunPyCOMPSs(tpr_path=p_gppnvt.tpr,
                             output_trr_path=p_mdnvt.trr,
                             output_gro_path=p_mdnvt.gro,
                             output_edr_path=p_mdnvt.edr,
                             output_xtc_path=p_mdnvt.xtc,
                             output_cpt_path=p_mdnvt.cpt,
                             log_path=p_mdnvt.out,
                             error_path=p_mdnvt.err,
                             gmx_path=gmx_path)

        print ('step13: gppnpt --- Preprocessing: npt '
               'constant number of molecules, pressure and temp')
        p_gppnpt = conf.step_prop('step13_gppnpt', mut)
        fu.create_dir(p_gppnpt.path)
        shutil.copy(opj(mdp_dir, prop['step13_gppnpt']['paths']['mdp']), p_gppnpt.mdp)
        grompp.gromppPyCOMPSs(mdp_path=p_gppnpt.mdp,
                              gro_path=p_mdnvt.gro,
                              top_path=p_gio.top,
                              output_tpr_path=p_gppnpt.tpr,
                              use_cpt=True,
                              cpt_path=p_mdnvt.cpt,
                              gmx_path=gmx_path,
                              log_path=p_gppnpt.out,
                              error_path=p_gppnpt.err,
                              mdp_dir=mdp_dir)

        print ('step14: mdnpt ---- Running: npt '
               'constant number of molecules, pressure and temp')
        p_mdnpt = conf.step_prop('step14_mdnpt', mut)
        fu.create_dir(p_mdnpt.path)
        mdrun.mdrunPyCOMPSs(tpr_path=p_gppnpt.tpr,
                             output_trr_path=p_mdnpt.trr,
                             output_gro_path=p_mdnpt.gro,
                             output_edr_path=p_mdnpt.edr,
                             output_xtc_path=p_mdnpt.xtc,
                             output_cpt_path=p_mdnpt.cpt,
                             log_path=p_mdnpt.out,
                             error_path=p_mdnpt.err,
                             gmx_path=gmx_path)

        print ('step15: gppeq ---- '
               'Preprocessing: 1ns Molecular dynamics Equilibration')
        p_gppeq = conf.step_prop('step15_gppeq', mut)
        fu.create_dir(p_gppeq.path)
        shutil.copy(opj(mdp_dir, prop['step15_gppeq']['paths']['mdp']), p_gppeq.mdp)
        grompp.gromppPyCOMPSs(mdp_path=p_gppeq.mdp,
                              gro_path=p_mdnpt.gro,
                              top_path=p_gio.top,
                              output_tpr_path=p_gppeq.tpr,
                              use_cpt=True,
                              cpt_path=p_mdnpt.cpt,
                              gmx_path=gmx_path,
                              log_path=p_gppeq.out,
                              error_path=p_gppeq.err,
                              mdp_dir=mdp_dir)

        print ('step16: mdeq ----- '
               'Running: 1ns Molecular dynamics Equilibration')
        p_mdeq = conf.step_prop('step16_mdeq', mut)
        fu.create_dir(p_mdeq.path)
        mdrun.mdrunPyCOMPSs(tpr_path=p_gppeq.tpr,
                             output_trr_path=p_mdeq.trr,
                             output_gro_path=p_mdeq.gro,
                             output_edr_path=p_mdeq.edr,
                             output_xtc_path=p_mdeq.xtc,
                             output_cpt_path=p_mdeq.cpt,
                             log_path=p_mdeq.out,
                             error_path=p_mdeq.err,
                             gmx_path=gmx_path)

        fu.rm_temp()

if __name__ == '__main__':
    main()
