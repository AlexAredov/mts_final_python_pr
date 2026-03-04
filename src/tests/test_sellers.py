import pytest
from fastapi import status
from sqlalchemy import select

from src.models.books import Book
from src.models.sellers import Seller

API_V1_SELLERS_URL_PREFIX = "/api/v1/seller"


@pytest.mark.asyncio()
async def test_create_seller(async_client):
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe@example.com",
        "password": "supersecret",
    }
    response = await async_client.post(f"{API_V1_SELLERS_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert "password" not in response_data
    assert response_data["first_name"] == "John"
    assert response_data["last_name"] == "Doe"
    assert response_data["e_mail"] == "john.doe@example.com"
    assert response_data["id"] is not None


@pytest.mark.asyncio()
async def test_get_all_sellers(db_session, async_client):
    seller = Seller(
        first_name="Anna",
        last_name="Smith",
        e_mail="anna@example.com",
        password="secret",
    )
    db_session.add(seller)
    await db_session.flush()

    response = await async_client.get(f"{API_V1_SELLERS_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert len(payload["sellers"]) == 1
    assert payload["sellers"][0] == {
        "id": seller.id,
        "first_name": "Anna",
        "last_name": "Smith",
        "e_mail": "anna@example.com",
    }
    assert "password" not in payload["sellers"][0]


@pytest.mark.asyncio()
async def test_get_single_seller_with_books(db_session, async_client):
    seller = Seller(
        first_name="Nikolay",
        last_name="Petrov",
        e_mail="n.petrov@example.com",
        password="secret",
    )
    db_session.add(seller)
    await db_session.flush()
    book = Book(title="Book 1", author="Author 1", year=2024, pages=111, seller_id=seller.id)
    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"{API_V1_SELLERS_URL_PREFIX}/{seller.id}")

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert payload["id"] == seller.id
    assert payload["first_name"] == "Nikolay"
    assert payload["last_name"] == "Petrov"
    assert payload["e_mail"] == "n.petrov@example.com"
    assert "password" not in payload
    assert payload["books"] == [
        {
            "id": book.id,
            "title": "Book 1",
            "author": "Author 1",
            "year": 2024,
            "pages": 111,
            "seller_id": seller.id,
        }
    ]


@pytest.mark.asyncio()
async def test_update_seller(db_session, async_client):
    seller = Seller(
        first_name="Old",
        last_name="Name",
        e_mail="old@example.com",
        password="secret",
    )
    db_session.add(seller)
    await db_session.flush()

    payload = {
        "first_name": "New",
        "last_name": "Seller",
        "e_mail": "new@example.com",
    }
    response = await async_client.put(f"{API_V1_SELLERS_URL_PREFIX}/{seller.id}", json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == {
        "id": seller.id,
        "first_name": "New",
        "last_name": "Seller",
        "e_mail": "new@example.com",
    }
    assert "password" not in data


@pytest.mark.asyncio()
async def test_delete_seller_cascade_books(db_session, async_client):
    seller = Seller(
        first_name="Delete",
        last_name="Me",
        e_mail="delete.me@example.com",
        password="secret",
    )
    db_session.add(seller)
    await db_session.flush()
    db_session.add(Book(title="Book 1", author="Author", year=2024, pages=111, seller_id=seller.id))
    db_session.add(Book(title="Book 2", author="Author", year=2024, pages=222, seller_id=seller.id))
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_SELLERS_URL_PREFIX}/{seller.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()
    seller_from_db = await db_session.get(Seller, seller.id)
    assert seller_from_db is None
    books = (await db_session.execute(select(Book))).scalars().all()
    assert books == []
