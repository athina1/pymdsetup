#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - python
inputs:
  gio_script:
    type: File
    inputBinding:
      position: 1
  gio_input_tpr_path:
    type: File
    inputBinding:
      position: 2
  gio_output_gro_path:
    type: string
    inputBinding:
      position: 3
  gio_input_top_tar_path:
    type: File
    inputBinding:
      position: 4
  gio_output_top_tar_path:
    type: string
    inputBinding:
      position: 5
  gio_properties:
    type: string
    inputBinding:
      position: 6

outputs:
  gio_output_gro_file:
    type: File
    outputBinding:
      glob: $(inputs.gio_output_gro_path)
  gio_output_top_tar_file:
    type: File
    outputBinding:
      glob: $(inputs.gio_output_top_tar_path)
