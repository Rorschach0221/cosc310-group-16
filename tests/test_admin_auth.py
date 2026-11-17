import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.auth import current_user

from fastapi import HTTPException

from app.core.auth import require_admin


def test_admin_role_is_allowed():
    user = {"id": "admin-test", "role": "admin"}
    assert require_admin(user) == user


def test_customer_role_is_forbidden():
    user = {"id": "customer-test", "role": "customer"}

    with pytest.raises(HTTPException) as error:
        require_admin(user)

    assert error.value.status_code == 403


def test_missing_admin_role_is_forbidden():
    user = {"id": "missing-role"}

    with pytest.raises(HTTPException) as error:
        require_admin(user)

    assert error.value.status_code == 403

def test_admin_can_create_restaurant(isolated_restaurants):
    test_admin = {
        "id": "test-admin",
        "role": "admin",
        "active": True,
    }

    app.dependency_overrides[current_user] = lambda: test_admin

    try:
        client = TestClient(app)

        restaurant = {
            "name": "Test Admin Restaurant",
            "cuisine": "ASIAN",
            "description": "Restaurant created by admin test",
            "image_url": "https://example.com/test.jpg",
            "is_open": True,
            "rating": 4.5,
        }

        response = client.post("/restaurants", json=restaurant)

        assert response.status_code == 201
    finally:
        app.dependency_overrides.pop(current_user, None)

def test_anonymous_cannot_create_restaurant():
    client = TestClient(app)

    response = client.post("/restaurants", json={
        "name": "Unauthorized Restaurant",
        "cuisine": "ASIAN",
        "description": "Test restaurant",
        "image_url": "https://example.com/test.jpg",
        "is_open": True,
        "rating": 4.5,
    })

    assert response.status_code == 401



