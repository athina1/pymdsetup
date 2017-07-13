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
from os.path import join as opj


class YamlReader(object):
    """Configuration file loader for yaml format files.

    The path for the configuration file path should be provided by an argument
    in the constructor or the 'PYMDS_CONF' environment variable.
    If none of the two is provided the default path will be './conf.yaml'
    """

    def __init__(self, yaml_path=None, system=None):
        if yaml_path is not None:
            self.yaml_path = yaml_path
        elif os.environ.get('PYMDS_CONF') is not None:
            self.yaml_path = os.environ.get('PYMDS_CONF')
        else:
            self.yaml_path = 'conf.yaml'

        self.system = system
        self.yaml_path= os.path.abspath(self.yaml_path)
        self.properties = self._read_yaml()

    def _read_yaml(self):
        with open(self.yaml_path, 'r') as stream:
            return yaml.load(stream)

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

        return dp

    def step_prop_obj(self, step, workflow_path, mutation):
        class Dict2Obj(object):
            def __init__(self, dictionary):
                for key in dictionary:
                    setattr(self, key, dictionary[key])
        return Dict2Obj(self.step_prop_dic(step, workflow_path, mutation))

def str2bool(v):
    if isinstance(v, bool):
            return v
    return v.lower() in ("true")
