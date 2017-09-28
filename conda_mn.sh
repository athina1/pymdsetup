#Install conda 2.5 from its script
#Afegir en el .bashrc abans de la linia de conda
# module unload PYTHON
source ~/.bashrc
conda create --use-index-cache --offline --name pymdsetup  python=2.7
source activate pymdsetup
wget https://repo.continuum.io/pkgs/free/linux-64/biopython-1.69-np113py27_0.tar.bz2
scp /home/pau/Downloads/biopython-1.69-np113py27_0.tar.bz2 mn:/home/bsc23/bsc23210/anaconda2/pkgs/
conda install /home/bsc23/bsc23210/anaconda2/pkgs/biopython-1.69-np113py27_0.tar.bz2
conda install --use-index-cache --offline --use-local  numpy pyyaml requests nose
echo "/home/bsc23/bsc23210/pymdsetup" > /home/bsc23/bsc23210/anaconda2/envs/pymdsetup/lib/python2.7/site-packages/pymdsetup.pth 
#change ../scwrl4/Scwrl4.ini 
