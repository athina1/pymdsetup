rm sol.top sol.gro sol_top.tar p2g.gro p2g_top.tar ec.gro gio.gro gio.top gio_top.tar gppions.tpr gppmin.tpr mdmin.edr mdmin.gro mdmin.trr gppnvt.tpr
cwl-runner pdb2gmx.cwl pdb2gmx_conf.yml
cwl-runner editconf.cwl editconf_conf.yml
cwl-runner solvate.cwl solvate_conf.yml
cwl-runner grompp.cwl gppions_conf.yml
cwl-runner genion.cwl genion_conf.yml
cwl-runner grompp.cwl gppmin_conf.yml
cwl-runner mdrun.cwl mdmin_conf.yml
cwl-runner grompp.cwl gppnvt_conf.yml
