

def test_list_publishers(client, httpx_mock, mock_list_response):
    httpx_mock.add_response(
        url="https://api.openalex.org/publishers?mailto=test%40example.com",
        json=mock_list_response,
    )
    result = client.publishers.list()
    assert result.meta.count == 100
