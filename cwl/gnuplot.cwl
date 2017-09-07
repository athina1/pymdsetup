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
  gnuplot_input_xvg_path:
    type: File
    inputBinding:
      position: 2
  gnuplot_output_png_path:
    type: string
    inputBinding:
      position: 3
    default: "gnuplot.png"
  gnuplot_step:
    type: string
    inputBinding:
      position: 4
  gnuplot_properties:
    type: File
    inputBinding:
      position: 5
outputs:
  gnuplot_output_png_file:
    type: File
    outputBinding:
      glob: $(inputs.gnuplot_output_png_path)
