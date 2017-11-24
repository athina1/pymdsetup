#!/uisr/bin/python3
#
#package CMIP::Run;
#
#=head1 NAME
#
#CMIP::Run - Object to run CMIP jobs
#
#=head1 SYNOPSIS
#
#use CMIP::Run;
#use CMIP::InputParameters;
#
#$cmipRun = CMIP::Run->new($inputParameters);
#
#=head1 METHODS
#
#$value=$cmipRun->type('direct'|'batch');
#
#$cmipRun->addFile(id1=>file1, id2=>file2,...);
#
#$cmipRun->delFile(id); 
#
#$hashref = $cmipRun->files;
#
#$resultref = $cmipRun->execute($queue);
#
#$cmipRun->rmTmpDir;
#
#=cut

import os
import shutil
import CMIP
import tempfile
import sys
import subprocess

class Run():
    def __init__(self,inputP):
        workdir=os.getcwd()
        self.workdir = workdir
        self.param = inputP
        self.type = 'direct'
        self.files = {'vdw': CMIP.Local.VDWPRM}
        self.queue = ''
        self.exefile = ''
        

    def rmTmpDir(self):
        shutil.rmtree(self.tmpdir)


    def addFile(self, FILES):
        for k in FILES.keys():
            self.files[k] = FILES[k]
        return self

    def delFile(self,file):
        self.files.pop(file, None)
        return self

    def execute(self,queue=''):
        tmpdir = tempfile.mkdtemp(prefix="CMIP")
        if 'i' not in self.files:
            try:
                TMPPAR = open (tmpdir+"/param", "w")
            except OSError:
                print ("Error: open "+ tmpdir + "/param")
                sys.exit(1)
            
            TMPPAR.write(str(self.param))
            TMPPAR.close()
            if self.exefile:
                cmd = self.exefile + " -i " + tmpdir +"/param"
            else:
                cmd = CMIP.Local.CMIP + " -i " + tmpdir + "/param"
        if 'o' not in self.files:
            self.addFile({'o' : tmpdir + "/cmip.out"})
        if 'l' not in self.files:
            self.addFile({'l' : tmpdir + "/cmip.log"})
        if  self.type ==  'direct':
            self.addFile(
                {
                    "stderr": tmpdir + "/stderr.log",
                    "stdout": tmpdir + "/stdout.log"
                }
            )
        for k in self.files.keys():
            cmd = cmd + " -{} {}".format(k,self.files[k])

        runscript = tmpdir + "/run.csh"
        try:
            CSH = open (runscript,"w")
        except OSError as e:
            print ("Error: {} {} ({})".format(e.errno, e.strerror,runscript))
            sys.exit(1)
        CSH.write ("#!/bin/tcsh -f\nhostname\ncd "+ self.workdir + "\n" + cmd + "\n#rm -rf " + tmpdir + "\n")
        CSH.close()
        if self.type == 'batch':
            if self.queue == '':
                QUEUE = self.queue
            else:
                QUEUE = CMIP.Local.QUEUEDEFAULT
#            return subprocess.run ("CMIP.Local.QSUB + "-q " + QUEUE + " " + tmpdir+"/run.csh")
            return ''
        else:
            cproc = subprocess.getoutput ("/bin/tcsh "+ runscript + " 1> " +  self.files['stdout'] + " 2> " + self.files['stderr'])            
            return CMIP.Result(self.files)
            
		
