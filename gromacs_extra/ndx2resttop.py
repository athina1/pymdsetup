#!/usr/bin/env python

"""Python module to generate a restrained topology from an index file
"""
import sys
import json
import configuration.settings as settings
from tools import file_utils as fu
import shutil as su
import os
import fnmatch


class Ndx2resttop(object):
    """Generate a restrained topology from an index file.
    Args:
        input_ndx_path (str): Path to the input NDX index file.
        input_top_zip_path (str): Path the input TOP topology in zip format.
        output_top_zip_path (str): Path the output TOP topology in zip format.
        properties (dic):
            output_top_path (str): Path the output TOP file.
            output_itp_path (str): Path to the output include for topology ITP file.
            force_constants (float[3]): Array of three floats defining the force constants.
            chain (str): Chain where the restrain will be applied.
            group (str): Group of the index file where the restrain will be applied.
    """

    def __init__(self, input_ndx_path, input_top_zip_path,
                 output_top_zip_path, properties, **kwargs):
        if isinstance(properties, basestring):
            properties=json.loads(properties)
        self.input_ndx_path = input_ndx_path
        self.input_top_zip_path = input_top_zip_path
        self.output_top_zip_path = output_top_zip_path
        self.output_itp_path = properties.get('output_itp_path','restrain.itp')
        self.output_top_path = properties.get('output_top_path','restrain.top')
        self.force_constants = properties.get('force_constants','500 500 500')
        self.chain = properties.get('chain', None)
        self.gmx_path = properties.get('gmx_path', None)
        self.mutation = properties.get('mutation', None)
        self.group = properties.get('group', None)
        self.step = properties.get('step',None)
        self.path = properties.get('path','')

    def launch(self):
        """Launch the topology generation.
        """
        out_log, err_log = fu.get_logs(path=self.path, mutation=self.mutation, step=self.step)
        self.output_top_path = fu.add_step_mutation_path_to_name(self.output_top_path, self.step, self.mutation)
        self.output_itp_path = fu.add_step_mutation_path_to_name(self.output_itp_path, self.step, self.mutation)

        self.chain = self.chain if self.chain else self.mutation.strip().upper()[0]
        out_log.info('The restrains will be applied over chain: '+self.chain)

        fu.unzip_top(zip_file=self.input_top_zip_path, top_file=self.output_top_path)
        out_log.info('Unzip: '+ self.input_top_zip_path + ' to: '+self.output_top_path)

        index_dic={}
        lines = open(self.input_ndx_path,'r').read().splitlines()
        for index, line in enumerate(lines):
            if line.startswith('['):
                index_dic[line] = index,
                if index > 0:
                    index_dic[label] = index_dic[label][0], index
                label = line

        complete_chain_list = [ int(elem) for line in lines[index_dic['[ Chain_'+self.chain+' ]'][0]+1: index_dic['[ Chain_'+self.chain+' ]'][1]] for elem in line.split() ]
        group_list = [ int(elem) for line in lines[index_dic['[ '+self.group+' ]'][0]+1: index_dic['[ '+self.group+' ]'][1]] for elem in line.split() ]
        selected_list = [complete_chain_list.index(atom)+1 for atom in group_list]

        with open(self.output_itp_path, 'w'):
                f.write('[ position_restraints ]\n')
                f.write('; atom  type      fx      fy      fz\n')
                for atom in selected_list:
                    f.write(str(atom)+'     1  '+self.force_constants)

        for f in os.listdir('.'):
            if not f.startswith("posre"):
                if fnmatch.fnmatch(f, "posre_*_chain_"+self.chain+".itp"):
                    with open(f, 'a'):
                        out_log.info('Opening: '+f+' and adding the ifdef include statement')
                        f.write('\n')
                        f.write('; Include Position restraint file\n')
                        f.write('#ifdef CUSTOM_POSRES\n')
                        f.write('#include "'+self.output_itp_path+'"\n')
                        f.write('#endif\n')




        # zip topology
        fu.zip_top(self.output_top_path, self.output_top_zip_path)
        out_log.info('Zip: '+ self.output_top_path +' to: '+ self.output_top_zip_path)

        return returncode
#Creating a main function to be compatible with CWL
def main():
    system=sys.argv[1]
    step=sys.argv[2]
    properties_file=sys.argv[3]
    prop = settings.YamlReader(properties_file, system).get_prop_dic()[step]
    Pdb2gmx(input_structure_pdb_path=sys.argv[4],
            output_gro_path=sys.argv[5],
            output_top_zip_path=sys.argv[6],
            properties=prop).launch()

if __name__ == '__main__':
    main()
