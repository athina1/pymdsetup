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

outputs:
  sol_output_gro_file:
    type: File
    outputSource: solvate/sol_output_gro_file
  sol_output_top_file:
    type: File
    outputSource: solvate/sol_output_top_file
  sol_output_top_tar_file:
    type: File
    outputSource: solvate/sol_output_top_tar_file

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
