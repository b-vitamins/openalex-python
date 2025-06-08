from openalex import OpenAlexConfig


def test_headers_and_params() -> None:
    config = OpenAlexConfig(
        email="test@example.com", api_key="abc", user_agent="ua"
    )
    headers = config.headers
    assert "test@example.com" in headers["User-Agent"]
    assert headers["Authorization"] == "Bearer abc"
    assert config.params["mailto"] == "test@example.com"
