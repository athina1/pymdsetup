sudo apt-get -y install git vim htop cmake gnuplot
pip install --upgrade pip
sudo pip install numpy biopython pyyaml requests

# Gromacs 5.1.2 quick and dirty installation
wget ftp://ftp.gromacs.org/pub/gromacs/gromacs-5.1.2.tar.gz
# http://manual.gromacs.org/documentation/5.1.2/install-guide/index.html
tar xfz gromacs-5.1.2.tar.gz
cd gromacs-5.1.2
mkdir build
cd build
cmake .. -DGMX_BUILD_OWN_FFTW=ON -DREGRESSIONTEST_DOWNLOAD=ON
make
make check
sudo make install
source /usr/local/gromacs/bin/GMXRC
echo "bash /usr/local/gromacs/bin/GMXRC" >> ~/.bashrc

# Register in http://dunbrack.fccc.edu/scwrl4/license/index.html and download
# the "install_Scwrl4_Linux" executable
cd ~
chmod u+x install_Scwrl4_Linux
./install_Scwrl4_Linux
