from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional

from .db import get_session
from .models import Request, Response, Currency


async def get_request(request_id: int) -> Optional[Request]:
    """Получить запрос по ID"""
    async with get_session() as session:
        result = await session.execute(
            select(Request).where(Request.id == request_id)
        )
        return result.scalar_one_or_none()


async def get_all_requests() -> List[Request]:
    """Получить все запросы"""
    async with get_session() as session:
        result = await session.execute(select(Request).order_by(Request.created_at.desc()))
        return list(result.scalars().all())


async def delete_request(request_id: int) -> bool:
    """Удалить запрос"""
    async with get_session() as session:
        result = await session.execute(
            delete(Request).where(Request.id == request_id)
        )
        await session.commit()
        return result.rowcount > 0


async def get_response(response_id: int) -> Optional[Response]:
    """Получить ответ по ID"""
    async with get_session() as session:
        result = await session.execute(
            select(Response).where(Response.id == response_id)
        )
        return result.scalar_one_or_none()


async def get_all_responses() -> List[Response]:
    """Получить все ответы"""
    async with get_session() as session:
        result = await session.execute(select(Response).order_by(Response.received_at.desc()))
        return list(result.scalars().all())


async def delete_response(response_id: int) -> bool:
    """Удалить ответ"""
    async with get_session() as session:
        result = await session.execute(
            delete(Response).where(Response.id == response_id)
        )
        await session.commit()
        return result.rowcount > 0


async def get_currency_by_code(currency_code: str) -> List[Currency]:
    """Получить курс валюты по коду"""
    async with get_session() as session:
        result = await session.execute(
            select(Currency)
            .where(Currency.currency_code == currency_code)
            .order_by(Currency.id.desc())
        )
        return list(result.scalars().all())


async def get_all_currencies() -> List[Currency]:
    """Получить все курсы валют"""
    async with get_session() as session:
        result = await session.execute(
            select(Currency).order_by(Currency.currency_code)
        )
        return list(result.scalars().all())


async def delete_currency(currency_id: int) -> bool:
    """Удалить валюту"""
    async with get_session() as session:
        result = await session.execute(
            delete(Currency).where(Currency.id == currency_id)
        )
        await session.commit()
        return result.rowcount > 0


async def get_request_history_with_currencies():
    """
    SQL-запрос с JOIN для получения истории запросов и валют.
    Возвращает данные о запросах, ответах и валютах.
    """
    async with get_session() as session:
        result = await session.execute(
            select(Request, Response, Currency)
            .join(Response, Request.id == Response.request_id)
            .join(Currency, Response.id == Currency.response_id)
            .order_by(Request.created_at.desc(), Currency.currency_code)
        )
        return result.all()


async def get_latest_currencies_for_request(request_id: int) -> List[Currency]:
    """Получить последние курсы валют для запроса"""
    async with get_session() as session:
        subquery = (
            select(Response.id)
            .where(Response.request_id == request_id)
            .order_by(Response.received_at.desc())
            .limit(1)
            .scalar_subquery()
        )
        
        result = await session.execute(
            select(Currency)
            .where(Currency.response_id == subquery)
            .order_by(Currency.currency_code)
        )
        return list(result.scalars().all())


async def get_full_request_data(request_id: int):
    """Получить полные данные запроса с ответами и валютами"""
    async with get_session() as session:
        result = await session.execute(
            select(Request)
            .options(
                selectinload(Request.responses).selectinload(Response.currencies)
            )
            .where(Request.id == request_id)
        )
        return result.scalar_one_or_none()
