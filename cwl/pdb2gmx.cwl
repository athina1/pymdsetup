#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand:
  - python
inputs:
  p2g_script:
    type: File
    inputBinding:
      position: 1
  p2g_input_structure_pdb_path:
    type: File
    format: http://edamontology.org/format_1476 #PDB format from EDAM
    inputBinding:
      position: 2
  p2g_output_gro_path:
    type: string
    inputBinding:
      position: 3
    default: "p2g.gro"
  p2g_output_top_tar_path:
    type: string
    inputBinding:
      position: 4
    default: "p2g_top.tar"
  p2g_step:
    type: string
    inputBinding:
      position: 5
  p2g_properties:
    type: File
    inputBinding:
      position: 6
outputs:
  p2g_output_gro_file:
    type: File
    outputBinding:
      glob: $(inputs.p2g_output_gro_path)
  p2g_output_top_tar_file:
    type: File
    outputBinding:
      glob: $(inputs.p2g_output_top_tar_path)
