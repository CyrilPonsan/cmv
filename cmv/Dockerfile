# Vue Frontend
FROM node:20 AS build-stage

WORKDIR /frontend
COPY cmv_front/ .
RUN npm install
RUN npm run build

FROM python:3.12

WORKDIR /app

COPY cmv_gateway/requirements.txt /app/requirements.txt

RUN apt-get update \
    && apt-get install gcc -y \
    && apt-get clean

RUN pip install -r /app/requirements.txt
COPY cmv_gateway/. /app/

COPY --from=build-stage /frontend/dist app/dist