#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - python
inputs:
  gnuplot_script:
    type: File
    inputBinding:
      position: 1
  gnuplot_input_xvg_path_dict:
    type: string
    inputBinding:
      position: 2
  gnuplot_output_png_path:
    type: File
    inputBinding:
      position: 3
  gnuplot_properties:
    type: string
    inputBinding:
      position: 4
outputs:
  gnuplot_output_png_file:
    type: File
    outputBinding:
      glob: $(inputs.gnuplot_output_png_path)
