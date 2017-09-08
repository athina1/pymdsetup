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
    default:
      class: File
      location: ../scwrl_wrapper/scwrl.py
  scw_input_pdb_path:
    type: File
    inputBinding:
      position: 2
  scw_output_pdb_path:
    type: string
    inputBinding:
      position: 3
    default: "mutated.pdb"
  scw_step:
    type: string
    inputBinding:
      position: 4
    default: "step3_scw:linux:A.Lys58Glu"
  scw_properties:
    type: File
    inputBinding:
      position: 5
    default:
      class: File
      location: ../workflows/conf_2mut_nt0.yaml
outputs:
  scw_output_pdb_file:
    type: File
    outputBinding:
      glob: $(inputs.scw_output_pdb_path)
