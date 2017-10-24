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
    default:
      class: File
      location: ../gromacs_wrapper/genion.py
  gio_input_tpr_path:
    type: File
    inputBinding:
      position: 2
  gio_output_gro_path:
    type: string
    inputBinding:
      position: 3
    default: "gio.gro"
  gio_input_top_zip_path:
    type: File
    inputBinding:
      position: 4
  gio_output_top_zip_path:
    type: string
    inputBinding:
      position: 5
    default: "gio_zip.top"
  gio_step:
    type: string
    inputBinding:
      position: 6
    default: "step8_gio:linux"
  gio_properties:
    type: File
    inputBinding:
      position: 7
    default:
      class: File
      location: "../workflows/conf_2mut_nt0.yaml"

outputs:
  gio_output_gro_file:
    type: File
    outputBinding:
      glob: $(inputs.gio_output_gro_path)
  gio_output_top_zip_file:
    type: File
    outputBinding:
      glob: $(inputs.gio_output_top_zip_path)
