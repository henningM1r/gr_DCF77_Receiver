FROM ubuntu:22.04
MAINTAINER henningM1r

ENV DEBIAN_FRONTEND=noninteractive

# install tools, libraries and gnuradio
RUN apt-get update -q
RUN apt-get install python3-pip python3-apt apt-utils -y
RUN apt-get install git -y
RUN apt-get install gnuradio -y
RUN pip install --upgrade pip
RUN pip install pyzmq
RUN pip install numpy
RUN pip install coverage

# generate python-files of gnuradio
WORKDIR /home/user/

RUN git clone https://github.com/henningM1r/gr_DCF77_Receiver.git
RUN grcc /home/user/gr_DCF77_Receiver/examples/DCF77_Receiver/DCF77_Receiver_OOK.grc -o /home/user/gr_DCF77_Receiver/examples/DCF77_Receiver/
RUN grcc /home/user/gr_DCF77_Receiver/examples/DCF77_Receiver/DCF77_Receiver_PhaseMod.grc -o /home/user/gr_DCF77_Receiver/examples/DCF77_Receiver/
RUN grcc /home/user/gr_DCF77_Receiver/examples/DCF77_Transmitter/DCF77_Transmitter.grc -o /home/user/gr_DCF77_Receiver/examples/DCF77_Transmitter/
RUN grcc /home/user/gr_DCF77_Receiver/examples/DCF77_Channel/DCF77_Channel.grc -o /home/user/gr_DCF77_Receiver/examples/DCF77_Channel/

# for local testing with docker
#docker build . --tag docker_gnuradio --no-cache
#docker run --name container_gnuradio -d -i -t docker_gnuradio /bin/sh
#docker exec -it container_gnuradio sh
