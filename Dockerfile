FROM python:3.9-alpine

WORKDIR /usr/src/app

COPY . .
RUN python setup.py install

CMD ["tibiawikisql", "generate"]
