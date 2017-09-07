#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow

inputs:
  #SCWRL
  scw_script: File
  scw_input_pdb_path: File
  scw_output_pdb_path: string
  scw_properties: string
  # #PDB2GMX
  p2g_script: File
  p2g_output_gro_path: string
  p2g_output_top_tar_path: string
  p2g_properties: string
  #EDITCONF
  ec_script: File
  ec_output_gro_path: string
  ec_properties: string
  #SOLVATE
  sol_script: File
  sol_output_gro_path: string
  sol_output_top_tar_path: string
  sol_properties: string
  #GPPIONS
  gppions_script: File
  gppions_output_tpr_path: string
  gppions_properties: string
  # #GENION
  gio_script: File
  gio_output_gro_path: string
  gio_output_top_tar_path: string
  gio_properties: string
  #GPPMIN
  gppmin_script: File
  gppmin_output_tpr_path: string
  gppmin_properties: string
  #MDMIN
  mdmin_script: File
  mdmin_output_gro_path: string
  mdmin_output_trr_path: string
  mdmin_output_cpt_path: string
  mdmin_properties: string
  #GPPNVT
  gppnvt_script: File
  gppnvt_output_tpr_path: string
  gppnvt_properties: string
  #MDNVT
  mdnvt_script: File
  mdnvt_output_trr_path: string
  mdnvt_output_gro_path: string
  mdnvt_output_cpt_path: string
  mdnvt_properties: string
  #GPPNPT
  gppnpt_script: File
  gppnpt_output_tpr_path: string
  gppnpt_properties: string
  #MDNPT
  mdnpt_script: File
  mdnpt_output_gro_path: string
  mdnpt_output_trr_path: string
  mdnpt_output_cpt_path: string
  mdnpt_properties: string
  #GPPEQ
  gppeq_script: File
  gppeq_output_tpr_path: string
  gppeq_properties: string
  #MDEQ
  mdeq_script: File
  mdeq_output_gro_path: string
  mdeq_output_trr_path: string
  mdeq_output_cpt_path: string
  mdeq_properties: string
  #RMS
  rms_script: File
  rms_output_xvg_path: string
  rms_properties: string
  #GNUPLOT
  gnuplot_script: File
  gnuplot_output_png_path: string
  gnuplot_properties: string

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
      scw_output_pdb_path: scw_output_pdb_path
      scw_properties: scw_properties
    out: [scw_output_pdb_file]
  create_topology:
    run: pdb2gmx.cwl
    in:
      p2g_script: p2g_script
      p2g_input_structure_pdb_path: mutate_structure/scw_output_pdb_file
      p2g_output_gro_path: p2g_output_gro_path
      p2g_output_top_tar_path: p2g_output_top_tar_path
      p2g_properties: p2g_properties
    out: [p2g_output_gro_file, p2g_output_top_tar_file]
  create_water_box:
    run: editconf.cwl
    in:
      ec_script: ec_script
      ec_input_gro_path: create_topology/p2g_output_gro_file
      ec_output_gro_path: ec_output_gro_path
      ec_properties: ec_properties
    out: [ec_output_gro_file]
  solvate:
    run: solvate.cwl
    in:
      sol_script: sol_script
      sol_input_solute_gro_path: create_water_box/ec_output_gro_file
      sol_output_gro_path: sol_output_gro_path
      sol_input_top_tar_path: create_topology/p2g_output_top_tar_file
      sol_output_top_tar_path: sol_output_top_tar_path
      sol_properties: sol_properties
    out: [sol_output_gro_file, sol_output_top_tar_file]

  ions_preprocess:
    run: grompp.cwl
    in:
      gpp_script: gppions_script
      gpp_input_gro_path: solvate/sol_output_gro_file
      gpp_input_top_tar_path: solvate/sol_output_top_tar_file
      gpp_output_tpr_path: gppions_output_tpr_path
      gpp_properties: gppions_properties
    out: [gpp_output_tpr_file]

  add_ions:
    run: genion.cwl
    in:
      gio_script: gio_script
      gio_input_tpr_path: ions_preprocess/gpp_output_tpr_file
      gio_output_gro_path: gio_output_gro_path
      gio_input_gro_path: solvate/sol_output_gro_file
      gio_input_top_tar_path: solvate/sol_output_top_tar_file
      gio_output_top_tar_path: gio_output_top_tar_path
      gio_properties: gio_properties
    out: [gio_output_gro_file, gio_output_top_tar_file]

  minimization_preprocess:
    run: grompp.cwl
    in:
      gpp_script: gppmin_script
      gpp_input_gro_path: add_ions/gio_output_gro_file
      gpp_input_top_tar_path: add_ions/gio_output_top_tar_file
      gpp_output_tpr_path: gppmin_output_tpr_path
      gpp_properties: gppmin_properties
    out: [gpp_output_tpr_file]

  minimization:
    run: mdrun.cwl
    in:
      md_script: mdmin_script
      md_input_tpr_path: minimization_preprocess/gpp_output_tpr_file
      md_output_gro_path: mdmin_output_gro_path
      md_output_trr_path: mdmin_output_trr_path
      md_properties: mdmin_properties
      md_output_cpt_path: mdmin_output_cpt_path
    out: [md_output_gro_file, md_output_trr_file]

  nvt_dynamics_preprocess:
    run: grompp.cwl
    in:
      gpp_script: gppnvt_script
      gpp_input_gro_path: minimization/md_output_gro_file
      gpp_input_top_tar_path: add_ions/gio_output_top_tar_file
      gpp_output_tpr_path: gppnvt_output_tpr_path
      gpp_properties: gppnvt_properties
    out: [gpp_output_tpr_file]

  nvt_dynamics:
    run: mdrun.cwl
    in:
      md_script: mdnvt_script
      md_input_tpr_path: nvt_dynamics_preprocess/gpp_output_tpr_file
      md_output_trr_path: mdnvt_output_trr_path
      md_output_gro_path: mdnvt_output_gro_path
      md_properties: mdnvt_properties
      md_output_cpt_path: mdnvt_output_cpt_path
    out: [md_output_gro_file, md_output_trr_file, md_output_cpt_file]

  npt_dynamics_preprocess:
    run: grompp.cwl
    in:
      gpp_script: gppnpt_script
      gpp_input_gro_path: nvt_dynamics/md_output_gro_file
      gpp_input_top_tar_path: add_ions/gio_output_top_tar_file
      gpp_output_tpr_path: gppnpt_output_tpr_path
      gpp_properties: gppnpt_properties
      gpp_input_cpt_path: nvt_dynamics/md_output_cpt_file
    out: [gpp_output_tpr_file]

  npt_dynamics:
    run: mdrun.cwl
    in:
      md_script: mdnpt_script
      md_input_tpr_path: npt_dynamics_preprocess/gpp_output_tpr_file
      md_output_trr_path: mdnpt_output_trr_path
      md_output_gro_path: mdnpt_output_gro_path
      md_properties: mdnpt_properties
      md_output_cpt_path: mdnpt_output_cpt_path
    out: [md_output_gro_file, md_output_trr_file, md_output_cpt_file]

  equilibration_preprocess:
    run: grompp.cwl
    in:
      gpp_script: gppeq_script
      gpp_input_gro_path: npt_dynamics/md_output_gro_file
      gpp_input_top_tar_path: add_ions/gio_output_top_tar_file
      gpp_output_tpr_path: gppeq_output_tpr_path
      gpp_properties: gppeq_properties
      gpp_input_cpt_path: npt_dynamics/md_output_cpt_file
    out: [gpp_output_tpr_file]

  equilibration:
    run: mdrun.cwl
    in:
      md_script: mdeq_script
      md_input_tpr_path: equilibration_preprocess/gpp_output_tpr_file
      md_output_trr_path: mdeq_output_trr_path
      md_output_gro_path: mdeq_output_gro_path
      md_properties: mdeq_properties
      md_output_cpt_path: mdeq_output_cpt_path
    out: [md_output_gro_file, md_output_trr_file, md_output_cpt_file]

  rmsd:
    run: rms.cwl
    in:
      rms_script: rms_script
      rms_input_gro_path: equilibration/md_output_gro_file
      rms_input_trr_path: equilibration/md_output_trr_file
      rms_output_xvg_path: rms_output_xvg_path
      rms_properties: rms_properties
    out: [rms_output_xvg_file]

  gnuplot:
    run: gnuplot.cwl
    in:
      gnuplot_script: gnuplot_script
      gnuplot_input_xvg_path: rmsd/rms_output_xvg_file
      gnuplot_output_png_path: gnuplot_output_png_path
      gnuplot_properties: gnuplot_properties
    out: [gnuplot_output_png_file]
