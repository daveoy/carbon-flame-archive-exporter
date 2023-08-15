FROM rockylinux:8.8-minimal
RUN microdnf install python3 python3-pip && pip3 install prometheus_client python-dateutil && mkdir -p /opt/Autodesk/io/bin/
COPY ArchInfo /opt/Autodesk/io/bin/ArchInfo
COPY flame-archive-exporter.py /flame-archive-exporter.py
CMD ["python3", "/flame-archive-exporter.py"]