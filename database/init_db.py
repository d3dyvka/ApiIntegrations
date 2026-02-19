import asyncio
from database.db import init_engine, Base
from logger_config import logger


async def create_tables():
    """Создание всех таблиц в базе данных"""
    logger.info("Инициализация базы данных...")
    
    try:
        engine = init_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.success("Таблицы успешно созданы")
        
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(create_tables())
