import pytest

from openalex.entities import AsyncBaseEntity
from openalex.models import BaseFilter, Work
from openalex.config import OpenAlexConfig


class DummyEntity(AsyncBaseEntity[Work, BaseFilter]):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.endpoint = "works"
        self.model_class = Work


class FakeLogger:
    def __init__(self) -> None:
        self.warnings: list[str] = []
        self.errors: list[str] = []

    def warning(self, msg: str, *args: object) -> None:
        self.warnings.append(msg % args)

    def exception(self, msg: str, *args: object) -> None:
        formatted_msg = msg % args if args else msg
        self.errors.append(formatted_msg)


@pytest.mark.asyncio
async def test_get_many_skips_invalid(
    monkeypatch: pytest.MonkeyPatch, mock_work_data
) -> None:
    """Test that get_many skips invalid IDs and logs warnings."""
    logger = FakeLogger()
    monkeypatch.setattr("openalex.entities.logger", logger)

    # Mock the _get_single_entity method to return a Work object
    async def fake_get_single(
        self: AsyncBaseEntity[Work, BaseFilter], eid: str, params=None
    ) -> Work:
        return Work.model_validate(
            {**mock_work_data, "id": f"https://openalex.org/{eid.upper()}"}
        )

    def fake_validate(eid: str, _typ: str) -> str:
        if eid == "bad":
            raise ValueError("bad id")
        return eid.upper()

    monkeypatch.setattr(
        "openalex.templates.AsyncEntityTemplate._get_single_entity",
        fake_get_single,
    )
    monkeypatch.setattr("openalex.templates.validate_entity_id", fake_validate)

    entity = DummyEntity(config=OpenAlexConfig())
    results = await entity.get_many(["a1", "bad", "a2"], max_concurrent=2)

    assert len(results) == 2
    assert all(isinstance(r, Work) for r in results)
    assert results[0].id == "https://openalex.org/A1"
    assert results[1].id == "https://openalex.org/A2"
    assert logger.warnings == ["Skipping invalid ID bad: bad id"]


@pytest.mark.asyncio
async def test_get_many_handles_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    logger = FakeLogger()
    monkeypatch.setattr("openalex.templates.logger", logger)

    async def fake_get_single(
        self: AsyncBaseEntity[str, BaseFilter], eid: str, params=None
    ) -> str:
        if eid == "B2":
            raise RuntimeError("boom")
        return f"ok-{eid}"

    monkeypatch.setattr(
        "openalex.templates.AsyncEntityTemplate._get_single_entity",
        fake_get_single,
    )
    monkeypatch.setattr(
        "openalex.templates.validate_entity_id", lambda e, _t: e
    )

    entity = DummyEntity(config=OpenAlexConfig())
    results = await entity.get_many(["A1", "B2"], max_concurrent=2)

    assert results == ["ok-A1"]
    assert logger.errors == ["Failed to fetch B2"]
