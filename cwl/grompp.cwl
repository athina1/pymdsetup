#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool

baseCommand:
  - python
inputs:
  gpp_script:
    type: File
    inputBinding:
      position: 1
  gpp_input_mdp_path:
    type: File
    inputBinding:
      position: 2
  gpp_input_gro_path:
    type: File
    inputBinding:
      position: 3
  gpp_input_top_tar_path:
    type: File
    inputBinding:
      position: 4
  gpp_output_tpr_path:
    type: string
    inputBinding:
      position: 5
  gpp_gmx_path:
    type: string
    inputBinding:
      position: 6
  gpp_log_path:
    type: string
    inputBinding:
      position: 7
  gpp_error_path:
    type: string
    inputBinding:
      position: 8
  gpp_input_cpt_path:
    type: File?
    inputBinding:
      position: 9
outputs:
  gpp_output_tpr_file:
    type: File
    outputBinding:
      glob: $(inputs.gpp_output_tpr_path)
