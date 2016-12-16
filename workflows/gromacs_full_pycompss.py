# -*- coding: utf-8 -*-
"""Gromacs full setup from a pdb
"""
import os
import sys
import shutil
from os.path import join as opj

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
    from command_wrapper import cmd_wrapper
    from dummies_pycompss.task import task
    from dummies_pycompss.parameter import *
    from dummies_pycompss.constraint import constraint
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
    from pymdsetup.command_wrapper import cmd_wrapper
    from pymdsetup.dummies_pycompss.task import task
    from pymdsetup.dummies_pycompss.constraint import constraint
    from pymdsetup.dummies_pycompss.parameter import *


def main():

    root_dir = os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))
    conf_file_path = os.path.join(root_dir, 'conf.yaml')
    conf = settings.YamlReader(yaml_path=(conf_file_path))
    prop = conf.properties
    mdp_dir = os.path.join(root_dir, 'mdp')
    gmx_path = prop['gmx_path']
    scwrl_path = prop['scwrl4_path']
    gnuplot_path = prop['gnuplot_path']
    input_pdb_code = prop['pdb_code']
    # Testing purposes: Remove last Test
    if os.path.exists(prop['workflow_path']):
        shutil.rmtree(prop['workflow_path'])
    # Create the wokflow working dir
    fu.create_change_dir(os.path.abspath(prop['workflow_path']))

    print ''
    print ''
    print '_______GROMACS FULL WORKFLOW_______'
    print ''
    print ''

    print 'step1:  mmbpdb -- Get PDB'
    print '     Selected PDB code: ' + input_pdb_code
    p_mmbpdb = conf.step_prop('step1_mmbpdb')
    fu.create_change_dir(p_mmbpdb.path)
    mmbpdb = pdb.MmbPdb(input_pdb_code, p_mmbpdb.pdb)
    mmbpdb.get_pdb()

    print 'step2:  mmbuniprot -- Get mutations'
    mmbuniprot = uniprot.MmbVariants(input_pdb_code)
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
               input_pdb_code + ' PDB variants')

    # Number of mutations to be modelled
    if prop['mutations_limit'] is None:
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
        print ''
        print '___________'
        print str(mutations_counter) + '/' + str(mutations_limit) + ' ' + mut
        print '-----------'

        print 'step3:  scw ------ Model mutation'
        p_scw = conf.step_prop('step3_scw', mut)
        scwrlPyCOMPSs(task_path=p_scw.path,
                      pdb_path=p_mmbpdb.pdb,
                      output_pdb_path=p_scw.mut_pdb,
                      mutation=mut,
                      log_path=p_scw.out,
                      error_path=p_scw.err,
                      scwrl_path=scwrl_path)

        print 'step4:  p2g ------ Create gromacs topology'
        p_p2g = conf.step_prop('step4_p2g', mut)
        fu.create_dir(p_p2g.path)
        pdb2gmxPyCOMPSs(structure_pdb_path=p_scw.mut_pdb,
                        output_path=p_p2g.gro,
                        output_top_path=p_p2g.top,
                        water_type=p_p2g.water_type,
                        force_field=p_p2g.force_field,
                        ignh=settings.str2bool(p_p2g.ignh),
                        log_path=p_p2g.out,
                        error_path=p_p2g.err,
                        gmx_path=gmx_path)

        # print 'step5:  ec ------- Define box dimensions'
        # p_ec = conf.step_prop('step5_ec', mut)
        # fu.create_dir(p_ec.path)
        # editconfPyCOMPSs(structure_gro_path=p_p2g.gro,
        #                  output_gro_path=p_ec.gro,
        #                  distance_to_molecule=float(p_ec.distance_to_molecule),
        #                  box_type=p_ec.box_type,
        #                  center_molecule=settings.str2bool(p_ec.center_molecule),
        #                  log_path=p_ec.out,
        #                  error_path=p_ec.err,
        #                  gmx_path=gmx_path)
        #
        # print 'step6:  sol ------ Fill the box with water molecules'
        # p_sol = conf.step_prop('step6_sol', mut)
        # fu.create_dir(p_sol.path)
        # solvatePyCOMPSs(p_ec.gro, p_sol.gro, p_p2g.top, p_sol.top,
        #                 log_path=p_sol.out, error_path=p_sol.err,
        #                 gmx_path=gmx_path)
        #
        # print ('step7:  gppions -- Preprocessing: '
        #        'Add ions to neutralice the charge')
        # p_gppions = conf.step_prop('step7_gppions', mut)
        # fu.create_dir(p_gppions.path)
        # dummy_cpt_path = opj(p_gppions.path,
        #                      'dummy' + str(random.randint(0, 1000000)) +
        #                      '.cpt')
        # with open(dummy_cpt_path, 'w+') as dummy_file:
        #     dummy_file.write('Useless file. Please, remove it')
        #
        # shutil.copy(opj(mdp_dir, prop['step7_gppions']['paths']['mdp']),
        #             p_gppions.mdp)
        # gromppPyCOMPSs(mdp_path=p_gppions.mdp,
        #                gro_path=p_sol.gro,
        #                top_path=p_sol.top,
        #                output_tpr_path=p_gppions.tpr,
        #                use_cpt=False,
        #                cpt_path=dummy_cpt_path,
        #                log_path=p_gppions.out,
        #                error_path=p_gppions.err,
        #                gmx_path=gmx_path)
        #
        # print 'step8:  gio -- Running: Add ions to neutralice the charge'
        # p_gio = conf.step_prop('step8_gio', mut)
        # fu.create_dir(p_gio.path)
        # genionPyCOMPSs(tpr_path=p_gppions.tpr,
        #                output_gro_path=p_gio.gro,
        #                input_top=p_sol.top,
        #                output_top=p_gio.top,
        #                replaced_group='SOL',
        #                neutral=False,
        #                concentration=0.05,
        #                seed='None',
        #                log_path=p_gio.out,
        #                error_path=p_gio.err,
        #                gmx_path=gmx_path)
        #
        # print 'step9:  gppmin --- Preprocessing: Energy minimization'
        # p_gppmin = conf.step_prop('step9_gppmin', mut)
        # fu.create_dir(p_gppmin.path)
        # dummy_cpt_path = opj(p_gppmin.path,
        #                      'dummy' + str(random.randint(0, 1000000)) +
        #                      '.cpt')
        # with open(dummy_cpt_path, 'w+') as dummy_file:
        #     dummy_file.write('Useless file. Please, remove it')
        # shutil.copy(opj(mdp_dir, prop['step9_gppmin']['paths']['mdp']),
        #             p_gppmin.mdp)
        # gromppPyCOMPSs(mdp_path=p_gppmin.mdp,
        #                gro_path=p_gio.gro,
        #                top_path=p_gio.top,
        #                output_tpr_path=p_gppmin.tpr,
        #                use_cpt=False,
        #                cpt_path=dummy_cpt_path,
        #                gmx_path=gmx_path,
        #                log_path=p_gppmin.out,
        #                error_path=p_gppmin.err)
        #
        # print 'step10: mdmin ---- Running: Energy minimization'
        # p_mdmin = conf.step_prop('step10_mdmin', mut)
        # fu.create_dir(p_mdmin.path)
        # mdrunPyCOMPSs(tpr_path=p_gppmin.tpr,
        #               output_trr_path=p_mdmin.trr,
        #               output_gro_path=p_mdmin.gro,
        #               output_edr_path=p_mdmin.edr,
        #               output_xtc_path='None',
        #               output_cpt_path='None',
        #               log_path=p_mdmin.out,
        #               error_path=p_mdmin.err,
        #               gmx_path=gmx_path)
        #
        # print ('step11: gppnvt --- Preprocessing: nvt '
        #        'constant number of molecules, volume and temp')
        # p_gppnvt = conf.step_prop('step11_gppnvt', mut)
        # fu.create_dir(p_gppnvt.path)
        # dummy_cpt_path = opj(p_gppmin.path,
        #                      'dummy' + str(random.randint(0, 1000000)) +
        #                      '.cpt')
        # with open(dummy_cpt_path, 'w+') as dummy_file:
        #     dummy_file.write('Useless file. Please, remove it')
        # shutil.copy(opj(mdp_dir, prop['step11_gppnvt']['paths']['mdp']),
        #             p_gppnvt.mdp)
        # gromppPyCOMPSs(mdp_path=p_gppnvt.mdp,
        #                gro_path=p_mdmin.gro,
        #                top_path=p_gio.top,
        #                output_tpr_path=p_gppnvt.tpr,
        #                use_cpt=False,
        #                cpt_path=dummy_cpt_path,
        #                gmx_path=gmx_path,
        #                log_path=p_gppnvt.out,
        #                error_path=p_gppnvt.err)
        #
        # print ('step12: mdnvt ---- Running: nvt '
        #        'constant number of molecules, volume and temp')
        # p_mdnvt = conf.step_prop('step12_mdnvt', mut)
        # fu.create_dir(p_mdnvt.path)
        # mdrunPyCOMPSs(tpr_path=p_gppnvt.tpr,
        #               output_trr_path=p_mdnvt.trr,
        #               output_gro_path=p_mdnvt.gro,
        #               output_edr_path=p_mdnvt.edr,
        #               output_xtc_path=p_mdnvt.xtc,
        #               output_cpt_path=p_mdnvt.cpt,
        #               log_path=p_mdnvt.out,
        #               error_path=p_mdnvt.err,
        #               gmx_path=gmx_path)
        #
        # print ('step13: gppnpt --- Preprocessing: npt '
        #        'constant number of molecules, pressure and temp')
        # p_gppnpt = conf.step_prop('step13_gppnpt', mut)
        # fu.create_dir(p_gppnpt.path)
        # shutil.copy(opj(mdp_dir, prop['step13_gppnpt']['paths']['mdp']),
        #             p_gppnpt.mdp)
        # gromppPyCOMPSs(mdp_path=p_gppnpt.mdp,
        #                gro_path=p_mdnvt.gro,
        #                top_path=p_gio.top,
        #                output_tpr_path=p_gppnpt.tpr,
        #                use_cpt=True,
        #                cpt_path=p_mdnvt.cpt,
        #                gmx_path=gmx_path,
        #                log_path=p_gppnpt.out,
        #                error_path=p_gppnpt.err)
        #
        # print ('step14: mdnpt ---- Running: npt '
        #        'constant number of molecules, pressure and temp')
        # p_mdnpt = conf.step_prop('step14_mdnpt', mut)
        # fu.create_dir(p_mdnpt.path)
        # mdrunPyCOMPSs(tpr_path=p_gppnpt.tpr,
        #               output_trr_path=p_mdnpt.trr,
        #               output_gro_path=p_mdnpt.gro,
        #               output_edr_path=p_mdnpt.edr,
        #               output_xtc_path=p_mdnpt.xtc,
        #               output_cpt_path=p_mdnpt.cpt,
        #               log_path=p_mdnpt.out,
        #               error_path=p_mdnpt.err,
        #               gmx_path=gmx_path)
        #
        # print ('step15: gppeq ---- '
        #        'Preprocessing: 1ns Molecular dynamics Equilibration')
        # p_gppeq = conf.step_prop('step15_gppeq', mut)
        # fu.create_dir(p_gppeq.path)
        # shutil.copy(opj(mdp_dir, prop['step15_gppeq']['paths']['mdp']),
        #             p_gppeq.mdp)
        # gromppPyCOMPSs(mdp_path=p_gppeq.mdp,
        #                gro_path=p_mdnpt.gro,
        #                top_path=p_gio.top,
        #                output_tpr_path=p_gppeq.tpr,
        #                use_cpt=True,
        #                cpt_path=p_mdnpt.cpt,
        #                gmx_path=gmx_path,
        #                log_path=p_gppeq.out,
        #                error_path=p_gppeq.err)
        #
        # print ('step16: mdeq ----- '
        #        'Running: 1ns Molecular dynamics Equilibration')
        # p_mdeq = conf.step_prop('step16_mdeq', mut)
        # fu.create_dir(p_mdeq.path)
        # mdrunPyCOMPSs(tpr_path=p_gppeq.tpr,
        #               output_trr_path=p_mdeq.trr,
        #               output_gro_path=p_mdeq.gro,
        #               output_edr_path=p_mdeq.edr,
        #               output_xtc_path=p_mdeq.xtc,
        #               output_cpt_path=p_mdeq.cpt,
        #               log_path=p_mdeq.out,
        #               error_path=p_mdeq.err,
        #               gmx_path=gmx_path)
        #
        # fu.rm_temp()


