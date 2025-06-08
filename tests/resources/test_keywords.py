from openalex.models import Keyword


def test_list_keywords(client, httpx_mock, mock_list_response):
    httpx_mock.add_response(
        url="https://api.openalex.org/keywords?mailto=test%40example.com",
        json=mock_list_response,
    )
    result = client.keywords.list()
    assert isinstance(result.results[0].id, str)
