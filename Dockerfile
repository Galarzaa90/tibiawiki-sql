FROM python:3.9.1-buster

WORKDIR /usr/src/app

COPY . .
RUN python setup.py install

CMD ["tibiawikisql", "generate"]