############################## PyCOMPSs functions #############################
@task(dependency_file_in=FILE_IN, dependency_file_out=FILE_OUT, task_path=IN,
      pdb_path=IN, output_pdb_path=IN, mutation=IN, log_path=IN, error_path=IN,
      scwrl_path=IN)
def scwrlPyCOMPSs(dependency_file_in, dependency_file_out, task_path, pdb_path,
                  output_pdb_path, mutation, log_path, error_path, scwrl_path):
    """ Launches SCWRL 4 using the PyCOMPSs library."""
    pycompss_none(locals())
    fu.create_change_dir(task_path)

    scwrl.Scwrl4(pdb_path, output_pdb_path, mutation, log_path, error_path,
                 scwrl_path).launch()

    open(dependency_file_out, 'a').close()


@task(dependency_file_in=FILE_IN, dependency_file_out=FILE_OUT, task_path=IN,
      structure_pdb_path=IN, output_path=IN, output_top_path=IN, water_type=IN,
      force_field=IN, ignh=IN, log_path=IN, error_path=IN, gmx_path=IN)
def pdb2gmxPyCOMPSs(dependency_file_in, dependency_file_out, task_path,
                    structure_pdb_path, output_path, output_top_path,
                    water_type, force_field, ignh, log_path, error_path,
                    gmx_path):
    """Launches the GROMACS pdb2gmx module using the PyCOMPSs library."""
    pycompss_none(locals())
    fu.create_change_dir(task_path)

    pdb2gmx.Pdb2gmx512(inputpdb, outputgro, output_top_path, water_type,
                       force_field, ignh, log_path, error_path,
                       gmx_path).launch()

    open(dependency_file_out, 'a').close()


