#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - scwrl.py
inputs:
  scw_input_pdb_path:
    type: File
    inputBinding:
      position: 1
  scw_output_pdb_path:
    type: string
    inputBinding:
      position: 2
    default: "mutated.pdb"
  scw_step:
    type: string
    inputBinding:
      position: 3
    default: "step3_scw:linux:A.Lys58Glu"
  scw_properties:
    type: File
    inputBinding:
      position: 4
    default:
      class: File
      location: ../workflows/conf/conf_2mut_nt0_1ps.yaml
outputs:
  scw_output_pdb_file:
    type: File
    outputBinding:
      glob: $(inputs.scw_output_pdb_path)
