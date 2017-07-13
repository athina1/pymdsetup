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
  scw_config_string:
    type: string
    inputBinding:
      position: 4
      
outputs:
  scw_output_pdb_file:
    type: File
    outputBinding:
      glob: $(inputs.scw_output_pdb_path)
