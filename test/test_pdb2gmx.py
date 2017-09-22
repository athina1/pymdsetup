"""Unittests for gromacs_wrapper.pdb2gmx module
"""
import os
import sys
import shutil
from os.path import join as opj
from configuration import settings
from gromacs_wrapper.pdb2gmx import Pdb2gmx
from tools import file_utils as fu
from os.path import isfile
from os.path import getsize

class TestPdb2gmx(object):
    """Unittests for the gromacs_wrapper.pdb2gmx.Pdb2gmx class.
    """
    def setUp(self):
        self.test_dir = self.__class__.__name__
        fu.create_dir(self.test_dir)
        self.data_dir = opj(os.path.dirname(os.path.abspath(sys.modules[__name__].__file__)),'data')
        self.yaml_path= opj(self.data_dir, 'conf.yaml')
        self.system=os.getenv('testsys')
        if self.system is None:
            print 'WARNING: "testsys" env variable should be set, "linux" will be used by default value.'
            print '     try "export testsys=linux"'
            self.system='linux'
        conf = settings.YamlReader(self.yaml_path, self.system)
        self.properties = conf.get_prop_dic()['pdb2gmx']

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        fu.remove_temp_files(['#', '.top', '.plotscript', '.edr', '.xtc', '.itp', '.top', '.log', '.pdb', '.cpt', '.mdp'])

    def test_launch(self):
        output_gro_path=opj(self.test_dir, self.properties['output_gro_path'])
        output_top_tar_path=opj(self.test_dir, self.properties['output_top_tar_path'])
        returncode = Pdb2gmx(input_structure_pdb_path=opj(self.data_dir, self.properties['input_structure_pdb_path']),
                             output_gro_path=output_gro_path,
                             output_top_tar_path=output_top_tar_path,
                             properties=self.properties).launch()

        assert returncode == 0
        assert ( os.path.isfile(output_gro_path) and os.path.getsize(output_gro_path) > 0 )
        assert ( os.path.isfile(output_top_tar_path) and os.path.getsize(output_top_tar_path) > 0 )
