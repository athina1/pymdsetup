#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - extract.py
inputs:
  input_gro_path:
    type: File
    inputBinding:
      position: 1
  input_trr_path:
    type: File
    inputBinding:
      position: 2

outputs:
  ec_output_gro_file:
    type: File
    outputBinding:
      glob: refined_structure.pdb
