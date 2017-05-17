#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool

baseCommand:
  - python
inputs:
  md_script:
    type: File
    inputBinding:
      position: 1
  md_input_tpr_path:
    type: File
    inputBinding:
      position: 2
  md_output_gro_path:
    type: string
    inputBinding:
      position: 3
  md_output_trr_path:
    type: string
    inputBinding:
      position: 4
  md_output_edr_path:
    type: string
    inputBinding:
      position: 5
  md_output_xtc_path:
    type: string
    inputBinding:
      position: 6
  md_output_cpt_path:
    type: string
    inputBinding:
      position: 7
  md_gmx_path:
    type: string
    inputBinding:
      position: 8
  md_log_path:
    type: string
    inputBinding:
      position: 9
  md_error_path:
    type: string
    inputBinding:
      position: 10

outputs:
  md_output_gro_file:
    type: File
    outputBinding:
      glob: $(inputs.md_output_gro_path)
  md_output_trr_file:
    type: File
    outputBinding:
      glob: $(inputs.md_output_trr_path)
  md_output_edr_file:
    type: File
    outputBinding:
      glob: $(inputs.md_output_edr_path)
  md_output_xtc_file:
    type: File?
    outputBinding:
      glob: $(inputs.md_output_xtc_path)
  md_output_cpt_file:
    type: File?
    outputBinding:
      glob: $(inputs.md_output_cpt_path)
