#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow

inputs:
  #PDB2GMX
  p2g_script: File
  p2g_input_structure_pdb_path: File
  p2g_output_gro_path: string
  p2g_output_top_path: string
  p2g_output_itp_path: string
  p2g_output_top_tar_path: string
  p2g_water_type: string
  p2g_force_field: string
  p2g_ignh: string
  p2g_gmx_path: string
  p2g_log_path: string
  p2g_error_path: string
  #EDITCONF
  ec_script: File
  ec_output_gro_path: string
  ec_box_type: string
  ec_distance_to_molecule: string
  ec_center_molecule: string
  ec_gmx_path: string
  ec_log_path: string
  ec_error_path: string
  #SOLVATE
  sol_script: File
  sol_output_gro_path: string
  sol_output_top_path: string
  sol_output_top_tar_path: string
  sol_input_solvent_gro_path: string
  sol_gmx_path: string
  sol_log_path: string
  sol_error_path: string
  #GPPIONS
  gppions_script: File
  gppions_input_mdp_path: File
  gppions_output_tpr_path: string
  gppions_gmx_path: string
  gppions_log_path: string
  gppions_error_path: string
  #GENION
  gio_script: File
  gio_output_gro_path: string
  gio_output_top_path: string
  gio_output_top_tar_path: string
  gio_replaced_group: string
  gio_neutral: string
  gio_concentration: string
  gio_gmx_path: string
  gio_log_path: string
  gio_error_path: string
  #GPPMIN
  gppmin_script: File
  gppmin_input_mdp_path: File
  gppmin_output_tpr_path: string
  gppmin_gmx_path: string
  gppmin_log_path: string
  gppmin_error_path: string
  #MDMIN
  mdmin_script: File
  mdmin_output_gro_path: string
  mdmin_output_trr_path: string
  mdmin_output_edr_path: string
  mdmin_output_xtc_path: string
  mdmin_output_cpt_path: string
  mdmin_gmx_path: string
  mdmin_log_path: string
  mdmin_error_path: string
  #GPPNVT
  gppnvt_script: File
  gppnvt_input_mdp_path: File
  gppnvt_output_tpr_path: string
  gppnvt_gmx_path: string
  gppnvt_log_path: string
  gppnvt_error_path: string


outputs:
  gpp_output_tpr_file:
    type: File
    outputSource: gppnvt/gpp_output_tpr_file

steps:
  pdb2gmx:
    run: pdb2gmx.cwl
    in:
      p2g_script: p2g_script
      p2g_input_structure_pdb_path: p2g_input_structure_pdb_path
      p2g_output_gro_path: p2g_output_gro_path
      p2g_output_top_path: p2g_output_top_path
      p2g_output_itp_path: p2g_output_itp_path
      p2g_output_top_tar_path: p2g_output_top_tar_path
      p2g_water_type: p2g_water_type
      p2g_force_field: p2g_force_field
      p2g_ignh: p2g_ignh
      p2g_gmx_path: p2g_gmx_path
      p2g_log_path: p2g_log_path
      p2g_error_path: p2g_error_path
    out: [p2g_output_gro_file, p2g_output_top_tar_file]

  editconf:
    run: editconf.cwl
    in:
      ec_script: ec_script
      ec_input_gro_path: pdb2gmx/p2g_output_gro_file
      ec_output_gro_path: ec_output_gro_path
      ec_box_type: ec_box_type
      ec_distance_to_molecule: ec_distance_to_molecule
      ec_center_molecule: ec_center_molecule
      ec_gmx_path: ec_gmx_path
      ec_log_path: ec_log_path
      ec_error_path: ec_error_path
    out: [ec_output_gro_file]

  solvate:
    run: solvate.cwl
    in:
      sol_script: sol_script
      sol_input_solute_gro_path: editconf/ec_output_gro_file
      sol_output_gro_path: sol_output_gro_path
      sol_input_top_tar_path: pdb2gmx/p2g_output_top_tar_file
      sol_output_top_path: sol_output_top_path
      sol_output_top_tar_path: sol_output_top_tar_path
      sol_input_solvent_gro_path: sol_input_solvent_gro_path
      sol_gmx_path: sol_gmx_path
      sol_log_path: sol_log_path
      sol_error_path: sol_error_path
    out: [sol_output_gro_file, sol_output_top_file, sol_output_top_tar_file]

  gppions:
    run: grompp.cwl
    in:
      gpp_script: gppions_script
      gpp_input_mdp_path: gppions_input_mdp_path
      gpp_input_gro_path: solvate/sol_output_gro_file
      gpp_input_top_tar_path: solvate/sol_output_top_tar_file
      gpp_output_tpr_path: gppions_output_tpr_path
      gpp_gmx_path: gppions_gmx_path
      gpp_log_path: gppions_log_path
      gpp_error_path: gppions_error_path
    out: [gpp_output_tpr_file]

  genion:
    run: genion.cwl
    in:
      gio_script: gio_script
      gio_input_tpr_path: gppions/gpp_output_tpr_file
      gio_output_gro_path: gio_output_gro_path
      gio_input_gro_path: solvate/sol_output_gro_file
      gio_input_top_tar_path: solvate/sol_output_top_tar_file
      gio_output_top_path: gio_output_top_path
      gio_output_top_tar_path: gio_output_top_tar_path
      gio_replaced_group: gio_replaced_group
      gio_neutral: gio_neutral
      gio_concentration: gio_concentration
      gio_gmx_path: gio_gmx_path
      gio_log_path: gio_log_path
      gio_error_path: gio_error_path
    out: [gio_output_gro_file, gio_output_top_file, gio_output_top_tar_file]

  gppmin:
    run: grompp.cwl
    in:
      gpp_script: gppmin_script
      gpp_input_mdp_path: gppmin_input_mdp_path
      gpp_input_gro_path: genion/gio_output_gro_file
      gpp_input_top_tar_path: genion/gio_output_top_tar_file
      gpp_output_tpr_path: gppmin_output_tpr_path
      gpp_gmx_path: gppmin_gmx_path
      gpp_log_path: gppmin_log_path
      gpp_error_path: gppmin_error_path
    out: [gpp_output_tpr_file]

  mdmin:
    run: mdrun.cwl
    in:
      md_script: mdmin_script
      md_input_tpr_path: gppmin/gpp_output_tpr_file
      md_output_gro_path: mdmin_output_gro_path
      md_output_trr_path: mdmin_output_trr_path
      md_output_edr_path: mdmin_output_edr_path
      md_output_xtc_path: mdmin_output_xtc_path
      md_output_cpt_path: mdmin_output_cpt_path
      md_gmx_path: mdmin_gmx_path
      md_log_path: mdmin_log_path
      md_error_path: mdmin_error_path
    out: [md_output_gro_file, md_output_trr_file, md_output_edr_file]

  gppnvt:
    run: grompp.cwl
    in:
      gpp_script: gppnvt_script
      gpp_input_mdp_path: gppnvt_input_mdp_path
      gpp_input_gro_path: mdmin/md_output_gro_file
      gpp_input_top_tar_path: genion/gio_output_top_tar_file
      gpp_output_tpr_path: gppnvt_output_tpr_path
      gpp_gmx_path: gppnvt_gmx_path
      gpp_log_path: gppnvt_log_path
      gpp_error_path: gppnvt_error_path
    out: [gpp_output_tpr_file]
