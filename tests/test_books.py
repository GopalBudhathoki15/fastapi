import copy
import pathlib
import sys

import pytest
from fastapi.testclient import TestClient

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import main  # noqa: E402  # placed after path setup


@pytest.fixture(autouse=True)
def reset_books():
    """Reset in-memory data before each test."""
    main.BOOKS[:] = copy.deepcopy(
        [
            {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
            {"id": 2, "title": "Deep Work", "author": "Cal Newport"},
            {"id": 3, "title": "Atomic Habits", "author": "James Clear"},
        ]
    )
    yield


@pytest.fixture()
def client():
    return TestClient(main.app)


def test_list_books(client):
    response = client.get("/books")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert len(body["items"]) == 3


def test_create_book_success(client):
    response = client.post(
        "/books", json={"title": "The Pragmatic Programmer", "author": "Andrew Hunt"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 4
    assert body["title"] == "The Pragmatic Programmer"


def test_create_book_duplicate_title_rejected(client):
    response = client.post("/books", json={"title": "Clean Code", "author": "Bob"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Book title already exists"

def test_list_books_filters_by_author(client):
    response = client.get("/books", params={"author": "martin"})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Clean Code"


def test_list_books_pagination(client):
    response = client.get("/books", params={"skip": 1, "limit": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Deep Work"


def test_get_book_not_found(client):
    response = client.get("/books/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


def test_put_rejects_duplicate_title(client):
    response = client.put(
        "/books/1", json={"title": "Deep Work", "author": "Robert C. Martin"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Book title already exists"


def test_patch_rejects_duplicate_title(client):
    response = client.patch("/books/3", json={"title": "Clean Code"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Book title already exists"
