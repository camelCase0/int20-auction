# Hub.Squadron
>Створений нашою командою веб-ресурс для благодійного онлайн-аукціону надає користувачам можливість опубліковувати, редагувати та видаляти свої лоти, робити ставки в режимі реального часу, спілкуватись з іншими користувачами на тему лоту, здійснювати пошук лотів за категоріями, переглядати історію ставок на дану позицію.

## Зміст
1. [Технології](###Технології)
2. [Інструкція з налаштування](###Інструкція-з-налаштування)
3. [Розгортання посилання на веб-додаток](###Розгортання-посилання-на-веб-додаток)

## Інструкція з налаштування
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

Фронтенд виконувався за останні 3 години.
Бекенд повністю функціональний, для динамічного оновлення застосовано вебсокети

