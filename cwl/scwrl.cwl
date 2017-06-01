#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool

baseCommand:
  - python
inputs:
  scw_script:
    type: File
    inputBinding:
      position: 1
  scw_input_pdb_path:
    type: File
    inputBinding:
      position: 2
  scw_output_pdb_path:
    type: string
    inputBinding:
      position: 3
  scw_mutation:
    type: string
    inputBinding:
      position: 4
  scw_path:
    type: string
    inputBinding:
      position: 5
  scw_log_path:
    type: string
    inputBinding:
      position: 6
  scw_error_path:
    type: string
    inputBinding:
      position: 7

outputs:
  scw_output_pdb_file:
    type: File
    outputBinding:
      glob: $(inputs.scw_output_pdb_path)