from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.app_registry.contracts.app_registry_contracts import AppRegistryAppOut


class _AppRegistryAdminContractBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_validator(
        "code",
        "name",
        "description",
        "web_path",
        "api_path",
        "local_web_url",
        "local_api_url",
        "status",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def _strip_string(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("web_path", "api_path", check_fields=False)
    @classmethod
    def _path_must_start_with_slash(cls, value: str | None) -> str | None:
        if value is not None and not value.startswith("/"):
            raise ValueError("路径必须以 / 开头")
        return value

    @field_validator("local_web_url", "local_api_url", check_fields=False)
    @classmethod
    def _local_url_must_be_http(cls, value: str | None) -> str | None:
        if value is not None and not value.startswith(("http://", "https://")):
            raise ValueError("本地地址必须以 http:// 或 https:// 开头")
        return value


class AppRegistryAdminAppCreateIn(_AppRegistryAdminContractBase):
    code: str = Field(min_length=1, max_length=64, pattern=r"^[a-z][a-z0-9-]*$")
    name: str = Field(min_length=1, max_length=128)
    description: str = Field(min_length=1, max_length=512)
    web_path: str = Field(min_length=1, max_length=256)
    api_path: str = Field(min_length=1, max_length=256)
    local_web_url: str = Field(min_length=1, max_length=256)
    local_api_url: str = Field(min_length=1, max_length=256)
    status: Literal["ready", "planned"] = "ready"
    sort_order: int = 0
    is_active: bool = True


class AppRegistryAdminAppUpdateIn(_AppRegistryAdminContractBase):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = Field(default=None, min_length=1, max_length=512)
    web_path: str | None = Field(default=None, min_length=1, max_length=256)
    api_path: str | None = Field(default=None, min_length=1, max_length=256)
    local_web_url: str | None = Field(default=None, min_length=1, max_length=256)
    local_api_url: str | None = Field(default=None, min_length=1, max_length=256)
    status: Literal["ready", "planned"] | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class AppRegistryAdminAppsOut(BaseModel):
    apps: list[AppRegistryAppOut] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


__all__ = [
    "AppRegistryAdminAppCreateIn",
    "AppRegistryAdminAppUpdateIn",
    "AppRegistryAdminAppsOut",
]
