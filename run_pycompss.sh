#!/bin/bash

sudo killall java 
/etc/init.d/compss-monitor start &
runcompss -d -g -m --lang=python --classpath=/home/compss/pymdsetup/:/pymdsetup/ --comm=integratedtoolkit.nio.master.NIOAdaptor /home/compss/pymdsetup/workflows/gromacs_full_pycompss.py &
firefox http://localhost:8080/compss-monitor &