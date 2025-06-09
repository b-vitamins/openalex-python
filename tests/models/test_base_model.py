from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydantic import HttpUrl
else:
    HttpUrl = str


from openalex.models.base import OpenAlexBase


class DummyModel(OpenAlexBase):
    dt: datetime
    d: date
    url: HttpUrl


def test_openalexbase_serialization() -> None:
    obj = DummyModel(
        dt=datetime(2024, 1, 1, 12, 0, 0),
        d=date(2024, 1, 1),
        url="https://example.com",
    )
    data = obj.model_dump(mode="json")
    assert data["dt"] == "2024-01-01 12:00:00"
    assert data["d"] == "2024-01-01"
    assert data["url"] == "https://example.com"