@task(structure_gro_path=FILE_IN, output_gro_path=FILE_OUT,
      distance_to_molecule=IN, box_type=IN, center_molecule=IN,
      log_path=FILE_OUT, error_path=FILE_OUT, gmx_path=IN)
def editconfPyCOMPSs(structure_gro_path, output_gro_path,
                     distance_to_molecule=1.0, box_type='octahedron',
                     center_molecule=True, log_path='None', error_path='None',
                     gmx_path='None'):
    """Launches the GROMACS editconf module using the PyCOMPSs library.
    """
    inputgro = "input" + str(random.randint(0, 1000000)) + ".gro"
    os.symlink(structure_gro_path, inputgro)

    outputgro = "output" + str(random.randint(0, 1000000)) + ".gro"
    os.symlink(output_gro_path, outputgro)

    editconf.Editconf512(inputgro, outputgro, distance_to_molecule, box_type,
                         center_molecule, log_path, error_path,
                         gmx_path).launch()
    os.remove(inputgro)
    os.remove(outputgro)


# solute_structure_gro_path will keep the dependency with the previous step
# output_gro_path will set the dependency with the next step
@task(solute_structure_gro_path=FILE_IN, output_gro_path=FILE_OUT,
      input_top_path=IN, output_top_path=IN,
      solvent_structure_gro_path=IN, log_path=FILE_OUT, error_path=FILE_OUT,
      gmx_path=IN)
