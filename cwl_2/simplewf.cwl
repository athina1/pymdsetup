#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow

inputs:
  p2g_input_structure_pdb_path: File


outputs:
  p2g_output_gro_file:
     type: File
     outputSource: create_topology/p2g_output_gro_file

  p2g_output_top_tar_file:
      type: File
      outputSource: create_topology/p2g_output_top_tar_file

steps:
  create_topology:
    run: pdb2gmx.cwl
    in:
      p2g_input_structure_pdb_path: p2g_input_structure_pdb_path
      p2g_water_type:
          default: spce
      p2g_force_field:
          default: amber99sb-ildn
      p2g_ignh:
          default: True
    out: [p2g_output_gro_file, p2g_output_top_tar_file]
