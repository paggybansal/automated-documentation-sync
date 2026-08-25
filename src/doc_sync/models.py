from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

HTTPMethod = Literal["GET", "POST", "PUT", "PATCH", "DELETE"]


@dataclass(frozen=True, slots=True)
class Endpoint:
    method: HTTPMethod
    path: str
    summary: str
    authentication: str


@dataclass(frozen=True, slots=True)
class Manifest:
    service_name: str
    version: str
    endpoints: list[Endpoint]