def solvatePyCOMPSs(solute_structure_gro_path, output_gro_path, input_top_path,
                    output_top_path, solvent_structure_gro_path="spc216.gro",
                    log_path='None', error_path='None', gmx_path='None'):
    """Launches the GROMACS solvate module using the PyCOMPSs library.

    Args:
        top (str): Path to the TOP file output from the PyCOMPSs
                   execution of pdb2gmx.
        gro (str): Path to the GRO file output from the PyCOMPSs
                   execution of pdb2gmx.
        topin (str): Path the input GROMACS TOP file.
        topout (str): Path the output GROMACS TOP file.
    """
    itp_input_path = os.path.dirname(input_top_path)
    itp_output_path = os.path.dirname(output_top_path)
    fu.copy_ext(itp_input_path, itp_output_path, 'itp')
    shutil.copy(input_top_path, output_top_path)
    # tempdir = tempfile.mkdtemp()
    # temptop = os.path.join(tempdir, "sol.top")
    # shutil.copy(output_top_path, temptop)

    inputsolutegro = "inputsolute" + str(random.randint(0, 1000000)) + ".gro"
    os.symlink(solute_structure_gro_path, inputsolutegro)

    outputgro = "output" + str(random.randint(0, 1000000)) + ".gro"
    os.symlink(output_gro_path, outputgro)

    gmx = "gmx" if gmx_path == 'None' else gmx_path
    cmd = [gmx, "solvate", "-cp", inputsolutegro,
           "-cs", solvent_structure_gro_path, "-o",
           outputgro, "-p", output_top_path]
    command = cmd_wrapper.CmdWrapper(cmd, log_path, error_path)
    command.launch()

    # shutil.copy(temptop, output_top_path)
    # shutil.rmtree(tempdir)

    os.remove(inputsolutegro)
    os.remove(outputgro)


