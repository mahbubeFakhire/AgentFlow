from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from agentflow.application.create_tenant import CreateTenantHandler
from agentflow.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    session_factory: async_sessionmaker[AsyncSession] = (
        request.app.state.session_factory
    )

    async with session_factory() as session:
        yield session


DatabaseSession = Annotated[AsyncSession, Depends(get_session)]

def get_create_tenant_handler(
    request: Request,
) -> CreateTenantHandler:
    session_factory = request.app.state.session_factory

    return CreateTenantHandler(
        uow=SqlAlchemyUnitOfWork(session_factory),
    )