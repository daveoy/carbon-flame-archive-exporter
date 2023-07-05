FROM python:3.11-alpine
RUN apk add --no-cache \
    popt \
    libstdc++
COPY flame-archive-exporter.py /flame-archive-exporter.py
CMD ["python3", "/flame-archive-exporter.py"]