@task(mdp_path=FILE_IN, gro_path=FILE_IN, top_path=IN,
      output_tpr_path=FILE_OUT, use_cpt=IN, cpt_path=FILE_IN,
      log_path=FILE_OUT, error_path=FILE_OUT, gmx_path=IN)
def gromppPyCOMPSs(mdp_path, gro_path, top_path, output_tpr_path,
                   use_cpt=False, cpt_path='None',
                   log_path='None',
                   error_path='None', gmx_path='None'):
    """Launches the GROMACS grompp module using the PyCOMPSs library.
    """

    inputmdp = "input" + str(random.randint(0, 1000000)) + ".mdp"
    os.symlink(mdp_path, inputmdp)

    inputgro = "input" + str(random.randint(0, 1000000)) + ".gro"
    os.symlink(gro_path, inputgro)

    outputtpr = "output" + str(random.randint(0, 1000000)) + ".tpr"
    os.symlink(output_tpr_path, outputtpr)

    if use_cpt:
        inputcpt = "input" + str(random.randint(0, 1000000)) + ".cpt"
        os.symlink(cpt_path, inputcpt)
    else:
        inputcpt = 'None'

    grompp.Grompp512(inputmdp, inputgro, top_path, outputtpr, inputcpt,
                     log_path, error_path, gmx_path).launch()

    os.remove(inputmdp)
    os.remove(inputgro)
    os.remove(outputtpr)
    if use_cpt:
        os.remove(inputcpt)


@task(tpr_path=FILE_IN, output_gro_path=FILE_OUT, input_top=IN,
      output_top=IN, replaced_group=IN,
      neutral=IN, concentration=IN, seed=IN, log_path=FILE_OUT,
      error_path=FILE_OUT, gmx_path=IN)
