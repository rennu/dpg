set -e
echo ubuntu soft core unlimited >> /etc/security/limits.conf
echo ubuntu hard core unlimited >> /etc/security/limits.conf
cd /tmp

# Upgrade system
apt-get -y update && apt-get upgrade -y

# Install dependencies
apt-get install -y  \
  build-essential \
  cmake \
  git \
  graphviz \
  libatlas-base-dev \
  libboost-filesystem-dev \
  libboost-iostreams-dev \
  libboost-program-options-dev \
  libboost-regex-dev \
  libboost-serialization-dev \
  libboost-system-dev \
  libboost-test-dev \
  libboost-graph-dev \
  libcgal-dev \
  libcgal-qt5-dev \
  libeigen3-dev \
  libfreeimage-dev \
  libgflags-dev \
  libglew-dev \
  libglu1-mesa-dev \
  libgoogle-glog-dev \
  libjpeg-dev \
  libopencv-dev \
  libpng-dev \
  libqt5opengl5-dev \
  libsuitesparse-dev \
  libtiff-dev \
  libxi-dev \
  libxrandr-dev \
  libxxf86vm-dev \
  libxxf86vm1 \
  mediainfo \
  mercurial \
  qtbase5-dev \
  libatlas-base-dev \
  libsuitesparse-dev
mkdir /tmp/build

# Install openmvg
git clone -b develop --recursive https://github.com/openMVG/openMVG.git /tmp/build/openmvg
cd /tmp/build/openmvg
mkdir /tmp/build/openmvg_build && cd /tmp/build/openmvg_build 
cmake -DCMAKE_BUILD_TYPE=RELEASE . /tmp/build/openmvg/src -DCMAKE_INSTALL_PREFIX=/opt/openmvg 
make -j2  && make install 

# Install eigen
hg clone https://bitbucket.org/eigen/eigen#3.2 /tmp/build/eigen 
mkdir /tmp/build/eigen_build && cd /tmp/build/eigen_build 
cmake . ../eigen 
make -j2 && make install 

# Get vcglib
git clone https://github.com/cdcseacave/VCG.git /tmp/build/vcglib 

# Install ceres solver
git clone https://ceres-solver.googlesource.com/ceres-solver /tmp/build/ceres_solver
cd /tmp/build/ceres_solver && git checkout $(git describe --tags)
mkdir /tmp/build/ceres_build && cd /tmp/build/ceres_build
cmake . ../ceres_solver/ -DMINIGLOG=ON -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF 
make -j2 && make install

# Install openmvs
git clone https://github.com/cdcseacave/openMVS.git /tmp/build/openmvs 
cd /tmp/build/openmvs
mkdir /tmp/build/openmvs_build && cd /tmp/build/openmvs_build
cmake . ../openmvs -DCMAKE_BUILD_TYPE=Release -DVCG_DIR="/tmp/build/vcglib" -DCMAKE_INSTALL_PREFIX=/opt/openmvs 
make -j2 && make install

# Install cmvs-pmvs
git clone https://github.com/pmoulon/CMVS-PMVS /tmp/build/cmvs-pmvs
mkdir /tmp/build/cmvs-pmvs_build && cd /tmp/build/cmvs-pmvs_build
cmake ../cmvs-pmvs/program -DCMAKE_INSTALL_PREFIX=/opt/cmvs
make -j2 && make install

# Install colmap
git clone -b master https://github.com/colmap/colmap /tmp/build/colmap
mkdir -p /tmp/build/colmap_build && cd /tmp/build/colmap_build
cmake . ../colmap -DCMAKE_INSTALL_PREFIX=/opt/colmap
make -j2 && make install

rm -rf /tmp/build
