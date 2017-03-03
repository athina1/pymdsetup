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


def create_change_dir(dir_path):
    create_dir(dir_path)
    os.chdir(dir_path)
    return dir_path


def get_workflow_path(dir_path):

    if not os.path.exists(dir_path):
        return dir_path

    cont = 1
    while os.path.exists(dir_path):
        dir_path = dir_path.rstrip('\\/0123456789_') + '_' + str(cont)
        cont += 1
    return dir_path


def rm_ext(ext, source_dir=None):
    if source_dir is None:
        source_dir = os.getcwd()
    files = glob.iglob(os.path.join(source_dir, "*." + ext))
    for f in files:
        if os.path.isfile(f):
            os.remove(f)


def backup_ext(ext, source_dir=None):
    if source_dir is None:
        source_dir = os.getcwd()
    files = glob.iglob(os.path.join(source_dir, "*." + ext))
    for f in files:
        if os.path.isfile(f):
            shutil.move(f, f+".bkp")


def copy_ext(dest_dir, ext, source_dir=None):
    if not os.path.isdir(dest_dir):
        dest_dir = os.path.dirname(dest_dir)
    if source_dir is None:
        source_dir = os.getcwd()
    files = glob.iglob(os.path.join(source_dir, "*." + ext))
    for f in files:
        if os.path.isfile(f):
            shutil.copy2(f, dest_dir)


def mv_ext(dest_dir, ext, source_dir=None):
    if not os.path.isdir(dest_dir):
        dest_dir = os.path.dirname(dest_dir)
    if source_dir is None:
        source_dir = os.getcwd()
    files = glob.iglob(os.path.join(source_dir, "*." + ext))
    for f in files:
        if os.path.isfile(f):
            shutil.move(f, dest_dir)


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
        if top_file is not None:
            dest_dir = os.path.dirname(top_file)
    else:
        if not os.path.isdir(dest_dir):
            dest_dir = os.path.dirname(dest_dir)

    new_tar_file = os.path.join(dest_dir, tar_file)
    if not os.path.exists(new_tar_file):
        shutil.copy2(tar_file, dest_dir)

    with tarfile.open(new_tar_file) as tar:
        tar_name = next(name for name in tar.getnames() if name.endswith(".top"))
        tar.extractall(path=dest_dir)
    if top_file is not None:
        shutil.copyfile(os.path.join(dest_dir, tar_name), top_file)
    return os.path.join(dest_dir, tar_name)


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
