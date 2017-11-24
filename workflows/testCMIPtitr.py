"""
Test CMIP wrappers: titration
"""

import os
import sys
import time
import shutil
from os.path import join as opj
from command_wrapper import cmd_wrapper
import tools.file_utils as fu
import configuration.settings as settings
import cmip_wrapper.titration as titration

def main():
    start_time = time.time()
    structure_pdb_path_in=os.path.abspath(sys.argv[1])
    structure_pdb_path_out=os.path.abspath(sys.argv[2])
    yaml_path='/data/DEVEL/BioExcel/pymdsetup/workflows/conf/testCMIPtitration.yaml'
    system='linux'
    conf = settings.YamlReader(yaml_path, system)
    workflow_path = conf.properties[system]['workflow_path']
    fu.create_dir(os.path.abspath(workflow_path))
    out_log, _ = fu.get_logs(path=workflow_path, console=True)
    paths = conf.get_paths_dic()
    prop = conf.get_prop_dic(global_log=out_log)
    #TODO: Source of problems
    #Change directories always creates problems
    os.chdir(workflow_path)

    out_log.info('\n\n_______CMIP_titration_______\n\n')

    out_log.info('in ----------- Get PDB structure')
    fu.create_dir(prop['step1_mmbpdb']['path'])
    shutil.copy(structure_pdb_path_in, paths['step1_mmbpdb']['output_pdb_path'])

    out_log.info('pdb2gmx ------ Create gromacs topology')
    fu.create_dir(prop['step2_titration']['path'])
    pdb2gmx.Pdb2gmx(properties=prop['step4_p2g'],
                    input_structure_pdb_path=sed_pdb_path,
                    output_gro_path=paths['step4_p2g']['output_gro_path'],
                    output_top_zip_path=paths['step4_p2g']['output_top_zip_path']).launch()
#TODO

    out_log.info('\n\nExecution sucessful: ')
    out_log.info('  Output_pdb_path: ' + structure_pdb_path_out)
    out_log.info('  Workflow_path: ' + workflow_path)
    out_log.info('  Config File: ' + yaml_path)
    out_log.info('  System: ' + system)
    out_log.info('  Elapsed time: ' + str(elapsed_time) + 'seconds')

if __name__ == '__main__':
    main()
