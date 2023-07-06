FROM rockylinux:8.8-minimal
RUN microdnf install python3 python3-pip && pip3 install prometheus_client
COPY flame-archive-exporter.py /flame-archive-exporter.py
CMD ["python3", "/flame-archive-exporter.py"]