# Use OpenMVG develop branch version 97d2957
# Use OpenMVS master branch version 019e9d6 

FROM ubuntu:16.04
MAINTAINER Speden Aave <renfld@gmail.com>
WORKDIR /tmp
RUN apt -y update && \
    apt -y install unzip curl build-essential git libpng-dev libxxf86vm1 libxxf86vm-dev libxi-dev libxrandr-dev graphviz mercurial cmake libpng-dev libjpeg-dev libtiff-dev libglu1-mesa-dev libboost-iostreams-dev libboost-program-options-dev libboost-system-dev libboost-serialization-dev libopencv-dev libcgal-dev libcgal-qt5-dev libatlas-base-dev libsuitesparse-dev && \
    mkdir /tmp/build && \
    git clone -b develop --recursive https://github.com/openMVG/openMVG.git /tmp/build/openmvg && \
    mkdir /tmp/build/openmvg_build && cd /tmp/build/openmvg_build && \
    cmake -DCMAKE_BUILD_TYPE=RELEASE . /tmp/build/openmvg/src -DCMAKE_INSTALL_PREFIX=/opt/openmvg && \
    make -j2 && make install && \
    main_path=/tmp/build && \
    hg clone https://bitbucket.org/eigen/eigen#3.2 /tmp/build/eigen && \
    mkdir /tmp/build/eigen_build && cd /tmp/build/eigen_build && \
    cmake . ../eigen && \
    make -j2 && make install && \
    git clone https://github.com/cdcseacave/VCG.git /tmp/build/vcglib && \
    git clone https://ceres-solver.googlesource.com/ceres-solver /tmp/build/ceres_solver && \
    mkdir /tmp/build/ceres_build && cd /tmp/build/ceres_build && \
    cmake . ../ceres_solver/ -DMINIGLOG=ON -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF && \
    make -j2 && make install && \
    git clone https://github.com/cdcseacave/openMVS.git /tmp/build/openmvs && \
    mkdir /tmp/build/openmvs_build && cd /tmp/build/openmvs_build && \
    cmake . ../openmvs -DCMAKE_BUILD_TYPE=Release -DVCG_DIR="/tmp/build/vcglib" -DCMAKE_INSTALL_PREFIX=/opt/openmvs && \
    make -j2 && make install && \
    git clone https://github.com/rennu/dpg.git /opt/pipeline
WORKDIR /
RUN rm -rf /tmp/build
ENTRYPOINT ["/usr/bin/python", "-u", "/opt/pipeline/pipeline.py"]