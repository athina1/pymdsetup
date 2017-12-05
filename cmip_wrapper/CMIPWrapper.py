#! /usr/bin/python
"""Python wrapper module for CMIP
"""
__author__ = "gelpi"
__date__ = "$24-nov-2017 12:30:59$"


class CMIPWrapper():
    """Wrapper class for the 2.7 version of CMIP
        Adapted from CMIP standard python wrapper
    """

    def __init__(self, paths, props, properties):
        self.inputFiles=[]
        self.outputFiles=[]
        for k in paths.keys():
            lb,keyw = re.split('_',k)
            if lb == 'input':
                self.inputFiles.append({keyw:paths[k]})
            elif lb=='output':
                self.outputFiles.append({keyw:paths[k]})
        
        self.properties={'cmipkwds':{}, 'step': prots['step']}
        for k in props.keys():
            if re.match('cmip_',k):
                lb, keyw = re.split('_',k)
                self.properties['cmipkwds'][keyw]=props[k]
            else:
                self.properties[k]=props[k]        
        
    def launch(self):
        dualgrid = 'pbfocus' in self.properties['cmipkwds'] and\
            self.properties['cmipkwds']['pbfocus'] == 1
        gr = self._prepGrid()
        if dualgrid:
            gr0 = _prepGrid(1)
            inpP = cmip_wrapper.InputParams(self.properties['step'], gr, gr0)
        else:
            inpP = cmip_wrapper.InputParams(self.properties['step'], gr)
        for prm in self.properties['cmipkwds'].keys():
            inpP.addKeyword ({prm.upper():self.properties['cmipkwds'][prm]})
        
        run = cmip_wrapper.Run(inpP,'wrapper')
        if 'titration' in self.properties['cmipkwds']:
            run.exefile = self.properties['CMIP_root']+"/src/titration"
        else:
            run.exefile = self.properties['CMIP_root']+"/src/cmip"
        for fn in self.inputFiles + self.outputFiles:
            run.addFile(fn)
        if 'vdw' not in run.files:
            run.addFile({'vdw':self.properties['CMIP_root']+'/dat/vdwprm'})
        # using cmd_wrapper
        out_log, err_log = fu.get_logs(path=self.properties['path'])
        
        cmd = run.prepare()
        print (cmd)
        command = cmd_wrapper.CmdWrapper(cmd, out_log, err_log)
        command.launch()
        # using original CMIP execute
        # result = run.execute
        result = cmip_wrapper.Result(run.files)
        print (result.asString())
        
    def _prepGrid(self,outgrid=0):        
        if outgrid:
            lb='0'
        else:
            lb=''
        gr = cmip_wrapper.Grid(outgrid)
        if 'readgrid'+lb in self.properties['cmipkwds']:
            gr.setreadGrid(self.properties['cmipkwds']['readgrid'+lb])
            del self.properties['cmipkwds']['readgrid'+lb]
        if 'perfill'+lb in self.properties['cmipkwds']:
            gr.setperfill (self.properties['cmipkwds']['perfill'+lb])
            del self.properties['cmipkwds']['perfill'+lb]
        if 'cen'+lb in self.properties['cmipkwds']:
            gr.cen = self.properties['cmipkwds']['cen'+lb]
            del self.properties['cmipkwds']['cen'+lb]
        if 'dim'+lb in self.properties['cmipkwds']:
            gr.dim = self.properties['cmipkwds']['dim'+lb]
            del self.properties['cmipkwds']['dim'+lb]
        if 'int'+lb in self.properties['cmipkwds']:
            gr.int = self.properties['cmipkwds']['int'+lb]
            del self.properties['cmipkwds']['int'+lb]
        gr.update()
        return gr
        
        

def main():
    step=sys.argv[1]
    propfn=sys.argv[2]
    props = settings.YamlReader(propfn, 'linux').get_prop_dic()[step]
    props['step']=step
    paths = settings.YamlReader(propfn, 'linux').get_paths_dic()[step]

    CMIPWrapper(paths,props).launch()

if __name__ == "__main__":
    main()
