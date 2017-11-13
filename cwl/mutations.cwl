#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow

inputs:
  scw_input_pdb_path: File

outputs:
  gnuplot_output_png_file:
     type: File
     outputSource: gnuplot/gnuplot_output_png_file
  rms_output_xvg_file:
     type: File
     outputSource: rmsd/rms_output_xvg_file
  md_output_gro_file:
    type: File
    outputSource: equilibration/md_output_gro_file
  md_output_trr_file:
    type: File
    outputSource: equilibration/md_output_trr_file

steps:
  mutate_structure:
    run: scwrl.cwl
    in:
      system:
        default: linux
      step:
        default: scwrl
      properties_file:
        default: test/conf_1ps.yaml
      scw_input_pdb_path: scw_input_pdb_path
    out: [scw_output_pdb_file]

  create_topology:
    run: pdb2gmx.cwl
    in:
      system:
        default: linux
      step:
        default: pdb2gmx
      properties_file:
        default: test/conf_1ps.yaml
      p2g_input_structure_pdb_path: mutate_structure/scw_output_pdb_file
    out: [p2g_output_gro_file, p2g_output_top_zip_file]

  create_water_box:
    run: editconf.cwl
    in:
      system:
        default: linux
      step:
        default: editconf
      properties_file:
        default: test/conf_1ps.yaml
      ec_input_gro_path: create_topology/p2g_output_gro_file
    out: [ec_output_gro_file]

  solvate:
    run: solvate.cwl
    in:
      system:
        default: linux
      step:
        default: solvate
      properties_file:
        default: test/conf_1ps.yaml
      sol_input_solute_gro_path: create_water_box/ec_output_gro_file
      sol_input_top_zip_path: create_topology/p2g_output_top_zip_file
    out: [sol_output_gro_file, sol_output_top_zip_file]

  ions_preprocess:
    run: grompp.cwl
    in:
      system:
        default: linux
      step:
        default: gppions
      properties_file:
        default: test/conf_1ps.yaml
      gpp_input_gro_path: solvate/sol_output_gro_file
      gpp_input_top_zip_path: solvate/sol_output_top_zip_file
      gpp_input_mdp_path:
        default:
          class: File
          location: ../workflows/mdp/gmx_full_ions_test.mdp
    out: [gpp_output_tpr_file]

  add_ions:
    run: genion.cwl
    in:
      system:
        default: linux
      step:
        default: genion
      properties_file:
        default: test/conf_1ps.yaml
      gio_input_tpr_path: ions_preprocess/gpp_output_tpr_file
      gio_input_gro_path: solvate/sol_output_gro_file
      gio_input_top_zip_path: solvate/sol_output_top_zip_file
    out: [gio_output_gro_file, gio_output_top_zip_file]

  minimization_preprocess:
    run: grompp.cwl
    in:
      system:
        default: linux
      step:
        default: gppmin
      properties_file:
        default: test/conf_1ps.yaml
      gpp_input_gro_path: add_ions/gio_output_gro_file
      gpp_input_top_zip_path: add_ions/gio_output_top_zip_file
      gpp_input_mdp_path:
        default:
          class: File
          location: ../workflows/mdp/gmx_full_min_test.mdp
    out: [gpp_output_tpr_file]

  minimization:
    run: mdrun.cwl
    in:
      system:
        default: linux
      step:
        default: mdmin
      properties_file:
        default: test/conf_1ps.yaml
      md_input_tpr_path: minimization_preprocess/gpp_output_tpr_file
    out: [md_output_gro_file, md_output_trr_file]

  nvt_dynamics_preprocess:
    run: grompp.cwl
    in:
      system:
        default: linux
      step:
        default: gppnvt
      properties_file:
        default: test/conf_1ps.yaml
      gpp_input_gro_path: minimization/md_output_gro_file
      gpp_input_top_zip_path: add_ions/gio_output_top_zip_file
      gpp_input_mdp_path:
        default:
          class: File
          location: ../workflows/mdp/gmx_full_nvt_test.mdp
    out: [gpp_output_tpr_file]

  nvt_dynamics:
    run: mdrun.cwl
    in:
      system:
        default: linux
      step:
        default: mdnvt
      properties_file:
        default: test/conf_1ps.yaml
      md_input_tpr_path: nvt_dynamics_preprocess/gpp_output_tpr_file
    out: [md_output_gro_file, md_output_trr_file, md_output_cpt_file]

  npt_dynamics_preprocess:
    run: grompp.cwl
    in:
      system:
        default: linux
      step:
        default: gppnpt
      properties_file:
        default: test/conf_1ps.yaml
      gpp_input_gro_path: nvt_dynamics/md_output_gro_file
      gpp_input_top_zip_path: add_ions/gio_output_top_zip_file
      gpp_input_cpt_path: nvt_dynamics/md_output_cpt_file
      gpp_input_mdp_path:
        default:
          class: File
          location: ../workflows/mdp/gmx_full_npt_test.mdp
    out: [gpp_output_tpr_file]

  npt_dynamics:
    run: mdrun.cwl
    in:
      system:
        default: linux
      step:
        default: mdnpt
      properties_file:
        default: test/conf_1ps.yaml
      md_input_tpr_path: npt_dynamics_preprocess/gpp_output_tpr_file
    out: [md_output_gro_file, md_output_trr_file, md_output_cpt_file]

  equilibration_preprocess:
    run: grompp.cwl
    in:
      system:
        default: linux
      step:
        default: gppeq
      properties_file:
        default: test/conf_1ps.yaml
      gpp_input_gro_path: npt_dynamics/md_output_gro_file
      gpp_input_top_zip_path: add_ions/gio_output_top_zip_file
      gpp_input_cpt_path: npt_dynamics/md_output_cpt_file
      gpp_input_mdp_path:
        default:
          class: File
          location: ../workflows/mdp/gmx_full_md_test.mdp
    out: [gpp_output_tpr_file]

  equilibration:
    run: mdrun.cwl
    in:
      system:
        default: linux
      step:
        default: mdeq
      properties_file:
        default: test/conf_1ps.yaml
      md_input_tpr_path: equilibration_preprocess/gpp_output_tpr_file
    out: [md_output_gro_file, md_output_trr_file, md_output_cpt_file]

  rmsd:
    run: rms.cwl
    in:
      system:
        default: linux
      step:
        default: rms
      properties_file:
        default: test/conf_1ps.yaml
      rms_input_gro_path: equilibration/md_output_gro_file
      rms_input_trr_path: equilibration/md_output_trr_file
    out: [rms_output_xvg_file]

  gnuplot:
    run: gnuplot.cwl
    in:
      system:
        default: linux
      step:
        default: gnuplot
      properties_file:
        default: test/conf_1ps.yaml
      gnuplot_input_xvg_path: rmsd/rms_output_xvg_file
    out: [gnuplot_output_png_file]
