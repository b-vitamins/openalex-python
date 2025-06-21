import pytest

from openalex.async_entities import AsyncBaseEntity
from openalex.models import BaseFilter
from openalex.config import OpenAlexConfig


class DummyEntity(AsyncBaseEntity[str, BaseFilter]):
    endpoint = "works"
    model_class = str


class FakeLogger:
    def __init__(self) -> None:
        self.warnings: list[str] = []
        self.errors: list[str] = []

    def warning(self, msg: str, *args: object) -> None:
        self.warnings.append(msg % args)

    def exception(self, msg: str, *args: object) -> None:
        self.errors.append(msg % args)


@pytest.mark.asyncio
async def test_get_many_skips_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    logger = FakeLogger()
    monkeypatch.setattr("openalex.async_entities.logger", logger)

    async def fake_get(self: AsyncBaseEntity[str, BaseFilter], eid: str) -> str:
        return f"item-{eid}"

    def fake_validate(eid: str, _typ: str) -> str:
        if eid == "bad":
            raise ValueError("bad id")
        return eid.upper()

    monkeypatch.setattr(
        "openalex.async_entities._AsyncBaseEntity.get", fake_get
    )
    monkeypatch.setattr(
        "openalex.async_entities.validate_entity_id", fake_validate
    )

    entity = DummyEntity(config=OpenAlexConfig())
    results = await entity.get_many(["a1", "bad", "a2"], max_concurrent=2)

    assert results == ["item-A1", "item-A2"]
    assert logger.warnings == ["Skipping invalid ID bad: bad id"]


@pytest.mark.asyncio
async def test_get_many_handles_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    logger = FakeLogger()
    monkeypatch.setattr("openalex.async_entities.logger", logger)

    async def fake_get(self: AsyncBaseEntity[str, BaseFilter], eid: str) -> str:
        if eid == "B2":
            raise RuntimeError("boom")
        return f"ok-{eid}"

    monkeypatch.setattr(
        "openalex.async_entities._AsyncBaseEntity.get", fake_get
    )
    monkeypatch.setattr(
        "openalex.async_entities.validate_entity_id", lambda e, _t: e
    )

    entity = DummyEntity(config=OpenAlexConfig())
    results = await entity.get_many(["A1", "B2"], max_concurrent=2)

    assert results == ["ok-A1"]
    assert logger.errors == ["Failed to fetch B2"]
