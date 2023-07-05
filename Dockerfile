FROM python:3.11-alpine
COPY flame-archive-exporter.py /flame-archive-exporter.py
CMD ["python3", "flame-archive-exporter.py"]