import requests
import asyncio
from decouple import config
from database.db import init_engine, Base
from database.models import Request, Response, Currency
from database.db import get_session

from logs.logger_config import logger

BASE_CURRENCY = "USD"
API_KEY = config("EXCHANGE_API_KEY")
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{BASE_CURRENCY}"
UPDATE_INTERVAL_MINUTES = int(config("UPDATE_INTERVAL_MINUTES"))


async def init_database():
    """Инициализация базы данных при первом запуске"""
    logger.info("Проверка и инициализация базы данных...")
    
    try:
        engine = init_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.success("База данных готова к работе")
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}")
        raise


async def fetch_currencies():
    logger.info(f"Отправка запроса к API для валюты: {BASE_CURRENCY}")
    
    try:
        response = requests.get(BASE_URL)
        status_code = response.status_code
        logger.info(f"Получен ответ от API. Статус: {status_code}")
        
        data = response.json()
        currencies = data.get("conversion_rates", {})
        logger.success(f"Успешно получено {len(currencies)} курсов валют")
        
        return status_code, currencies
        
    except Exception as e:
        logger.error(f"Ошибка при запросе к API: {e}")
        raise


async def save_currencies_to_db():
    status_code, currencies = await fetch_currencies()
    
    try:
        async with get_session() as session:
            request = Request(base_currency=BASE_CURRENCY, api_url=BASE_URL)
            session.add(request)
            await session.flush()
            logger.debug(f"Создана запись запроса с ID: {request.id}")
            
            response_record = Response(request_id=request.id, status_code=status_code)
            session.add(response_record)
            await session.flush()
            logger.debug(f"Создана запись ответа с ID: {response_record.id}")
            
            currency_records = [
                Currency(
                    response_id=response_record.id,
                    currency_code=code,
                    rate=round(rate, 2)
                )
                for code, rate in currencies.items()
            ]
            session.add_all(currency_records)
            await session.commit()
            
            logger.success(f"Сохранено {len(currency_records)} валют в БД")
            
    except Exception as e:
        logger.error(f"Ошибка при сохранении в БД: {e}")
        raise


async def run_periodic_updates():
    await init_database()
    logger.info(f"Запуск периодического обновления курсов валют каждые {UPDATE_INTERVAL_MINUTES} минут")
    
    while True:
        try:
            await save_currencies_to_db()
            logger.info(f"Ожидание {UPDATE_INTERVAL_MINUTES} минут до следующего обновления")
            await asyncio.sleep(UPDATE_INTERVAL_MINUTES * 60)
            
        except KeyboardInterrupt:
            logger.warning("Получен сигнал остановки. Завершение работы...")
            break
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            logger.info(f"Повторная попытка через {UPDATE_INTERVAL_MINUTES} минут")
            await asyncio.sleep(UPDATE_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    asyncio.run(run_periodic_updates())







