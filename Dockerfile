FROM python:3.7
MAINTAINER Artem Kozlov <kozlov.artem@gmail.com>
RUN useradd -c 'SimMon user' -m -d /home/simmon -s /bin/bash simmon && \
    mkdir -p /opt/simmon && \
    chown -R simmon:simmon /opt/simmon/
WORKDIR /opt/simmon/
USER simmon
COPY ./src/* /opt/simmon/
RUN pip install -r requirements.txt --user --no-warn-script-location
CMD [ "python", "-u", "simmon.py" ]