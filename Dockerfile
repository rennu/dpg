# First build...
FROM ubuntu:16.04 as build
MAINTAINER Speden Aave <renfld@gmail.com>
WORKDIR /tmp
ADD build.sh /tmp/build.sh
RUN /tmp/build.sh

# ..and then create a more lightweight image to actually run stuff in.
FROM ubuntu:16.04
ARG UID=1000
ARG GID=1000
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    curl \
    exiftool \
    ffmpeg \
    mediainfo \
    graphviz \
    libpng12-0 \
    libjpeg-turbo8 \
    libtiff5 \
    libxxf86vm1 \
    libxi6 \
    libxrandr2 \
    libatlas-base-dev \
    libqt5widgets5 \
    libboost-iostreams1.58.0 \
    libboost-program-options1.58.0 \
    libboost-serialization1.58.0 \
    libopencv-calib3d2.4v5 \
    libopencv-highgui2.4v5 \
    libgoogle-glog0v5 \
    libfreeimage3 \
    libcgal11v5 \
    libglew1.13 \
    libcholmod3.0.6 \
    libcxsparse3.1.4 \
    python-minimal
COPY --from=build /opt /opt
COPY pipeline.py /opt/dpg/pipeline.py
RUN groupadd -g $GID ptools
RUN useradd -r -u $UID -m -g ptools ptools
WORKDIR /
USER ptools
ENV PATH=/opt/openmvs/bin/OpenMVS:/opt/openmvg/bin:/opt/cmvs/bin:/opt/colmap/bin:/opt/dpg:$PATH
