from os.path import join as opj
from test import fixtures as fx
from gromacs_wrapper.solvate import Solvate


class TestSolvate(object):
    def setUp(self):
        fx.test_setup(self,'solvate')

    def tearDown(self):
        fx.test_teardown(self)

    def test_launch(self):
        output_gro_path = opj(self.test_dir, self.properties['output_gro_path'])
        output_top_tar_path = opj(self.test_dir, self.properties['output_top_tar_path'])
        returncode = Solvate(input_solute_gro_path=opj(self.data_dir, self.properties['input_solute_gro_path']),
                             output_gro_path=output_gro_path,
                             input_top_tar_path=opj(self.data_dir, self.properties['input_top_tar_path']),
                             output_top_tar_path=output_top_tar_path,
                             properties=self.properties).launch()
        assert fx.exe_success(returncode)
        assert fx.not_empty(output_gro_path)
        assert fx.not_empty(output_top_tar_path)
