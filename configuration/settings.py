# -*- coding: utf-8 -*-
"""Settings loader module.

This module contains the classes to read the different formats of the
configuration files.

The configuration file path should be specified in the PYMDS_CONF environment
variable.
"""

import yaml
import os
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
                    prop_dic[key]['step']= key
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

        #Solving dependencies and adding workflow and step path
        for key in prop_dic:
            for key2, value in prop_dic[key].iteritems():
                if isinstance(value, basestring) and value.startswith('dependency'):
                    while isinstance(value, basestring) and value.startswith('dependency'):
                        dependency_step=value.split('/')[1]
                        value = prop_dic[value.split('/')[1]][value.split('/')[2]]
                    prop_dic[key][key2] = opj(self.properties[self.system]['workflow_path'], mutation, dependency_step, value)
                elif isinstance(key2, basestring) and key2 == 'input_mdp_path':
                    prop_dic[key][key2] = opj(self.properties[self.system]['mdp_path'], value)
                else:
                    prop_dic[key][key2] = opj(self.properties[self.system]['workflow_path'], mutation, key, value)
        return prop_dic
