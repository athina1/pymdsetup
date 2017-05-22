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
  gnuplot_mutation:
    type: string
    inputBinding:
      position: 2
  gnuplot_xvg_file_path:
    type: File
    inputBinding:
      position: 3
  gnuplot_output_png_path:
    type: string
    inputBinding:
      position: 4
  gnuplot_output_plotscript_path:
    type: string
    inputBinding:
      position: 5
  gnuplot_gnuplot_path:
    type: string
    inputBinding:
      position: 6
  gnuplot_log_path:
    type: string
    inputBinding:
      position: 7
  gnuplot_error_path:
    type: string
    inputBinding:
      position: 8

outputs:
  gnuplot_output_png_file:
    type: File
    outputBinding:
      glob: $(inputs.gnuplot_output_png_path)
  gnuplot_output_plotscript_file:
    type: File
    outputBinding:
      glob: $(inputs.gnuplot_output_plotscript_path)