def test_customer_cannot_create_restaurant(tmp_path, monkeypatch):
    from app.api.routes import commerce_router
    from app.repositories.commerce_repository import CommerceRepository
    from app.services.commerce_service import CommerceService

    test_file = tmp_path / "commerce.json"

    test_service = CommerceService(
        repo=CommerceRepository(path=test_file)
    )

    monkeypatch.setattr(commerce_router, "service", test_service)

    client = TestClient(app)

    customer = {
        "name": "Test Customer",
        "email": "rbac-customer@example.com",
        "password": "TestPassword123!",
        "address": "123 Test Street",
    }

    register_response = client.post(
        "/customers/register",
        json=customer,
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/customers/login",
        json={
            "email": customer["email"],
            "password": customer["password"],
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    restaurant = {
        "name": "Unauthorized Restaurant",
        "cuisine": "ASIAN",
        "description": "Test restaurant",
        "image_url": "https://example.com/test.jpg",
        "is_open": True,
        "rating": 4.5,
    }

    response = client.post(
        "/restaurants",
        json=restaurant,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403

    menu_item = {
        "name": "Unauthorized Item",
        "cuisine": "ASIAN",
        "category": "Main",
        "price": 999,
        "description": "Permission test",
        "image_url": "https://example.com/item.jpg",
    }

    menu_response = client.post(
        "/restaurants/1/menu",
        json=menu_item,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert menu_response.status_code == 403



def test_anonymous_cannot_create_menu_item():
    client = TestClient(app)

    response = client.post(
        "/restaurants/1/menu",
        json={
            "name": "Test Item",
            "cuisine": "ASIAN",
            "category": "Main",
            "price": 999,
        },
    )

    assert response.status_code == 401


def test_admin_can_manage_menu(isolated_items, admin_client):
    new_item = {
        "name": "Admin Test Dish",
        "cuisine": "ASIAN",
        "category": "Main",
        "price": 1299,
        "description": "Admin menu test",
        "image_url": "https://example.com/admin-dish.jpg",
    }

    created = admin_client.post(
        "/restaurants/1/menu",
        json=new_item,
    )

    assert created.status_code == 201

    item_id = created.json()["id"]

    updated_item = {
        **new_item,
        "price": 1499,
    }

    updated = admin_client.put(
        f"/restaurants/1/menu/{item_id}",
        json=updated_item,
    )

    assert updated.status_code == 200
    assert updated.json()["price"] == 1499


def test_real_admin_token_can_create_restaurant(
    tmp_path, monkeypatch, isolated_restaurants, isolated_items
):
    from app.api.routes import commerce_router
    from app.repositories.commerce_repository import CommerceRepository
    from app.services.commerce_service import CommerceService

    test_file = tmp_path / "admin_commerce.json"
    test_service = CommerceService(
        repo=CommerceRepository(path=test_file)
    )

    monkeypatch.setattr(commerce_router, "service", test_service)

    client = TestClient(app)

    customer = {
        "name": "Test Admin",
        "email": "admin-test@example.com",
        "password": "TestPassword123!",
        "address": "123 Test Street",
    }

    register_response = client.post(
        "/customers/register",
        json=customer,
    )
    assert register_response.status_code == 201

    with test_service.repo.lock:
        db = test_service.repo.read()

        admin_found = False

        for user in db["customers"].values():
            if user["email"] == customer["email"]:
                user["role"] = "admin"
                admin_found = True
                break

        assert admin_found
        test_service.repo.save(db)

    login_response = client.post(
        "/customers/login",
        json={
            "email": customer["email"],
            "password": customer["password"],
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    restaurant = {
        "name": "Admin Test Restaurant",
        "cuisine": "ASIAN",
        "description": "Admin integration test",
        "image_url": "https://example.com/admin.jpg",
        "is_open": True,
        "rating": 4.5,
    }

    response = client.post(
        "/restaurants",
        json=restaurant,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Admin Test Restaurant"

    restaurant_id = response.json()["id"]

    menu_item = {
        "name": "Admin Test Dish",
        "cuisine": "ASIAN",
        "category": "Main",
        "price": 1299,
        "description": "Admin token menu test",
        "image_url": "https://example.com/admin-dish.jpg",
    }

    menu_response = client.post(
        f"/restaurants/{restaurant_id}/menu",
        json=menu_item,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert menu_response.status_code == 201

    item_id = menu_response.json()["id"]

    updated_item = {
        **menu_item,
        "price": 1599,
    }

    update_response = client.put(
        f"/restaurants/{restaurant_id}/menu/{item_id}",
        json=updated_item,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["price"] == 1599


def test_customer_cannot_update_restaurant_or_menu(tmp_path, monkeypatch):
    from app.api.routes import commerce_router
    from app.repositories.commerce_repository import CommerceRepository
    from app.services.commerce_service import CommerceService

    test_service = CommerceService(
        repo=CommerceRepository(tmp_path / "commerce.json")
    )
    monkeypatch.setattr(commerce_router, "service", test_service)

    client = TestClient(app)

    customer = {
        "name": "Permission Test",
        "email": "update-permission@example.com",
        "password": "TestPassword123!",
        "address": "123 Test Street",
    }

    registered = client.post("/customers/register", json=customer)
    assert registered.status_code == 201

    login = client.post(
        "/customers/login",
        json={
            "email": customer["email"],
            "password": customer["password"],
        },
    )
    assert login.status_code == 200

    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    restaurant_update = {
        "name": "Unauthorized Update",
        "cuisine": "ASIAN",
        "description": "Should not be saved",
        "image_url": "https://example.com/test.jpg",
        "is_open": True,
        "rating": 4.5,
    }

    response = client.put(
        "/restaurants/1",
        json=restaurant_update,
        headers=headers,
    )
    assert response.status_code == 403

    item_update = {
        "name": "Unauthorized Item Update",
        "cuisine": "NORAM",
        "category": "Main",
        "price": 999,
        "description": "Should not be saved",
        "image_url": "https://example.com/item.jpg",
    }

    response = client.put(
        "/restaurants/1/menu/R1-beef-pie",
        json=item_update,
        headers=headers,
    )
    assert response.status_code == 403




