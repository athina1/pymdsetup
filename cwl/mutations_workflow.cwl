#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow

inputs:
  #GENERAL
  properties: File
  grompp_script: File
  mdrun_script: File
  #SCWRL
  scw_script: File
  scw_input_pdb_path: File
  scw_step: string
  # #PDB2GMX
  p2g_script: File
  p2g_step: string
  #EDITCONF
  ec_script: File
  ec_step: string
  #SOLVATE
  sol_script: File
  sol_step: string
  #GPPIONS
  gppions_step: string
  # #GENION
  gio_script: File
  gio_step: string
  #GPPMIN
  gppmin_step: string
  #MDMIN
  mdmin_step: string
  #GPPNVT
  gppnvt_step: string
  #MDNVT
  mdnvt_step: string
  #GPPNPT
  gppnpt_step: string
  #MDNPT
  mdnpt_step: string
  #GPPEQ
  gppeq_step: string
  #MDEQ
  mdeq_step: string
  #RMS
  rms_script: File
  rms_step: string
  #GNUPLOT
  gnuplot_script: File
  gnuplot_step: string

outputs:
  gnuplot_output_png_file:
     type: File
     outputSource: gnuplot/gnuplot_output_png_file
  rms_output_xvg_file:
     type: File
     outputSource: rmsd/rms_output_xvg_file
  md_output_gro_file:
    type: File
    outputSource: equilibration/md_output_gro_file
  md_output_trr_file:
    type: File
    outputSource: equilibration/md_output_trr_file

steps:
  mutate_structure:
    run: scwrl.cwl
    in:
      scw_script: scw_script
      scw_input_pdb_path: scw_input_pdb_path
      scw_step: scw_step
      scw_properties: properties
    out: [scw_output_pdb_file]
  create_topology:
    run: pdb2gmx.cwl
    in:
      p2g_script: p2g_script
      p2g_input_structure_pdb_path: mutate_structure/scw_output_pdb_file
      p2g_step: p2g_step
      p2g_properties: properties
    out: [p2g_output_gro_file, p2g_output_top_tar_file]
  create_water_box:
    run: editconf.cwl
    in:
      ec_script: ec_script
      ec_input_gro_path: create_topology/p2g_output_gro_file
      ec_step: ec_step
      ec_properties: properties
    out: [ec_output_gro_file]
  solvate:
    run: solvate.cwl
    in:
      sol_script: sol_script
      sol_input_solute_gro_path: create_water_box/ec_output_gro_file
      sol_input_top_tar_path: create_topology/p2g_output_top_tar_file
      sol_step: sol_step
      sol_properties: properties
    out: [sol_output_gro_file, sol_output_top_tar_file]

  ions_preprocess:
    run: grompp.cwl
    in:
      gpp_script: grompp_script
      gpp_input_gro_path: solvate/sol_output_gro_file
      gpp_input_top_tar_path: solvate/sol_output_top_tar_file
      gpp_step: gppions_step
      gpp_properties: properties
    out: [gpp_output_tpr_file]

  add_ions:
    run: genion.cwl
    in:
      gio_script: gio_script
      gio_input_tpr_path: ions_preprocess/gpp_output_tpr_file
      gio_input_gro_path: solvate/sol_output_gro_file
      gio_input_top_tar_path: solvate/sol_output_top_tar_file
      gio_step: gio_step
      gio_properties: properties
    out: [gio_output_gro_file, gio_output_top_tar_file]

  minimization_preprocess:
    run: grompp.cwl
    in:
      gpp_script: grompp_script
      gpp_input_gro_path: add_ions/gio_output_gro_file
      gpp_input_top_tar_path: add_ions/gio_output_top_tar_file
      gpp_step: gppmin_step
      gpp_properties: properties
    out: [gpp_output_tpr_file]

  minimization:
    run: mdrun.cwl
    in:
      md_script: mdrun_script
      md_input_tpr_path: minimization_preprocess/gpp_output_tpr_file
      md_properties: properties
      md_step: mdmin_step
    out: [md_output_gro_file, md_output_trr_file]

  nvt_dynamics_preprocess:
    run: grompp.cwl
    in:
      gpp_script: grompp_script
      gpp_input_gro_path: minimization/md_output_gro_file
      gpp_input_top_tar_path: add_ions/gio_output_top_tar_file
      gpp_step: gppnvt_step
      gpp_properties: properties
    out: [gpp_output_tpr_file]

  nvt_dynamics:
    run: mdrun.cwl
    in:
      md_script: mdrun_script
      md_input_tpr_path: nvt_dynamics_preprocess/gpp_output_tpr_file
      md_step: mdnvt_step
      md_properties: properties
    out: [md_output_gro_file, md_output_trr_file, md_output_cpt_file]

  npt_dynamics_preprocess:
    run: grompp.cwl
    in:
      gpp_script: grompp_script
      gpp_input_gro_path: nvt_dynamics/md_output_gro_file
      gpp_input_top_tar_path: add_ions/gio_output_top_tar_file
      gpp_step: gppnpt_step
      gpp_properties: properties
      gpp_input_cpt_path: nvt_dynamics/md_output_cpt_file
    out: [gpp_output_tpr_file]

  npt_dynamics:
    run: mdrun.cwl
    in:
      md_script: mdrun_script
      md_input_tpr_path: npt_dynamics_preprocess/gpp_output_tpr_file
      md_step: mdnpt_step
      md_properties: properties
    out: [md_output_gro_file, md_output_trr_file, md_output_cpt_file]

  equilibration_preprocess:
    run: grompp.cwl
    in:
      gpp_script: grompp_script
      gpp_input_gro_path: npt_dynamics/md_output_gro_file
      gpp_input_top_tar_path: add_ions/gio_output_top_tar_file
      gpp_step: gppeq_step
      gpp_properties: properties
      gpp_input_cpt_path: npt_dynamics/md_output_cpt_file
    out: [gpp_output_tpr_file]

  equilibration:
    run: mdrun.cwl
    in:
      md_script: mdrun_script
      md_input_tpr_path: equilibration_preprocess/gpp_output_tpr_file
      md_step: mdeq_step
      md_properties: properties
    out: [md_output_gro_file, md_output_trr_file, md_output_cpt_file]

  rmsd:
    run: rms.cwl
    in:
      rms_script: rms_script
      rms_input_gro_path: equilibration/md_output_gro_file
      rms_input_trr_path: equilibration/md_output_trr_file
      rms_step: rms_step
      rms_properties: properties
    out: [rms_output_xvg_file]

  gnuplot:
    run: gnuplot.cwl
    in:
      gnuplot_script: gnuplot_script
      gnuplot_input_xvg_path: rmsd/rms_output_xvg_file
      gnuplot_step: gnuplot_step
      gnuplot_properties: properties
    out: [gnuplot_output_png_file]
