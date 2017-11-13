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
    default:
      class: File
      location: ../gnuplot_wrapper/gnuplot.py
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
    default: "step18_gnuplot:linux"
  gnuplot_properties:
    type: File
    inputBinding:
      position: 5
    default:
      class: File
      location: "../workflows/conf_2mut_nt0.yaml"
outputs:
  gnuplot_output_png_file:
    type: File
    outputBinding:
      glob: $(inputs.gnuplot_output_png_path)
