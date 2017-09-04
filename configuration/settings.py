# -*- coding: utf-8 -*-
"""Settings loader module.

This module contains the classes to read the different formats of the
configuration files.

The configuration file path should be specified in the PYMDS_CONF environment
variable.

@author: pau
"""

import yaml
import os
import logging
from os.path import join as opj
import tools.file_utils as fu

class YamlReader(object):
    """Configuration file loader for yaml format files.
    """

    def __init__(self, yaml_path, system):
        self.yaml_path= os.path.abspath(yaml_path)
        self.system = system
        self.properties = self._read_yaml()
        self.properties[system]['workflow_path'] = fu.get_workflow_path(self.properties[system]['workflow_path'])

    def _read_yaml(self):
        with open(self.yaml_path, 'r') as stream:
            return yaml.load(stream)

    def get_prop_dic(self, mutation=None):
        if mutation is None:
            mutation = ''
        prop_dic = dict()

        #Filtering just properties
        for key in self.properties:
            if isinstance(self.properties[key], dict):
                if 'paths' in self.properties[key] or 'properties' in self.properties[key]:
                    prop_dic[key]={'path': opj(self.properties[self.system]['workflow_path'], mutation, key)}
                    prop_dic[key]['mutation']=mutation
                    prop_dic[key].update(self.properties[self.system].copy())
                if 'properties' in self.properties[key] and isinstance(self.properties[key]['properties'], dict):
                    prop_dic[key].update(self.properties[key]['properties'].copy())

        return prop_dic

    def get_paths_dic(self, mutation=None):
        if mutation is None:
            mutation = ''
        prop_dic = dict()

        #Filtering just paths
        for key in self.properties:
            if isinstance(self.properties[key], dict):
                if 'paths' in self.properties[key]:
                    prop_dic[key]=self.properties[key]['paths'].copy()

        #Solving dependencies
        for key in prop_dic:
            for key2, value in prop_dic[key].iteritems():
                while isinstance(value, basestring) and value.startswith('dependency'):
                    value = prop_dic[value.split('/')[1]][value.split('/')[2]]
                prop_dic[key][key2] = value

        #Adding paths
        for key in prop_dic:
            for key2, value in prop_dic[key].iteritems():
                prop_dic[key][key2] = opj(self.properties[self.system]['workflow_path'], mutation, key, value)

        return prop_dic


    def step_prop_dic(self, step, workflow_path, mutation=None, add_workflow_path=True):
        self.properties = self._read_yaml()
        dp = self.properties[step]

        #Adding system paths
        if self.system is not None:
            for key, value in self.properties[self.system].iteritems():
                dp[key]=value

        #Adding mutation
        if mutation is not None:
            dp['mutation']=mutation

        if 'paths' in dp:
            if add_workflow_path:
                if mutation is None:
                    dp['path'] = opj(workflow_path, dp['paths']['path'])
                else:
                    dp['path'] = opj(workflow_path, mutation, dp['paths']['path'])

                for key, value in dp['paths'].iteritems():
                    #solving dependencies
                    if isinstance(value, basestring) and value.startswith('dependency'):
                        dp[key] = self.step_prop_dic(value.split('/')[1], workflow_path, mutation)[value.split('/')[2]]
                    elif key == 'input_mdp_path':
                        dp[key] = opj(dp['mdp_path'],dp['paths'][key])
                    elif key != 'path':
                        dp[key] = opj(dp['path'], dp['paths'][key])
            else:
                for key, value in dp['paths'].iteritems():
                    #solving dependencies
                    if isinstance(value, basestring) and value.startswith('dependency'):
                        dp[key] = self.step_prop_dic(value.split('/')[1], workflow_path, mutation, False)[value.split('/')[2]]
                    elif key == 'input_mdp_path':
                        dp[key] = dp['paths'][key]
                    elif key != 'path':
                        dp[key] = dp['paths'][key]


        if 'properties' in dp:
            for key, value in dp['properties'].iteritems():
                #solving dependencies
                if isinstance(value, basestring) and value.startswith('dependency'):
                    dp[key] = self.step_prop_dic(value.split('/')[1], workflow_path, mutation)[value.split('/')[2]]
                #casting booleans
                elif isinstance(value, basestring) and value.lower() in ('true', 'false'):
                    dp[key]=str2bool(value)
                else:
                    dp[key] = dp['properties'][key]

        dp.pop('paths', None)
        dp.pop('properties', None)

        for key, value in dp.iteritems():
            dp[key] = str(value)

        return dp

def str2bool(v):
    if isinstance(v, bool):
            return v
    return v.lower() in ("true")

def get_logs(path, console=False):
    if path is None or not os.path.isdir(path):
        path = ''
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    out_Logger = logging.getLogger(opj(path, "out.log"))
    err_Logger = logging.getLogger(opj(path, "err.log"))
    out_fileHandler = logging.FileHandler(opj(path, "out.log"), mode='a', encoding=None, delay=False)
    err_fileHandler = logging.FileHandler(opj(path, "err.log"), mode='a', encoding=None, delay=False)
    out_fileHandler.setFormatter(logFormatter)
    err_fileHandler.setFormatter(logFormatter)
    out_Logger.addHandler(out_fileHandler)
    err_Logger.addHandler(err_fileHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    # Adding console aditional output
    if console:
        out_Logger.addHandler(consoleHandler)
        err_Logger.addHandler(consoleHandler)
    out_Logger.setLevel(10)
    err_Logger.setLevel(10)
    return out_Logger, err_Logger
