FROM python:latest
WORKDIR /opt
ENV a=5 r=3
COPY geometric_lib/circle.py .
COPY main.py .
COPY geometric_lib/square.py .
CMD ["python", "main.py"]
