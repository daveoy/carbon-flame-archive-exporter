FROM rockylinux:8.8-minimal
RUN microdnf install python3 python3-pip
COPY flame-archive-exporter.py /flame-archive-exporter.py
CMD ["python3", "/flame-archive-exporter.py"]