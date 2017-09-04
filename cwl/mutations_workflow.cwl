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
  # p2g_script: File
  # p2g_output_gro_path: string
  # p2g_output_top_path: string
  # p2g_output_itp_path: string
  # p2g_output_top_tar_path: string
  # p2g_water_type: string
  # p2g_force_field: string
  # p2g_ignh: string
  # p2g_gmx_path: string
  # p2g_log_path: string
  # p2g_error_path: string
  # #EDITCONF
  # ec_script: File
  # ec_output_gro_path: string
  # ec_box_type: string
  # ec_distance_to_molecule: string
  # ec_center_molecule: string
  # ec_gmx_path: string
  # ec_log_path: string
  # ec_error_path: string
  # #SOLVATE
  # sol_script: File
  # sol_output_gro_path: string
  # sol_output_top_path: string
  # sol_output_top_tar_path: string
  # sol_input_solvent_gro_path: string
  # sol_gmx_path: string
  # sol_log_path: string
  # sol_error_path: string
  # #GPPIONS
  # gppions_script: File
  # gppions_input_mdp_path: File
  # gppions_output_tpr_path: string
  # gppions_gmx_path: string
  # gppions_log_path: string
  # gppions_error_path: string
  # #GENION
  # gio_script: File
  # gio_output_gro_path: string
  # gio_output_top_path: string
  # gio_output_top_tar_path: string
  # gio_replaced_group: string
  # gio_neutral: string
  # gio_concentration: string
  # gio_gmx_path: string
  # gio_log_path: string
  # gio_error_path: string
  # #GPPMIN
  # gppmin_script: File
  # gppmin_input_mdp_path: File
  # gppmin_output_tpr_path: string
  # gppmin_gmx_path: string
  # gppmin_log_path: string
  # gppmin_error_path: string
  # #MDMIN
  # mdmin_script: File
  # mdmin_output_gro_path: string
  # mdmin_output_trr_path: string
  # mdmin_output_edr_path: string
  # mdmin_output_xtc_path: string
  # mdmin_output_cpt_path: string
  # mdmin_gmx_path: string
  # mdmin_log_path: string
  # mdmin_error_path: string
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
  scw_output_pdb_file:
    type: File
    outputSource: mutate_structure/scw_output_pdb_file
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
  # pdb2gmx:
  #   run: pdb2gmx.cwl
  #   in:
  #     p2g_script: p2g_script
  #     p2g_input_structure_pdb_path: scwrl/scw_output_pdb_file
  #     p2g_output_gro_path: p2g_output_gro_path
  #     p2g_output_top_path: p2g_output_top_path
  #     p2g_output_itp_path: p2g_output_itp_path
  #     p2g_output_top_tar_path: p2g_output_top_tar_path
  #     p2g_water_type: p2g_water_type
  #     p2g_force_field: p2g_force_field
  #     p2g_ignh: p2g_ignh
  #     p2g_gmx_path: p2g_gmx_path
  #     p2g_log_path: p2g_log_path
  #     p2g_error_path: p2g_error_path
  #   out: [p2g_output_gro_file, p2g_output_top_tar_file]
  #
  # editconf:
  #   run: editconf.cwl
  #   in:
  #     ec_script: ec_script
  #     ec_input_gro_path: pdb2gmx/p2g_output_gro_file
  #     ec_output_gro_path: ec_output_gro_path
  #     ec_box_type: ec_box_type
  #     ec_distance_to_molecule: ec_distance_to_molecule
  #     ec_center_molecule: ec_center_molecule
  #     ec_gmx_path: ec_gmx_path
  #     ec_log_path: ec_log_path
  #     ec_error_path: ec_error_path
  #   out: [ec_output_gro_file]
  #
  # solvate:
  #   run: solvate.cwl
  #   in:
  #     sol_script: sol_script
  #     sol_input_solute_gro_path: editconf/ec_output_gro_file
  #     sol_output_gro_path: sol_output_gro_path
  #     sol_input_top_tar_path: pdb2gmx/p2g_output_top_tar_file
  #     sol_output_top_path: sol_output_top_path
  #     sol_output_top_tar_path: sol_output_top_tar_path
  #     sol_input_solvent_gro_path: sol_input_solvent_gro_path
  #     sol_gmx_path: sol_gmx_path
  #     sol_log_path: sol_log_path
  #     sol_error_path: sol_error_path
  #   out: [sol_output_gro_file, sol_output_top_file, sol_output_top_tar_file]
  #
  # gppions:
  #   run: grompp.cwl
  #   in:
  #     gpp_script: gppions_script
  #     gpp_input_mdp_path: gppions_input_mdp_path
  #     gpp_input_gro_path: solvate/sol_output_gro_file
  #     gpp_input_top_tar_path: solvate/sol_output_top_tar_file
  #     gpp_output_tpr_path: gppions_output_tpr_path
  #     gpp_gmx_path: gppions_gmx_path
  #     gpp_log_path: gppions_log_path
  #     gpp_error_path: gppions_error_path
  #   out: [gpp_output_tpr_file]
  #
  # genion:
  #   run: genion.cwl
  #   in:
  #     gio_script: gio_script
  #     gio_input_tpr_path: gppions/gpp_output_tpr_file
  #     gio_output_gro_path: gio_output_gro_path
  #     gio_input_gro_path: solvate/sol_output_gro_file
  #     gio_input_top_tar_path: solvate/sol_output_top_tar_file
  #     gio_output_top_path: gio_output_top_path
  #     gio_output_top_tar_path: gio_output_top_tar_path
  #     gio_replaced_group: gio_replaced_group
  #     gio_neutral: gio_neutral
  #     gio_concentration: gio_concentration
  #     gio_gmx_path: gio_gmx_path
  #     gio_log_path: gio_log_path
  #     gio_error_path: gio_error_path
  #   out: [gio_output_gro_file, gio_output_top_file, gio_output_top_tar_file]
  #
  # gppmin:
  #   run: grompp.cwl
  #   in:
  #     gpp_script: gppmin_script
  #     gpp_input_mdp_path: gppmin_input_mdp_path
  #     gpp_input_gro_path: genion/gio_output_gro_file
  #     gpp_input_top_tar_path: genion/gio_output_top_tar_file
  #     gpp_output_tpr_path: gppmin_output_tpr_path
  #     gpp_gmx_path: gppmin_gmx_path
  #     gpp_log_path: gppmin_log_path
  #     gpp_error_path: gppmin_error_path
  #   out: [gpp_output_tpr_file]
  #
  # mdmin:
  #   run: mdrun.cwl
  #   in:
  #     md_script: mdmin_script
  #     md_input_tpr_path: gppmin/gpp_output_tpr_file
  #     md_output_gro_path: mdmin_output_gro_path
  #     md_output_trr_path: mdmin_output_trr_path
  #     md_output_edr_path: mdmin_output_edr_path
  #     md_output_xtc_path: mdmin_output_xtc_path
  #     md_output_cpt_path: mdmin_output_cpt_path
  #     md_gmx_path: mdmin_gmx_path
  #     md_log_path: mdmin_log_path
  #     md_error_path: mdmin_error_path
  #   out: [md_output_gro_file, md_output_trr_file, md_output_edr_file]
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
  # rms:
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
