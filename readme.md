## Task 
📋[Project task](Task.md)


# Hub.Squadron
>The web resource for the online charity auction created by our team allows users to publish, edit and delete their items, place bids in real time, communicate with other users about the item, search for items by category, and view the history of bids on a given item.

## Instruction to configure
### To run via Docker
```bash
git clone https://github.com/camelCase0/int20-auction.git
cd int20-auction
nano .env-example
cp .env-example .env
docker compose up -d
```

### Run only fastapi command: 
```bash
mkdir cert
openssl req -x509 -newkey rsa:4096 -nodes -out cert/cert.pem -keyout cert/key.pem -days 365
cd src
uvicorn main:app --ssl-keyfile ../cert/key.pem --ssl-certfile ../cert/cert.pem --host 0.0.0.0 --port 8000 --reload
```
### Alembic commands
```bash
# To make migration:
alembic revision --autogenerate -m "Migration text"
alembic upgrade head
```
## Розгортання посилання на веб-додаток

`https://localhost:8000/docs`  - documentation backend

`http://localhost:8080/`

The backend is fully functional, *websockets* are used for dynamic updates

