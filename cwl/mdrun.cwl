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
    default:
      class: File
      location: "../gromacs_wrapper/mdrun.py"
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
    default: "step10_mdmin:linux"
  md_properties:
    type: File
    inputBinding:
      position: 6
    default:
      class: File
      location: "../workflows/conf_2mut_nt0.yaml"
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
