from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TelegramLoginRequest(BaseModel):
    init_data: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    telegram_id: int | None
    first_name: str
    last_name: str | None
    username: str | None
    is_superuser: bool
    roles: list[str]


class MeResponse(BaseModel):
    id: UUID
    telegram_id: int | None
    first_name: str
    last_name: str | None
    username: str | None
    is_superuser: bool
    roles: list[str]
    permissions: list[str]
