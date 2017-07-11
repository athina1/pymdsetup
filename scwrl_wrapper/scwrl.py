"""Python wrapper module for SCWRL
"""
import sys
import re
from Bio.PDB.PDBParser import PDBParser
from Bio.PDB import PDBIO
import configuration.settings as settings

try:
    from command_wrapper import cmd_wrapper
    from tools import file_utils as fu
except ImportError:
    from pymdsetup.command_wrapper import cmd_wrapper
    from pymdsetup.tools import file_utils as fu


class Scwrl4(object):
    """Wrapper class for the 4.0 version of SCWRL.

    Args:
        input_pdb_path (str): Path to the input PDB file.
        output_pdb_path (srt): Path to the output mutated PDB file.
        mutation (str): String representing the mutation. ie: A.His11Asp
        log_path (str): Path to the file where the SCWRL log will be stored.
        error_path (str): Path to the file where the SCWRL error log will be
            stored.
        scwrl4_path (str): Path to the SCWRL executable binary.
    """

    def __init__(self, input_pdb_path, output_pdb_path, mutation,
                 log_path=None, error_path=None, scwrl4_path=None,
                 config_string=None, **kwargs):
        self.input_pdb_path = input_pdb_path
        self.output_pdb_path = output_pdb_path

        if step_conf_path is not None:
            config_path, system, step = step_conf_path.split(":")
            general_conf = settings.YamlReader(yaml_path=config_path, system=system)
            self.mutation = general_conf.properties['input_mapped_mutations_list'].split(',')[0]
            config = general_conf.step_prop_dic(step, fu.get_workflow_path(general_conf.properties[system]['workflow_path']), self.mutation)
            pattern = re.compile(("(?P<chain>[a-zA-Z]{1}).(?P<wt>[a-zA-Z]{3})"
                                  "(?P<resnum>\d+)(?P<mt>[a-zA-Z]{3})"))
            self.mutation = pattern.match(mutation).groupdict()
            self.log_path = config['log_path']
            self.error_path = config['error_path']
            self.scwrl4_path = config['scwrl4_path']
        else:
            self.mutation = mutation
            if self.mutation is not None:
                pattern = re.compile(("(?P<chain>[a-zA-Z]{1}).(?P<wt>[a-zA-Z]{3})"
                                      "(?P<resnum>\d+)(?P<mt>[a-zA-Z]{3})"))
                self.mutation = pattern.match(mutation).groupdict()
            self.log_path = log_path
            self.error_path = error_path
            self.scwrl4_path = scwrl4_path

    def launch(self):
        """Launches the execution of the SCWRL binary.
        """
        if self.mutation is not None:
            # Read structure with Biopython
            parser = PDBParser(PERMISSIVE=1)
            st = parser.get_structure('s', self.input_pdb_path)  # s random id never used

            # Remove the side chain of the AA to be mutated
            chain = self.mutation['chain']
            resnum = int(self.mutation['resnum'])
            residue = st[0][chain][(' ', resnum, ' ')]
            backbone_atoms = ['N', 'CA', 'C', 'O', 'CB']
            not_backbone_atoms = []

            # The following formula does not work. Biopython bug?
            # for atom in residue:
            #     if atom.id not in backbone_atoms:
            #         residue.detach_child(atom.id)

            for atom in residue:
                if atom.id not in backbone_atoms:
                    not_backbone_atoms.append(atom)
            for atom in not_backbone_atoms:
                residue.detach_child(atom.id)

            # Change residue name
            residue.resname = self.mutation['mt'].upper()

            # Write resultant structure
            w = PDBIO()
            w.set_structure(st)
            prepared_file_path = self.output_pdb_path + '.scwrl4.prepared.pdb'
            w.save(prepared_file_path)
        else:
            prepared_file_path = self.input_pdb_path

        scrwl = 'Scwrl4' if self.scwrl4_path is None else self.scwrl4_path
        cmd = [scrwl, '-i', prepared_file_path, '-o', self.output_pdb_path]

        command = cmd_wrapper.CmdWrapper(cmd, self.log_path, self.error_path)
        command.launch()

#Creating a main function to be compatible with CWL
def main():
    Scwrl4(input_pdb_path=sys.argv[1],
               output_pdb_path=sys.argv[2],
               mutation=sys.argv[3],
               scwrl4_path=sys.argv[4],
               log_path=sys.argv[5],
               error_path=sys.argv[6]).launch()

if __name__ == '__main__':
    main()
