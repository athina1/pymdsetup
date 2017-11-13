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
    default:
      class: File
      location: ../gromacs_wrapper/grompp.py
  gpp_input_gro_path:
    type: File
    inputBinding:
      position: 2
  gpp_input_top_tar_path:
    type: File
    inputBinding:
      position: 3
  gpp_output_tpr_path:
    type: string
    inputBinding:
      position: 4
    default: "grompp.tpr"
  gpp_step:
    type: string
    inputBinding:
      position: 5
  gpp_properties:
    type: File
    inputBinding:
      position: 6
    default:
      class: File
      location: "../workflows/conf_2mut_nt0.yaml"
  gpp_input_cpt_path:
    type: File?
    inputBinding:
      position: 7
outputs:
  gpp_output_tpr_file:
    type: File
    outputBinding:
      glob: $(inputs.gpp_output_tpr_path)
