FROM centos:7

RUN yum -y install gcc-c++ wget make
RUN wget http://www.oberhumer.com/opensource/ucl/download/ucl-1.03.tar.gz
RUN tar xzf ucl-1.03.tar.gz
RUN cd /ucl-1.03 && ./configure && make && make install

RUN yum -y install vim-common # for xxd
RUN cp /ucl-1.03/examples/uclpack /bin/
