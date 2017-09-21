"""Unittests for gromacs_wrapper.pdb2gmx module
"""
import os
import sys
import shutil
from os.path import join as opj
from configuration import settings
from gromacs_wrapper.pdb2gmx import Pdb2gmx

class TestPdb2gmx(object):
    """Unittests for the gromacs_wrapper.pdb2gmx.Pdb2gmx class.
    """
    def setUp(self):
        test_dir = self.__class__.__name__
        data_dir = os.path.dirname(os.path.abspath(sys.modules[__name__].__file__))
        self.yaml_path= opj(data_dir, 'conf.yaml')
        self.system=os.getenv('testsys')
        if self.system is None:
            print 'WARNING: "testsys" env variable should be set, "linux" will be used by default value.'
            self.system='linux'
        conf = settings.YamlReader(self.yaml_path, self.system)
        self.properties = conf.get_prop_dic()
        self.paths = conf.get_paths_dic()

    def tearDown(self):
        pass
        #shutil.rmtree(self.p_p2g.h)

    def test_launch(self):
        print self.properties
        print self.paths
        # Pdb2gmx(input_structure_pdb_path=opj(self.root_dir, self.prop['p2g']['paths']['in_pdb']),
        #            output_gro_path=self.p_p2g.gro,
        #            output_top_path=self.p_p2g.top,
        #            output_itp_path=self.prop['p2g']['paths']['itp'],
        #            output_top_tar_path=self.p_p2g.tar,
        #            water_type=self.p_p2g.water_type,
        #            force_field=self.p_p2g.force_field,
        #            ignh=settings.str2bool(self.p_p2g.ignh),
        #            gmx_path=self.prop['gmx_path'],
        #            log_path=self.p_p2g.out, error_path=self.p_p2g.err).launch()
        #
        # print self.p_p2g.out
        # with open(self.p_p2g.gro, 'r') as out_gro, open(opj(self.root_dir, self.prop['p2g']['paths']['gold_gro']), 'r') as gold_gro:
        #     self.assertMultiLineEqual(out_gro.read(), gold_gro.read())
        #
        # with open(self.p_p2g.top, 'r') as out_top, open(opj(self.root_dir, self.prop['p2g']['paths']['gold_top']), 'r') as gold_top:
        #     out_top_list = " ".join([line if not line.startswith(';') else '' for line in out_top])
        #     out_top_gold_list = " ".join([line if not line.startswith(';') else '' for line in gold_top])
        #     self.assertItemsEqual(out_top_list, out_top_gold_list)
        #
        # with open(self.p_p2g.itp, 'r') as out_itp, open(opj(self.root_dir, self.prop['p2g']['paths']['gold_itp']), 'r') as gold_itp:
        #     out_itp_list = " ".join([line if not line.startswith(';') else '' for line in out_itp])
        #     out_itp_gold_list = " ".join([line if not line.startswith(';') else '' for line in gold_itp])
        #     self.assertItemsEqual(out_itp_list, out_itp_gold_list)
