#!/usr/bin/python3
#
"""MDWeb Titration wrapper
"""
import sys
import re
import json
import configuration.settings as settings
from command_wrapper import cmd_wrapper
from tools import file_utils as fu
import CMIP

class CMIPSTitration(object):
    """Wrapper class for the titration module of CMIP v2.7.
    Args:
        input_pdb_path (str): Path to the input PDB file.
        output_pdb_path (srt): Path to the output mutated PDB file.
        properties (dic): All properties and system path
    """
    def __init__(self, input_pdb_path, output_pdb_path, properties, **kwargs):
        if isinstance(properties, basestring):
            properties=json.loads(properties)
        self.input_pdb_path = input_pdb_path
        self.output_pdb_path = output_pdb_path
        self.cmip_root = properties.get('cmip_root','')
        self.titration_path = self.cmip.root+"/src/titration"
        self.cmip_dat = self.cmip.root+"/dat"
       
        self.path = properties.get('path','')
        self.step = properties.get('step','')
       


    def launch(self):
        """Launches the execution of the CMIPTtitration binary.
        """

    

    return command.launch()

#Creating a main function to be compatible with CWL
def main():
    step=sys.argv[3]
    prop=sys.argv[4]
    step, system, mut = step.split(':')
    prop = settings.YamlReader(prop, system).get_prop_dic(mut)[step]
    prop['path']=''
    CMIPSTitration(input_pdb_path=sys.argv[1],
           output_pdb_path=sys.argv[2],
           step=step,
           properties=prop).launch()

if __name__ == '__main__':
    main()

import CMIP

def main(params):
    titwat=titip=titim=0
    [titwat, titip, titim]=params
    
    gr=CMIP.Grid()
    gr.setreadGrid(2)
    gr.perfill=0.7
    gr.int = [0.8,0.8,0.8]
    
    inpP = CMIP.InputParams("Titration", gr)
    inpP.addKeyword(
        {
            'tipcalc': 1,
            'titration':1,
            'readgrid':2,
            'inifoc':2,
            'cutfoc': -0.5,
            'focus':1,
            'ninter':10,
            'dields':2,
            'clhost':1,
            'calcgrid':1,
            'irest':0,
            'orest':0,
            'coorfmt':2,
            'titwat':titwat,
            'titip':titip,
            'titim':titim,
        }
        )
    return inpP
        

#    gr = CMIP.Grid()
#    gr.setreadGrid(2)
#    gr.int = [0.5,0.5,0.5]
#    gr0 = CMIP.Grid(1)
#    gr0.setreadGrid(2)
#    gr0.int = [1.5,1.5,1.5]
#    inp = CMIP.InputParams("CMIP test",gr,gr0)
#    inp.addKeyword({'CUBEOUTPUT':1,'MINOUT':1})
#    run = CMIP.Run(inp)
#    run.addFile({'hs': "1kim_l.pdb", 'cube' : "1kim_l.cube"})
#    result = run.execute()
#    print (result.asString())
#    #print (result.getFileContents("cube"))


if __name__ == "__main__":
    main(argv)
