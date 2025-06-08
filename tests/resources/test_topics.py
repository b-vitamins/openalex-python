def test_list_topics(client, httpx_mock, mock_list_response):
    httpx_mock.add_response(
        url="https://api.openalex.org/topics?mailto=test%40example.com",
        json=mock_list_response,
    )
    result = client.topics.list()
    assert len(result.results) == 1
