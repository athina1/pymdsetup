#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - python
inputs:
  rms_script:
    type: File
    inputBinding:
      position: 1
  rms_input_gro_path:
    type: File
    inputBinding:
      position: 2
  rms_input_trr_path:
    type: File
    inputBinding:
      position: 3
  rms_output_xvg_path:
    type: string
    inputBinding:
      position: 4
    default: "rms.xvg"
  rms_step:
    type: string
    inputBinding:
      position: 5
  rms_properties:
    type: File
    inputBinding:
      position: 6
outputs:
  rms_output_xvg_file:
    type: File
    outputBinding:
      glob: $(inputs.rms_output_xvg_path)
