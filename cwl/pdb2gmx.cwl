#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool

baseCommand:
  - python
inputs:
  p2g_script:
    type: File
    inputBinding:
      position: 1
  p2g_input_structure_pdb_path: 
    type: File
    format: http://edamontology.org/format_1476 #PDB format from EDAM
    inputBinding:
      position: 2
  p2g_output_gro_path: 
    type: string
    inputBinding:
      position: 3
  p2g_output_top_path:
    type: string
    inputBinding:
      position: 4
  p2g_output_itp_path:
    type: string
    inputBinding:
      position: 5
  p2g_output_top_tar_path:
    type: string
    inputBinding:
      position: 6
  p2g_water_type:
    type: string
    inputBinding:
      position: 7
  p2g_force_field:
    type: string
    inputBinding:
      position: 8
  p2g_ignh:
    type: string
    inputBinding:
      position: 9
  p2g_gmx_path:
    type: string
    inputBinding:
      position: 10
  p2g_log_path:
    type: string
    inputBinding:
      position: 11
  p2g_error_path:
    type: string
    inputBinding:
      position: 12

outputs:
  p2g_output_gro_file:
    type: File
    outputBinding:
      glob: $(inputs.p2g_output_gro_path)
  p2g_output_top_tar_file:
    type: File
    outputBinding:
      glob: $(inputs.p2g_output_top_tar_path)
