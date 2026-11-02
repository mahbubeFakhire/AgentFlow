from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from agentflow.api.dependencies import get_create_tenant_handler
from agentflow.application.create_tenant import (
    CreateTenantCommand,
    CreateTenantHandler,
)


router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"],
)


class CreateTenantResponse(BaseModel):
    id: UUID
    name: str


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateTenantResponse,
)
async def create_tenant(
    command: CreateTenantCommand,
    handler: Annotated[
        CreateTenantHandler,
        Depends(get_create_tenant_handler),
    ],
) -> CreateTenantResponse:
    result = await handler.handle(command)

    return CreateTenantResponse(
        id=result.id,
        name=result.name,
    )