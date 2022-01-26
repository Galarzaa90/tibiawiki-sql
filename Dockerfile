FROM python:3.9-slim

WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install -r requirements.txt

LABEL maintainer="Allan Galarza <allan.galarza@gmail.com>"
LABEL org.opencontainers.image.licenses="Apache 2.0"
LABEL org.opencontainers.image.authors="Allan Galarza <allan.galarza@gmail.com>"
LABEL org.opencontainers.image.url="https://github.com/Galarzaa90/tibiawiki-sql"
LABEL org.opencontainers.image.source="https://github.com/Galarzaa90/tibiawiki-sql"
LABEL org.opencontainers.image.vendor="Allan Galarza <allan.galarza@gmail.com>"
LABEL org.opencontainers.image.title="tibiawiki-sql"
LABEL org.opencontainers.image.description="Python script that generates a SQLite database from TibiaWiki articles."

COPY . .
ENTRYPOINT ["python","-m", "tibiawikisql", "generate"]
