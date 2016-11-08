# -*- coding: utf-8 -*-
"""Python wrapper for command line
"""
import subprocess
import os


class CmdWrapper(object):
    """Command line wrapper using subprocess library
    """

    def __init__(self, cmd, log_path=None, error_path=None):

        self.cmd = cmd
        self.log_path = log_path
        self.error_path = error_path

    def launch(self):
        cmd = " ".join(self.cmd)
        if self.log_path is None:
            print ''
            print "cmd_wrapper commnand print: " + cmd
        new_env = os.environ.copy()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=True,
                                   env=new_env)

        out, err = process.communicate()
        if self.log_path is None:
            print "Exit, code {}".format(process.returncode)
        process.wait()

        # Write output to log_file
        if self.log_path is not None:
            with open(self.log_path, 'w') as log_file:
                log_file.write(cmd+'\n')
                log_file.write("Exit code {}".format(process.returncode)+'\n')
                if out is not None:
                    log_file.write(out)

        if self.error_path is not None:
            with open(self.error_path, 'w') as error_file:
                if err is not None:
                    error_file.write(err)
