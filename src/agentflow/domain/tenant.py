from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Tenant:
    id: UUID
    name: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Tenant name is required.")

        if len(self.name) > 200:
            raise ValueError("Tenant name cannot exceed 200 characters.")