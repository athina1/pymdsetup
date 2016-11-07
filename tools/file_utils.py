# -*- coding: utf-8 -*-
"""Tools to work with files
"""
import os
import shutil
import glob
import tarfile


def create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


def copy_ext(source_dir, dest_dir, ext):
    files = glob.iglob(os.path.join(source_dir, "*." + ext))
    for f in files:
        if os.path.isfile(f):
            shutil.copy2(f, dest_dir)


def tar_top(top_file, tar_file):
    files = glob.iglob(os.path.join(os.path.dirname(top_file), "*.itp"))
    with tarfile.open(tar_file, 'w') as tar:
        for f in files:
            tar.add(f)
        tar.add(top_file)


def untar(tar_file, top_file):
    dest_dir = os.path.diname(top_file)
    shutil.copy2(tar_file, dest_dir)
    new_tar_file = os.path.join(dest_dir, tar_file)
    with tarfile.open(new_tar_file) as tar:
        tar_name = next(name for name in tar.getnames() if name.endswith(".top"))
        tar.extractall(path=dest_dir)
    shutil.copyfile(os.path.join(dest_dir, tar_name), top_file)


def rm_hash_bakup():
    filelist = [f for f in os.listdir(".") if f.startswith("#") and
                f.endswith("#")]
    for f in filelist:
        os.remove(f)


def rm_temp():
    # Remove all files in the temp_results directory
    for f in os.listdir('.'):
        try:
            # Not removing directories
            if (os.path.isfile(f) and
                (f.startswith('#') or
                 f.startswith('temp') or
                 f.startswith('None') or
                 f.startswith('step') or
                 f == 'mdout.mdp' or
                 f == 'md.log')):
                os.unlink(f)
            # elif os.path.isdir(f) and (f.startswith('pycompss')):
            #     shutil.rmtree(f)
        except Exception, e:
            print e
