#!/bin/bash

sudo docker build -t tibiawiki-sql .

touch tibiawiki.db
mkdir -p images

sudo docker run \
-v "$(pwd)"/tibiawiki.db:/usr/src/app/tibiawiki.db \
-v "$(pwd)"/images:/usr/src/app/images \
-ti --rm tibiawiki-sql
