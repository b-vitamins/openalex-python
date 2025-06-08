import pytest
from pydantic import BaseModel

from openalex.exceptions import ValidationError as OpenAlexValidationError
from openalex.models import BaseFilter
from openalex.resources.base import BaseResource


class DummyModel(BaseModel):
    id: int


class DummyResource(BaseResource[DummyModel, BaseFilter]):
    endpoint = "dummy"
    model_class = DummyModel
    filter_class = BaseFilter


def test_parse_list_error(client, httpx_mock):
    dummy = DummyResource(client)
    httpx_mock.add_response(
        url="https://api.openalex.org/dummy?mailto=test%40example.com",
        json={"results": [{}]},
    )
    with pytest.raises(OpenAlexValidationError):
        dummy.list()
