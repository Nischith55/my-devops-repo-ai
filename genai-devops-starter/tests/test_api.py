from fastapi.testclient import TestClient

from backend.main import app


def test_health_endpoint():
    client = TestClient(app)
    res = client.get('/health')
    assert res.status_code == 200
    body = res.json()
    assert body['status'] == 'ok'
    assert 'model' in body


def test_chat_endpoint_mock_mode():
    client = TestClient(app)
    res = client.post(
        '/chat',
        json={
            'prompt': 'Hello there',
            'temperature': 0.2,
            'max_tokens': 64,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert '[MOCK RESPONSE]' in body['answer']
    assert body['mock_mode'] is True
