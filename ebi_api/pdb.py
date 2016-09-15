import requests
import os
import shutil
import itertools


class EbiPdb(object):
    """EBI PDBe entry downloader.

    This class is used to download PDB files from the european PDB repository
    (http://www.ebi.ac.uk/pdbe)

    Args:
        pdb_code (str): Protein Data Bank (PDB) four letter code.
            ie: '2ki5'
        output_pdb_path (str): File path where the PDB file will be stored.
            ie: '/home/user1/2ki5.pdb'
    """

    def __init__(self, pdb_code, output_pdb_path):
        self._pdb_code = pdb_code
        self._output_pdb_path = output_pdb_path

    def get_pdb(self):
        """
        Writes the PDB file content of `self._pdb_code`
        to `self._output_pdb_path`
        """
        if os.path.isfile(self._pdb_code):
            shutil.copy(self._pdb_code, self._output_pdb_path)
        else:
            url = ("http://www.ebi.ac.uk/pdbe/entry-files/"
                   "pdb"+self._pdb_code.lower()+".ent")
            pdb_string = requests.get(url).content
            lines = pdb_string.splitlines(True)

            with open(self._output_pdb_path, 'w') as pdb_file:
                pdb_file.write(''.join(itertools.dropwhile(
                               lambda line: line[:6] != "ATOM  ", lines)))
