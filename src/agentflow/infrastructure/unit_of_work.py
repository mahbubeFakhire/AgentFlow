from contextlib import AsyncExitStack
from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agentflow.application.contracts.tenant_repository import (
    TenantRepository,
)
from agentflow.infrastructure.tenant_repository import (
    SqlAlchemyTenantRepository,
)


class SqlAlchemyUnitOfWork:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._session_factory = session_factory
        self._stack: AsyncExitStack | None = None
        self._tenants: TenantRepository | None = None
        self._used = False

    @property
    def tenants(self) -> TenantRepository:
        if self._tenants is None:
            raise RuntimeError("Unit of Work is not active.")

        return self._tenants

    async def __aenter__(self) -> Self:
        if self._used:
            raise RuntimeError(
                "Create a new Unit of Work for each operation."
            )

        self._used = True
        stack = AsyncExitStack()

        try:
            session = await stack.enter_async_context(
                self._session_factory.begin()
            )

            self._tenants = SqlAlchemyTenantRepository(session)
            self._stack = stack

            return self

        except BaseException as exc:
            await stack.__aexit__(
                type(exc),
                exc,
                exc.__traceback__,
            )
            raise

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._stack is None:
            raise RuntimeError("Unit of Work is not active.")

        try:
            await self._stack.__aexit__(
                exc_type,
                exc_value,
                traceback,
            )
        finally:
            self._tenants = None
            self._stack = None