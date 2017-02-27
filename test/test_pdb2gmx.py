"""Unittests for gromacs_wrapper.pdb2gmx module
"""
import os
import sys
import shutil
import unittest
from os.path import join as opj
from pymdsetup.configuration import settings
from pymdsetup.tools import file_utils as fu
from pymdsetup.gromacs_wrapper.pdb2gmx import Pdb2gmx512


class TestPdb2gmx512(unittest.TestCase):
    """Unittests for the gromacs_wrapper.pdb2gmx.Pdb2gmx512 class.
    """

    def setUp(self):
        self.sys_paths = 'linux'
        conf_dir = os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))
        conf = settings.YamlReader(yaml_path=(os.path.join(conf_dir, 'conf_test.yaml')))
        self.prop = conf.properties
        self.root_dir=self.prop[self.sys_paths]['pymdsetup_path']
        self.p_p2g = conf.step_prop('p2g', self.prop[self.sys_paths]['test_path'])
        fu.create_change_dir(self.p_p2g.path)

    def tearDown(self):
        # Remove all files in the temp_results directory
        shutil.rmtree(self.p_p2g.path)

    def test_launch(self):
        Pdb2gmx512(input_structure_pdb_path=opj(self.root_dir, self.prop['p2g']['paths']['in_pdb']),
                   output_gro_path=self.p_p2g.gro,
                   output_top_path=self.p_p2g.top,
                   output_top_tar_path=self.p_p2g.tar,
                   water_type=self.p_p2g.water_type,
                   force_field=self.p_p2g.force_field,
                   ignh=settings.str2bool(self.p_p2g.ignh),
                   gmx_path=self.prop[self.sys_paths]['gmx_path'],
                   log_path=self.p_p2g.out, error_path=self.p_p2g.err).launch()

        print self.p_p2g.out
        with open(self.p_p2g.gro, 'r') as out_gro, open(opj(self.root_dir, self.prop['p2g']['paths']['gold_gro']), 'r') as gold_gro:
            self.assertMultiLineEqual(out_gro.read(), gold_gro.read())

        with open(self.p_p2g.top, 'r') as out_top, open(opj(self.root_dir, self.prop['p2g']['paths']['gold_top']), 'r') as gold_top:
            out_top_list = " ".join([line if not line.startswith(';') else '' for line in out_top])
            out_top_gold_list = " ".join([line if not line.startswith(';') else '' for line in gold_top])
            self.assertItemsEqual(out_top_list, out_top_gold_list)

        with open(self.p_p2g.itp, 'r') as out_itp, open(opj(self.root_dir, self.prop['p2g']['paths']['gold_itp']), 'r') as gold_itp:
            out_itp_list = " ".join([line if not line.startswith(';') else '' for line in out_itp])
            out_itp_gold_list = " ".join([line if not line.startswith(';') else '' for line in gold_itp])
            self.assertItemsEqual(out_itp_list, out_itp_gold_list)

if __name__ == '__main__':
    unittest.main()
