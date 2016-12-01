FROM ubuntu:16.04
MAINTAINER Speden Aave <renfld@gmail.com>
WORKDIR /tmp
RUN apt -y update && \
    apt -y install unzip curl build-essential git libpng-dev libxxf86vm1 libxxf86vm-dev libxi-dev libxrandr-dev graphviz mercurial cmake libpng-dev libjpeg-dev libtiff-dev libglu1-mesa-dev libboost-iostreams-dev libboost-program-options-dev libboost-system-dev libboost-serialization-dev libopencv-dev libcgal-dev libcgal-qt5-dev libatlas-base-dev libsuitesparse-dev && \
    mkdir /tmp/build ; cd /tmp/build && \
    git clone -b develop --recursive https://github.com/openMVG/openMVG.git && \
    mkdir openmvg_build; cd openmvg_build && \
    cmake -DCMAKE_BUILD_TYPE=RELEASE . ../openMVG/src -DCMAKE_INSTALL_PREFIX=/opt/openmvg && \
    make -j4 && make install && \
    cd .. && \
    main_path=`pwd` && \
    hg clone https://bitbucket.org/eigen/eigen#3.2 && \
    mkdir eigen_build && cd eigen_build && \
    cmake . ../eigen && \
    make -j4 && make install && \
    cd .. && \
    git clone https://github.com/cdcseacave/VCG.git vcglib && \
    git clone https://ceres-solver.googlesource.com/ceres-solver ceres-solver && \
    mkdir ceres_build && cd ceres_build && \
    cmake . ../ceres-solver/ -DMINIGLOG=ON -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF && \
    make -j4 && make install && \
    cd .. && \
    git clone https://github.com/cdcseacave/openMVS.git openMVS && \
    mkdir openMVS_build && cd openMVS_build && \
    cmake . ../openMVS -DCMAKE_BUILD_TYPE=Release -DVCG_DIR="$main_path/vcglib" -DCMAKE_INSTALL_PREFIX=/opt/openmvs && \
    make -j4 && make install && \
    git clone git@bitbucket.org:renfld/dpg.git /opt/pipeline
WORKDIR /
RUN rm -rf /tmp/build
ENTRYPOINT ["/usr/bin/python", "/opt/pipeline/pipeline.py"]