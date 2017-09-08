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
    default:
      class: File
      location: ../gromacs_wrapper/editconf.py
  ec_input_gro_path:
    type: File
    inputBinding:
      position: 2
  ec_output_gro_path:
    type: string
    inputBinding:
      position: 3
    default: "ec.gro"
  ec_step:
    type: string
    inputBinding:
      position: 4
    default: "step5_ec:linux"
  ec_properties:
    type: File
    inputBinding:
      position: 5
    default:
      class: File
      location: ../workflows/conf_2mut_nt0.yaml
outputs:
  ec_output_gro_file:
    type: File
    outputBinding:
      glob: $(inputs.ec_output_gro_path)
