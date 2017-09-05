rm sol.top sol.gro sol_top.tar p2g.gro p2g_top.tar ec.gro gio.gro gio.top gio_top.tar gppions.tpr gppmin.tpr mdmin.edr mdmin.gro mdmin.trr gppnvt.tpr test_* test/mutated.pdb
cwl-runner scwrl.cwl test/scwrl_conf.yml
cwl-runner editconf.cwl test/editconf_conf.yml
cwl-runner solvate.cwl test/solvate_conf.yml
cwl-runner grompp.cwl test/gppions_conf.yml
cwl-runner genion.cwl test/genion_conf.yml
cwl-runner grompp.cwl test/gppmin_conf.yml
cwl-runner mdrun.cwl test/mdmin_conf.yml
cwl-runner grompp.cwl test/gppnvt_conf.yml
