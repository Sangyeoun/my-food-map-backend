# Design Ref: §8.2 L1 API Test Scenarios #11-13
from unittest.mock import patch

import httpx

GOOGLE_API_RESPONSE = {
    "places": [
        {
            "id": "ChIJ123",
            "displayName": {"text": "이치란 라멘"},
            "formattedAddress": "도쿄도 시부야구",
            "location": {"latitude": 35.6595, "longitude": 139.7005},
        }
    ]
}


def test_search_places_returns_array_with_google_place_id(client):
    # Scenario #11: 정상 검색 (Google API mock)
    mock_response = httpx.Response(
        200, json=GOOGLE_API_RESPONSE, request=httpx.Request("POST", "https://example.com")
    )
    with patch("httpx.post", return_value=mock_response):
        response = client.get("/places/search?query=라멘")

    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert all("google_place_id" in item for item in data)


def test_search_places_missing_query_returns_400(client):
    # Scenario #12: query 파라미터 누락
    response = client.get("/places/search")

    assert response.status_code == 400
    assert "errors" in response.json()["error"]["details"]


def test_search_places_google_api_failure_returns_502(client):
    # Scenario #13: Google API 실패 시뮬레이션
    with patch("httpx.post", side_effect=httpx.ConnectTimeout("timeout")):
        response = client.get("/places/search?query=x")

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "EXTERNAL_API_ERROR"
