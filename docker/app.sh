#!/bin/bash
mkdir cert

openssl req -x509 -newkey rsa:4096 -nodes -out cert/cert.pem -keyout cert/key.pem -days 365 -subj "/C=UA/ST=Kyiv/L=Kyiv/O=Hub.Squadron/OU=Team/CN=WeWantToParticipate/emailAddress=kondratukandry3@gmail.com"

alembic upgrade head

cd src

gunicorn main:app --certfile="../cert/cert.pem" --keyfile="../cert/key.pem"  --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000