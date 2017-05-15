#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool

baseCommand:
  - python
inputs:
  ec_script:
    type: File
    inputBinding:
      position: 1
  ec_input_gro_path:
    type: File
    inputBinding:
      position: 2
  ec_output_gro_path:
    type: string
    inputBinding:
      position: 3
  ec_box_type:
    type: string
    inputBinding:
      position: 4
  ec_distance_to_molecule:
    type: string
    inputBinding:
      position: 5
  ec_center_molecule:
    type: string
    inputBinding:
      position: 6
  ec_gmx_path:
    type: string
    inputBinding:
      position: 7
  ec_log_path:
    type: string
    inputBinding:
      position: 8
  ec_error_path:
    type: string
    inputBinding:
      position: 9
outputs:
  ec_output_gro_file:
    type: File
    outputBinding:
      glob: $(inputs.ec_output_gro_path)
