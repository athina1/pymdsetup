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
  md_output_trr_path:
    type: string
    inputBinding:
      position: 3
    default: "md.trr"
  md_output_gro_path:
    type: string
    inputBinding:
      position: 4
    default: "md.gro"
  md_step:
    type: string
    inputBinding:
      position: 5
  md_properties:
    type: File
    inputBinding:
      position: 6
  md_output_cpt_path:
    type: string?
    inputBinding:
      position: 7
    default: "md.cpt"
outputs:
  md_output_gro_file:
    type: File
    outputBinding:
      glob: $(inputs.md_output_gro_path)
  md_output_trr_file:
    type: File
    outputBinding:
      glob: $(inputs.md_output_trr_path)
  md_output_cpt_file:
    type: File?
    outputBinding:
      glob: $(inputs.md_output_cpt_path)
