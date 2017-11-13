#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - replace.py
inputs:
  pdb_structure:
    type: File
    inputBinding:
      position: 1

outputs:
  ec_output_gro_file:
    type: File
    outputBinding:
      glob: fixed.pdb
