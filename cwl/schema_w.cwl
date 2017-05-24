#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow

inputs:
  scw_input_pdb_path: File
  scw_mutation: string


outputs:
  gnuplot_output_png_file:
     type: File
     outputSource: gnuplot/gnuplot_output_png_file
  rms_output_xvg_file:
     type: File
     outputSource: rms/rms_output_xvg_file
  md_output_gro_file:
    type: File
    outputSource: mdeq/md_output_gro_file
  md_output_xtc_file:
    type: File
    outputSource: mdeq/md_output_xtc_file

steps:
  scwrl:
    run: scwrl.cwl
    in:
      scw_input_pdb_path: scw_input_pdb_path
      scw_mutation: scw_mutation
    out: [scw_output_pdb_file]
  pdb2gmx:
    run: pdb2gmx.cwl
    in:
      p2g_input_structure_pdb_path: scwrl/scw_output_pdb_file
    out: [p2g_output_gro_file, p2g_output_top_tar_file]

  editconf:
    run: editconf.cwl
    in:
      ec_input_gro_path: pdb2gmx/p2g_output_gro_file
    out: [ec_output_gro_file]

  solvate:
    run: solvate.cwl
    in:
      sol_input_solute_gro_path: editconf/ec_output_gro_file
      sol_input_top_tar_path: pdb2gmx/p2g_output_top_tar_file
    out: [sol_output_gro_file, sol_output_top_tar_file]

  gppions:
    run: grompp.cwl
    in:
      gpp_input_gro_path: solvate/sol_output_gro_file
      gpp_input_top_tar_path: solvate/sol_output_top_tar_file
    out: [gpp_output_tpr_file]

  genion:
    run: genion.cwl
    in:
      gio_input_tpr_path: gppions/gpp_output_tpr_file
      gio_input_gro_path: solvate/sol_output_gro_file
      gio_input_top_tar_path: solvate/sol_output_top_tar_file
    out: [gio_output_gro_file, gio_output_top_tar_file]

  gppmin:
    run: grompp.cwl
    in:
      gpp_input_gro_path: genion/gio_output_gro_file
      gpp_input_top_tar_path: genion/gio_output_top_tar_file
    out: [gpp_output_tpr_file]

  mdmin:
    run: mdrun.cwl
    in:
      md_input_tpr_path: gppmin/gpp_output_tpr_file
    out: [md_output_gro_file]

  gppnvt:
    run: grompp.cwl
    in:
      gpp_input_gro_path: mdmin/md_output_gro_file
      gpp_input_top_tar_path: genion/gio_output_top_tar_file
    out: [gpp_output_tpr_file]

  mdnvt:
    run: mdrun.cwl
    in:
      md_input_tpr_path: gppnvt/gpp_output_tpr_file
    out: [md_output_gro_file, md_output_cpt_file]

  gppnpt:
    run: grompp.cwl
    in:
      gpp_input_gro_path: mdnvt/md_output_gro_file
      gpp_input_top_tar_path: genion/gio_output_top_tar_file
      gpp_input_cpt_path: mdnvt/md_output_cpt_file
    out: [gpp_output_tpr_file]

  mdnpt:
    run: mdrun.cwl
    in:
      md_input_tpr_path: gppnpt/gpp_output_tpr_file
    out: [md_output_gro_file, md_output_cpt_file]

  gppeq:
    run: grompp.cwl
    in:
      gpp_input_gro_path: mdnpt/md_output_gro_file
      gpp_input_top_tar_path: genion/gio_output_top_tar_file
      gpp_input_cpt_path: mdnpt/md_output_cpt_file
    out: [gpp_output_tpr_file]

  mdeq:
    run: mdrun.cwl
    in:
      md_input_tpr_path: gppeq/gpp_output_tpr_file
    out: [md_output_gro_file, md_output_xtc_file]

  rms:
    run: rms.cwl
    in:
      rms_input_gro_path: mdeq/md_output_gro_file
      rms_input_trr_path: mdeq/md_output_trr_file
    out: [rms_output_xvg_file]

  gnuplot:
    run: gnuplot.cwl
    in:
      gnuplot_mutation: scw_mutation
      gnuplot_xvg_file_path: rms/rms_output_xvg_file
    out: [gnuplot_output_png_file]
