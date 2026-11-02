from dataclasses import dataclass
from uuid import UUID, uuid4

from agentflow.application.contracts.unit_of_work import UnitOfWork
from agentflow.domain.tenant import Tenant
from typing import Annotated
from pydantic import BaseModel, ConfigDict, StringConstraints

class CreateTenantCommand(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    name: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True,
            min_length=1,
            max_length=200,
            strict=True,
        ),
    ]


@dataclass(frozen=True, slots=True)
class CreateTenantResult:
    id: UUID
    name: str


class CreateTenantHandler:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(
        self,
        command: CreateTenantCommand,
    ) -> CreateTenantResult:
        tenant = Tenant(
            id=uuid4(),
            name=command.name,
        )

        async with self._uow as uow:
            await uow.tenants.add(tenant)

        return CreateTenantResult(
            id=tenant.id,
            name=tenant.name,
        )