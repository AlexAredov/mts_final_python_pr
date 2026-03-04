import pytest
from fastapi import status

from src.models.sellers import Seller

API_V1_TOKEN_URL_PREFIX = "/api/v1/token"


@pytest.mark.asyncio()
async def test_create_token(async_client, db_session):
    seller = Seller(
        first_name="Token",
        last_name="User",
        e_mail="token.user@example.com",
        password="my-secret-password",
    )
    db_session.add(seller)
    await db_session.flush()

    payload = {
        "e_mail": "token.user@example.com",
        "password": "my-secret-password",
    }
    response = await async_client.post(f"{API_V1_TOKEN_URL_PREFIX}/", json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"].split(".")) == 3


@pytest.mark.asyncio()
async def test_create_token_with_wrong_password(async_client, db_session):
    seller = Seller(
        first_name="Token",
        last_name="User",
        e_mail="token.user2@example.com",
        password="my-secret-password",
    )
    db_session.add(seller)
    await db_session.flush()

    payload = {
        "e_mail": "token.user2@example.com",
        "password": "wrong-password",
    }
    response = await async_client.post(f"{API_V1_TOKEN_URL_PREFIX}/", json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect e_mail or password"
