#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - python
inputs:
  sol_script:
    type: File
    inputBinding:
      position: 1
  sol_input_solute_gro_path:
    type: File
    inputBinding:
      position: 2
  sol_output_gro_path:
    type: string
    inputBinding:
      position: 3
  sol_input_top_tar_path:
    type: File
    inputBinding:
      position: 4
  sol_output_top_tar_path:
    type: string
    inputBinding:
      position: 5
  sol_properties:
    type: string
    inputBinding:
      position: 6
outputs:
  sol_output_gro_file:
    type: File
    outputBinding:
      glob: $(inputs.sol_output_gro_path)
  sol_output_top_tar_file:
    type: File
    outputBinding:
      glob: $(inputs.sol_output_top_tar_path)
