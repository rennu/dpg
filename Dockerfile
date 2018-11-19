FROM ubuntu:16.04
MAINTAINER Speden Aave <renfld@gmail.com>
ARG UID=1000
ARG GID=1000
WORKDIR /tmp
ADD install /tmp/install
RUN /tmp/install
RUN rm -rf /tmp/build
RUN git clone https://github.com/rennu/dpg.git /opt/dpg
RUN groupadd -g $GID ptools
RUN useradd -r -u $UID -m -g ptools ptools
WORKDIR /
USER ptools
