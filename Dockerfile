FROM python:3.10.9
WORKDIR /server-docker
COPY . /server-docker
RUN pip install -r requirements.txt
EXPOSE 3769
CMD ["python", "server.py"]