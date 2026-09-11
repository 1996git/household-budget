from fastapi.testclient import TestClient
from main import app
from security import create_access_token
from db import get_connection

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

def test_get_expenses(auth_headers):
    response = client.get(
        "/expenses/",
        headers=auth_headers
    )

    assert response.status_code == 200

def test_get_expenses_response():
     token = create_access_token(1)
     response = client.get(
        "/expenses/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    
     assert response.status_code == 200

     data = response.json()
     assert isinstance(data, list)
     for expense in data:
         assert "id" in expense
         assert "category" in expense
         assert "amount" in expense
         assert "expense_date" in expense

def test_get_expenses_only_own_data(auth_headers, test_expense):
        response = client.get(
            "/expenses/",
             headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        ids = [expense["id"] for expense in data]
        assert test_expense in ids