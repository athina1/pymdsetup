"""Tools to work with files
"""
import os
import shutil
import glob
import tarfile
import logging
from os.path import join as opj

def create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

def get_workflow_path(dir_path):
    if not os.path.exists(dir_path):
        return dir_path

    cont = 1
    while os.path.exists(dir_path):
        dir_path = dir_path.rstrip('\\/0123456789_') + '_' + str(cont)
        cont += 1
    return dir_path

def remove_temp_files(endswith_list, source_dir=None):
    removed_list = []
    source_dir = os.getcwd() if source_dir is None else os.path.abspath(source_dir)
    files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
    for f in files:
        if f.endswith(tuple(endswith_list)):
            os.remove(f)
            removed_list.append(f)
    return removed_list

def tar_top(top_file, tar_file):
    top_dir = os.path.abspath(os.path.dirname(top_file))
    files = glob.iglob(os.path.join(top_dir, "*.itp"))
    if os.path.abspath(os.getcwd()) != top_dir:
        files = glob.iglob(os.path.join(os.getcwd(), "*.itp"))
    with tarfile.open(tar_file, 'w') as tar:
        for f in files:
            tar.add(f, arcname=os.path.basename(f))
        tar.add(top_file, arcname=os.path.basename(top_file))

def untar_top(tar_file, dest_dir=None, top_file=None):
    if dest_dir is None:
        dest_dir = os.getcwd()
    with tarfile.open(tar_file) as tar:
        tar_name = next(name for name in tar.getnames() if name.endswith(".top"))
        tar.extractall(path=dest_dir)
    if top_file is not None:
        shutil.copyfile(os.path.join(dest_dir, tar_name), os.path.basename(top_file))
        return top_file
    return tar_name

def get_logs(path, mutation=None, step=None, console=False):
    path = '' if (path is None or not os.path.isdir(path)) else path
    mutation = '' if mutation is None else mutation+'_'
    step = '' if step is None else step+'_'
    out_log_path = opj(path, mutation+step+'out.log')
    err_log_path = opj(path, mutation+step+'err.log')
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    out_Logger = logging.getLogger(out_log_path)
    err_Logger = logging.getLogger(err_log_path)
    out_fileHandler = logging.FileHandler(out_log_path, mode='a', encoding=None, delay=False)
    err_fileHandler = logging.FileHandler(err_log_path, mode='a', encoding=None, delay=False)
    out_fileHandler.setFormatter(logFormatter)
    err_fileHandler.setFormatter(logFormatter)
    out_Logger.addHandler(out_fileHandler)
    err_Logger.addHandler(err_fileHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    # Adding console aditional output
    if console:
        out_Logger.addHandler(consoleHandler)
        err_Logger.addHandler(consoleHandler)
    out_Logger.setLevel(10)
    err_Logger.setLevel(10)
    return out_Logger, err_Logger
