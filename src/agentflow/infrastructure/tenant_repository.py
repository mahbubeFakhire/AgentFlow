from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from agentflow.domain.tenant import Tenant
from agentflow.infrastructure.models.tenant import TenantModel


class SqlAlchemyTenantRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, tenant: Tenant) -> None:
        model = TenantModel(
            id=tenant.id,
            name=tenant.name,
        )

        self._session.add(model)
        await self._session.flush()

    async def get_by_id(self, tenant_id: UUID) -> Tenant | None:
        model = await self._session.get(TenantModel, tenant_id)

        if model is None:
            return None

        return Tenant(
            id=model.id,
            name=model.name,
        )