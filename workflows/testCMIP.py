#! /usr/bin/python
"""Python wrapper module for CMIP
"""
__author__ = "gelpi"
__date__ = "$24-nov-2017 12:30:59$"

import time
import sys
import os
import configuration.settings as settings
import tools.file_utils as fu
import cmip_wrapper.CMIPWrapper as CMIPWrapper

def main():
    start_time = time.time()
    yaml_path=sys.argv[1]
    system=sys.argv[2]
    conf = settings.YamlReader(yaml_path, system)
    workflow_path = conf.properties[system]['workflow_path']
    fu.create_dir(os.path.abspath(workflow_path))
    out_log, _ = fu.get_logs(path=workflow_path, console=True)
    paths = conf.get_paths_dic()
    props = conf.get_prop_dic(global_log=out_log)

    out_log.info('')
    out_log.info('_______TEST CMIP TITRATION WORKFLOW_______')
    out_log.info('')

    out_log.info('step3:  CMIPTitration')
    props['step'] = 'step3_CMIPTitration'
    fu.create_dir(props['step3_CMIPTitration']['path'])
    CMIPWrapper(paths['step3_CMIPTitration'],props['step3_CMIPTitration']).launch()

    out_log.info('')

    elapsed_time = time.time() - start_time
    out_log.info('')
    out_log.info('')
    out_log.info('Execution sucessful: ')
    out_log.info('  Workflow_path: '+workflow_path)
    out_log.info('  Config File: '+yaml_path)
    out_log.info('  System: '+system)
    if len(sys.argv) >= 4:
        out_log.info('  Nodes: '+sys.argv[3])
    out_log.info('')
    out_log.info('Elapsed time: '+str(elapsed_time)+' seconds')
    out_log.info('')


if __name__ == "__main__":
    main()
