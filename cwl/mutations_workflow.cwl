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
  # #GPPNVT
  # gppnvt_script: File
  # gppnvt_input_mdp_path: File
  # gppnvt_output_tpr_path: string
  # gppnvt_gmx_path: string
  # gppnvt_log_path: string
  # gppnvt_error_path: string
  # #MDNVT
  # mdnvt_script: File
  # mdnvt_output_gro_path: string
  # mdnvt_output_trr_path: string
  # mdnvt_output_edr_path: string
  # mdnvt_output_xtc_path: string
  # mdnvt_output_cpt_path: string
  # mdnvt_gmx_path: string
  # mdnvt_log_path: string
  # mdnvt_error_path: string
  # #GPPNPT
  # gppnpt_script: File
  # gppnpt_input_mdp_path: File
  # gppnpt_output_tpr_path: string
  # gppnpt_gmx_path: string
  # gppnpt_log_path: string
  # gppnpt_error_path: string
  # #MDNPT
  # mdnpt_script: File
  # mdnpt_output_gro_path: string
  # mdnpt_output_trr_path: string
  # mdnpt_output_edr_path: string
  # mdnpt_output_xtc_path: string
  # mdnpt_output_cpt_path: string
  # mdnpt_gmx_path: string
  # mdnpt_log_path: string
  # mdnpt_error_path: string
  # #GPPEQ
  # gppeq_script: File
  # gppeq_input_mdp_path: File
  # gppeq_output_tpr_path: string
  # gppeq_gmx_path: string
  # gppeq_log_path: string
  # gppeq_error_path: string
  # #MDEQ
  # mdeq_script: File
  # mdeq_output_gro_path: string
  # mdeq_output_trr_path: string
  # mdeq_output_edr_path: string
  # mdeq_output_xtc_path: string
  # mdeq_output_cpt_path: string
  # mdeq_gmx_path: string
  # mdeq_log_path: string
  # mdeq_error_path: string
  # #RMS
  # rms_script: File
  # rms_output_xvg_path: string
  # rms_gmx_path: string
  # rms_log_path: string
  # rms_error_path: string
  # #GNUPLOT
  # gnuplot_script: File
  # gnuplot_output_png_path: string
  # gnuplot_output_plotscript_path: string
  # gnuplot_gnuplot_path: string
  # gnuplot_log_path: string
  # gnuplot_error_path: string


