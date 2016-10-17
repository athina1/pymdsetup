"""Unittests for  ebi_api package
"""
import unittest
from pymdsetup.ebi_api.pdb import EbiPdb
#from pymdsetup.ebi_api.uniprot import EbiVariants
import os
from os.path import join as opj


class TestPdb(unittest.TestCase):
    """Unittests for  ebi_api.pdb module
    """

    def setUp(self):
        self.data_dir = opj(os.path.dirname(__file__), 'data')
        self.results = opj(self.data_dir, "temp_results")

    def tearDown(self):
        # Remove all files in the temp_results directory
        for the_file in os.listdir(self.results):
            file_path = opj(self.results, the_file)
            try:
                # Not removing directories
                if os.path.isfile(file_path) and not the_file == 'README.txt':
                    os.unlink(file_path)
            except Exception, e:
                print e

    def test_get_pdb(self):
        pdb_code = '2ki5'
        output_path = opj(self.results, 'structure.pdb')
        gold_path = opj(self.data_dir, '2ki5_gold.pdb')
        ebi_st = EbiPdb(pdb_code, output_path)
        ebi_st.get_pdb()
        with open(output_path, 'r') as out_file, open(gold_path,
                                                      'r') as gold_file:
            out_string = out_file.read()
            gold_string = gold_file.read()
            # Don't know why use:
            # self.assertMultiLineEqual(out_string,
            #                           gold_string)
            # Prints the whole pdb file in the standar output (screen)
            self.assertMultiLineEqual(out_string[:1000], gold_string[:1000])


# class TestUniprot(unittest.TestCase):
#     """Unittests for  mmb_api.uniprot module
#     """
#
#     def setUp(self):
#         self.data_dir = opj(os.path.dirname(__file__), 'data')
#         self.results = opj(self.data_dir, "temp_results")
#
#     def tearDown(self):
#         # Remove all files in the temp_results directory
#         for the_file in os.listdir(self.results):
#             file_path = opj(self.results, the_file)
#             try:
#                 # Not removing directories
#                 if os.path.isfile(file_path) and not the_file == 'README.txt':
#                     os.unlink(file_path)
#             except Exception, e:
#                 print e
#
#     def test_get_uniprot(self):
#         pdb_code = '3vtv'
#         ebi_var = EbiVariants(pdb_code)
#         uniprot = ebi_var.get_uniprot()
#         uniprot_expected = 'Q96CV9'
#         self.assertEqual(uniprot, uniprot_expected)
#
#     def test_get_variants(self):
#         pdb_code = '3vtv'
#         ebi_var = EbiVariants(pdb_code)
#         variants = ebi_var.get_variants()
#         variants_expected = ['p.His26Asp', 'p.Glu50Lys']
#         self.assertEqual(variants[:2], variants_expected)
#
#     # TODO: Not implemented yet
#     # pymdsetup.mmb_api.uniprot.MmbVariants.get_pdb_variants() used instead
#     # def test_get_pdb_variants(self):
#     #     pdb_code = '2vgb'
#     #     ebi_var = EbiVariants(pdb_code)
#     #     variants = ebi_var.get_pdb_variants()
#     #     variants_expected = ['A.Met107Thr', 'B.Met107Thr']
#     #     self.assertEqual(variants[:2], variants_expected)
#

if __name__ == '__main__':
    unittest.main()