FROM python:3.8-slim-buster

WORKDIR /workload-simulator

COPY requirements.txt requirements.txt

RUN apt-get update
RUN apt-get -y install vim
RUN pip3 install -r requirements.txt

COPY . .

CMD ["bash"]
