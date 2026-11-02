from typing import Protocol
from uuid import UUID

from agentflow.domain.tenant import Tenant


class TenantRepository(Protocol):
    async def add(self, tenant: Tenant) -> None:
        ...

    async def get_by_id(self, tenant_id: UUID) -> Tenant | None:
        ...