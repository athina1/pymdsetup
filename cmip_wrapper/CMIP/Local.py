#!/usr/bin/python3
#
#package CMIP::Local;
#
#=head1 NAME 
#
#CMIP::Local
#
#=head1 SYNOPSIS
#
#Internal data for CMIP::Run
#
#use CMIP::Local;
#
#=head1
#
#$jobId=createTMP;
#
#=cut

import os


BASEDIR = "/data/soft/CMIP"
VDWPRM = BASEDIR +"/dat/vdwprm"
CMIP = BASEDIR + "/src/cmip"
QSUB = "/usr/local/bin/qsub"
QUEUEDEFAULT = "ibm"
TMPDIR = "/usr/tmp"

#def createTMP():
#    id = tempfile.makdtemp(prefix="CMIP")
##    id = "CMIP" + "{5}".format(time.gmtime())
#    #os.umask(022)
#    return id
