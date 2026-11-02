from types import TracebackType
from typing import Protocol, Self

from agentflow.application.contracts.tenant_repository import (
    TenantRepository,
)


class UnitOfWork(Protocol):
    @property
    def tenants(self) -> TenantRepository:
        ...

    async def __aenter__(self) -> Self:
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        ...