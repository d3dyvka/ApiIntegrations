# API Integrations - Currency Exchange

Проект для получения и хранения курсов валют с автоматическим обновлением в PostgreSQL.

## Быстрый старт

### 1. Настройка .env файла

Скопируйте `.env.example` в `.env` и укажите ваш API ключ:

```bash
cp .env.example .env
```

```env
# API ENV
EXCHANGE_API_KEY=your_api_key_here

# DATABASE ENV
DB_HOST=localhost
DB_NAME=requests
DB_USER=requests_user
DB_PASSWORD=12345

# UPDATE RATE
UPDATE_INTERVAL_MINUTES=5
```

### 2. Запуск проекта

```bash
docker-compose up -d
```

### 3. Проверка работы

```bash
docker-compose logs -f app
```

### 4. Остановка

```bash
docker-compose down
```

## Структура базы данных

**requests** → **responses** → **currencies**

- `requests` - история запросов к API (id, base_currency, api_url, created_at)
- `responses` - ответы от API (id, request_id, status_code, received_at)
- `currencies` - курсы валют (id, response_id, currency_code, rate)

## SQL-запрос с JOIN

```sql
SELECT 
    r.id AS request_id,
    r.base_currency,
    r.created_at AS request_time,
    resp.status_code,
    resp.received_at AS response_time,
    c.currency_code,
    c.rate
FROM 
    requests r
INNER JOIN 
    responses resp ON r.id = resp.request_id
INNER JOIN 
    currencies c ON resp.id = c.response_id
ORDER BY 
    r.created_at DESC, 
    c.currency_code ASC;
```

### Примеры запросов

**Последние курсы валют:**
```sql
SELECT c.currency_code, c.rate, resp.received_at
FROM requests r
INNER JOIN responses resp ON r.id = resp.request_id
INNER JOIN currencies c ON resp.id = c.response_id
WHERE r.id = (SELECT MAX(id) FROM requests)
ORDER BY c.currency_code;
```

**История курса конкретной валюты:**
```sql
SELECT r.created_at, c.rate
FROM requests r
INNER JOIN responses resp ON r.id = resp.request_id
INNER JOIN currencies c ON resp.id = c.response_id
WHERE c.currency_code = 'EUR'
ORDER BY r.created_at DESC;
```

## Подключение к БД

```bash
docker exec -it requests_db psql -U requests_user -d requests
```

Параметры: `localhost:5432`, DB: `requests`, User: `requests_user`, Password: `12345`

## Полезные команды

```bash
# Пересборка
docker-compose build

# Логи
docker-compose logs -f

# Перезапуск
docker-compose restart app

# Удаление с данными
docker-compose down -v
```
