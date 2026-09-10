from fastapi.testclient import TestClient
from main import app
from security import create_access_token

client = TestClient(app)

def test_get_expense_not_found():
    token = create_access_token(1)
    response = client.get(
        "/expenses/999999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404