outputs:
  md_output_gro_file:
    type: File
    outputSource: minimization/md_output_gro_file
  md_output_trr_file:
    type: File
    outputSource: minimization/md_output_trr_file
  # sol_output_top_tar_file:
  #   type: File
  #   outputSource: solvate/sol_output_top_tar_file
  # gnuplot_output_png_file:
  #    type: File
  #    outputSource: gnuplot/gnuplot_output_png_file
  # gnuplot_output_plotscript_file:
  #    type: File
  #    outputSource: gnuplot/gnuplot_output_plotscript_file
  # rms_output_xvg_file:
  #    type: File
  #    outputSource: rms/rms_output_xvg_file
  # md_output_gro_file:
  #   type: File
  #   outputSource: mdeq/md_output_gro_file
  # md_output_trr_file:
  #   type: File
  #   outputSource: mdeq/md_output_trr_file
  # md_output_xtc_file:
  #   type: File
  #   outputSource: mdeq/md_output_xtc_file

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
  #
  # gppnvt:
  #   run: grompp.cwl
  #   in:
  #     gpp_script: gppnvt_script
  #     gpp_input_mdp_path: gppnvt_input_mdp_path
  #     gpp_input_gro_path: mdmin/md_output_gro_file
  #     gpp_input_top_tar_path: genion/gio_output_top_tar_file
  #     gpp_output_tpr_path: gppnvt_output_tpr_path
  #     gpp_gmx_path: gppnvt_gmx_path
  #     gpp_log_path: gppnvt_log_path
  #     gpp_error_path: gppnvt_error_path
  #   out: [gpp_output_tpr_file]
  #
  # mdnvt:
  #   run: mdrun.cwl
  #   in:
  #     md_script: mdnvt_script
  #     md_input_tpr_path: gppnvt/gpp_output_tpr_file
  #     md_output_gro_path: mdnvt_output_gro_path
  #     md_output_trr_path: mdnvt_output_trr_path
  #     md_output_edr_path: mdnvt_output_edr_path
  #     md_output_xtc_path: mdnvt_output_xtc_path
  #     md_output_cpt_path: mdnvt_output_cpt_path
  #     md_gmx_path: mdnvt_gmx_path
  #     md_log_path: mdnvt_log_path
  #     md_error_path: mdnvt_error_path
  #   out: [md_output_gro_file, md_output_trr_file, md_output_edr_file, md_output_cpt_file]
  #
  # gppnpt:
  #   run: grompp.cwl
  #   in:
  #     gpp_script: gppnpt_script
  #     gpp_input_mdp_path: gppnpt_input_mdp_path
  #     gpp_input_gro_path: mdnvt/md_output_gro_file
  #     gpp_input_top_tar_path: genion/gio_output_top_tar_file
  #     gpp_output_tpr_path: gppnpt_output_tpr_path
  #     gpp_gmx_path: gppnpt_gmx_path
  #     gpp_log_path: gppnpt_log_path
  #     gpp_error_path: gppnpt_error_path
  #     gpp_input_cpt_path: mdnvt/md_output_cpt_file
  #   out: [gpp_output_tpr_file]
  #
  # mdnpt:
  #   run: mdrun.cwl
  #   in:
  #     md_script: mdnpt_script
  #     md_input_tpr_path: gppnpt/gpp_output_tpr_file
  #     md_output_gro_path: mdnpt_output_gro_path
  #     md_output_trr_path: mdnpt_output_trr_path
  #     md_output_edr_path: mdnpt_output_edr_path
  #     md_output_xtc_path: mdnpt_output_xtc_path
  #     md_output_cpt_path: mdnpt_output_cpt_path
  #     md_gmx_path: mdnpt_gmx_path
  #     md_log_path: mdnpt_log_path
  #     md_error_path: mdnpt_error_path
  #   out: [md_output_gro_file, md_output_trr_file, md_output_edr_file, md_output_cpt_file]
  #
  # gppeq:
  #   run: grompp.cwl
  #   in:
  #     gpp_script: gppeq_script
  #     gpp_input_mdp_path: gppeq_input_mdp_path
  #     gpp_input_gro_path: mdnpt/md_output_gro_file
  #     gpp_input_top_tar_path: genion/gio_output_top_tar_file
  #     gpp_output_tpr_path: gppeq_output_tpr_path
  #     gpp_gmx_path: gppeq_gmx_path
  #     gpp_log_path: gppeq_log_path
  #     gpp_error_path: gppeq_error_path
  #     gpp_input_cpt_path: mdnpt/md_output_cpt_file
  #   out: [gpp_output_tpr_file]
  #
  # mdeq:
  #   run: mdrun.cwl
  #   in:
  #     md_script: mdeq_script
  #     md_input_tpr_path: gppeq/gpp_output_tpr_file
  #     md_output_gro_path: mdeq_output_gro_path
  #     md_output_trr_path: mdeq_output_trr_path
  #     md_output_edr_path: mdeq_output_edr_path
  #     md_output_xtc_path: mdeq_output_xtc_path
  #     md_output_cpt_path: mdeq_output_cpt_path
  #     md_gmx_path: mdeq_gmx_path
  #     md_log_path: mdeq_log_path
  #     md_error_path: mdeq_error_path
  #   out: [md_output_gro_file, md_output_trr_file, md_output_edr_file, md_output_xtc_file, md_output_cpt_file]
  #
  # rmsd:
  #   run: rms.cwl
  #   in:
  #     rms_script: rms_script
  #     rms_input_gro_path: mdeq/md_output_gro_file
  #     rms_input_trr_path: mdeq/md_output_trr_file
  #     rms_output_xvg_path: rms_output_xvg_path
  #     rms_gmx_path: rms_gmx_path
  #     rms_log_path: rms_log_path
  #     rms_error_path: rms_error_path
  #   out: [rms_output_xvg_file]
  #
  # gnuplot:
  #   run: gnuplot.cwl
  #   in:
  #     gnuplot_script: gnuplot_script
  #     gnuplot_mutation: scw_mutation
  #     gnuplot_xvg_file_path: rms/rms_output_xvg_file
  #     gnuplot_output_png_path: gnuplot_output_png_path
  #     gnuplot_output_plotscript_path: gnuplot_output_plotscript_path
  #     gnuplot_gnuplot_path: gnuplot_gnuplot_path
  #     gnuplot_log_path: gnuplot_log_path
  #     gnuplot_error_path: gnuplot_error_path
  #   out: [gnuplot_output_png_file, gnuplot_output_plotscript_file]