def genionPyCOMPSs(tpr_path, output_gro_path, input_top, output_top,
                   replaced_group="SOL", neutral=False,
                   concentration=0.05, seed='None', log_path='None',
                   error_path='None', gmx_path='None'):
    """Launches the GROMACS genion module using the PyCOMPSs library.
    """
    itp_input_path = os.path.dirname(input_top)
    itp_output_path = os.path.dirname(output_top)
    fu.copy_ext(itp_input_path, itp_output_path, 'itp')
    shutil.copy(input_top, output_top)
    # tempdir = tempfile.mkdtemp()
    # temptop = os.path.join(tempdir, "gio.top")
    # shutil.copy(output_top, temptop)

    inputtpr = "input" + str(random.randint(0, 1000000)) + ".tpr"
    os.symlink(tpr_path, inputtpr)

    outputgro = "output" + str(random.randint(0, 1000000)) + ".gro"
    os.symlink(output_gro_path, outputgro)

    gmx = "gmx" if gmx_path == 'None' else gmx_path
    cmd = ["echo", replaced_group, "|", gmx, "genion", "-s",
           inputtpr, "-o", outputgro,
           "-p", output_top]

    if neutral:
        cmd.append('-neutral')
    elif concentration:
        cmd.append('-conc')
        cmd.append(str(concentration))

    if seed != 'None':
        cmd.append('-seed')
        cmd.append(str(seed))

    command = cmd_wrapper.CmdWrapper(cmd, log_path, error_path)
    command.launch()
    # shutil.copy(temptop, output_top)
    # shutil.rmtree(tempdir)
    os.remove(inputtpr)
    os.remove(outputgro)


@task(tpr_path=FILE_IN, output_trr_path=FILE_OUT, output_gro_path=FILE_OUT,
      output_edr_path=FILE_OUT, output_xtc_path=IN, output_cpt_path=IN,
      log_path=FILE_OUT, error_path=FILE_OUT, gmx_path=IN)
def mdrunPyCOMPSs(tpr_path, output_trr_path, output_gro_path, output_edr_path,
                  output_xtc_path, output_cpt_path,
                  log_path='None', error_path='None', gmx_path='None'):
    """Launches the GROMACS mdrun module using the PyCOMPSs library.
    Args:
        tpr (str): Path to the portable binary run input file TPR.
    """
    inputtpr = "input" + str(random.randint(0, 1000000)) + ".tpr"
    os.symlink(tpr_path, inputtpr)

    outputtrr = "output" + str(random.randint(0, 1000000)) + ".trr"
    os.symlink(output_trr_path, outputtrr)

    outputgro = "output" + str(random.randint(0, 1000000)) + ".gro"
    os.symlink(output_gro_path, outputgro)

    outputedr = "output" + str(random.randint(0, 1000000)) + ".edr"
    os.symlink(output_edr_path, outputedr)

    # outputxtc = "output" + str(random.randint(0,1000000)) +".xtc"
    # os.symlink(output_xtc_path, outputxtc)
    #
    # outputcpt = "output" + str(random.randint(0,1000000)) +".cpt"
    # os.symlink(output_cpt_path, outputcpt)

    mdrun.Mdrun512(tpr_path=inputtpr,
                   output_trr_path=outputtrr,
                   output_gro_path=outputgro,
                   output_edr_path=outputedr,
                   output_xtc_path=output_xtc_path,
                   output_cpt_path=output_cpt_path,
                   log_path=log_path,
                   error_path=error_path,
                   gmx_path=gmx_path).launch()


# This funcstion is here because this pycompss version still does not support
# the None value in the function task decorator
def pycompss_none(local_arg_dict):
    for key, value in local_arg_dict.iteritems():
        if isinstance(value, basestring) and value.lower() == 'none':
            local_arg_dict[key] = None
##############################################################################


if __name__ == '__main__':
    main()
