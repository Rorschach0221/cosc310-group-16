"""Run from repository root with: python -m pytest tests/test_commerce_m2.py -v"""
from types import SimpleNamespace
import pytest
from fastapi import HTTPException
from app.repositories.commerce_repository import CommerceRepository
from app.services.commerce_service import CommerceService
from app.schemas.commerce import RegisterInput

class Items:
    def __init__(self):
        self.values = {
            'a': SimpleNamespace(id='a', name='Pie', price=1200, restaurant_id=1, available=True),
            'b': SimpleNamespace(id='b', name='Soup', price=700, restaurant_id=1, available=True),
            'c': SimpleNamespace(id='c', name='Pizza', price=1500, restaurant_id=2, available=True),
        }
    def get_by_item_id(self, item_id):
        return self.values.get(item_id)

class Restaurants:
    def get_by_id(self, rid):
        return SimpleNamespace(id=rid, is_open=True) if rid in ('1','2') else None

@pytest.fixture
def setup(tmp_path):
    repo = CommerceRepository(tmp_path / 'commerce.json')
    items = Items()
    service = CommerceService(repo=repo, items=items, restaurants=Restaurants())
    user = service.register(RegisterInput(name='Test', email='test@example.com', password='securepass', address='123 St'))
    return service, repo, items, user['id']

def expect_status(status, f):
    with pytest.raises(HTTPException) as caught:
        f()
    assert caught.value.status_code == status


def test_integrated_customer_to_order_and_restart(setup):
    svc, repo, items, uid = setup
    token = svc.login('test@example.com', 'securepass')['access_token']
    assert svc.authenticated(token)['id'] == uid
    svc.add(uid, 'a', 2)
    svc.add(uid, 'b', 1)
    assert svc.cart(uid)['total_cents'] == 3100
    # Current price must be authoritative during checkout
    items.values['a'].price = 1300
    order = svc.checkout(uid)
    assert order['total_cents'] == 3300
    assert order['items'][0]['unit_price_cents'] == 1300
    assert svc.cart(uid)['items'] == []
    after_restart = CommerceService(repo=CommerceRepository(repo.path), items=items, restaurants=Restaurants())
    assert after_restart.get_order(uid, order['id'])['id'] == order['id']
    assert len(after_restart.list_orders(uid)) == 1


def test_mixed_restaurants_rejected_without_mutation(setup):
    svc, repo, items, uid = setup
    svc.add(uid, 'a', 1)
    expect_status(409, lambda: svc.add(uid, 'c', 1))
    assert len(svc.cart(uid)['items']) == 1


def test_unavailable_and_invalid_quantity_rejected(setup):
    svc, repo, items, uid = setup
    items.values['a'].available = False
    expect_status(409, lambda: svc.add(uid, 'a', 1))
    expect_status(422, lambda: svc.add(uid, 'b', 0))
    assert svc.cart(uid)['items'] == []


def test_empty_checkout_and_deactivated_customer(setup):
    svc, repo, items, uid = setup
    expect_status(409, lambda: svc.checkout(uid))
    token = svc.login('test@example.com', 'securepass')['access_token']
    svc.deactivate(uid)
    expect_status(403, lambda: svc.authenticated(token))
    expect_status(401, lambda: svc.login('test@example.com', 'securepass'))


def test_failed_save_keeps_cart(setup, monkeypatch):
    svc, repo, items, uid = setup
    svc.add(uid, 'a', 1)
    original = repo.save
    def broken(_):
        raise OSError('simulated disk error')
    monkeypatch.setattr(repo, 'save', broken)
    with pytest.raises(OSError):
        svc.checkout(uid)
    monkeypatch.setattr(repo, 'save', original)
    assert svc.cart(uid)['items'][0]['item_id'] == 'a'
    assert svc.list_orders(uid) == []


def test_order_isolation(setup):
    svc, repo, items, uid = setup
    other = svc.register(RegisterInput(name='Other', email='other@example.com', password='securepass', address='456 St'))['id']
    svc.add(uid, 'a', 1)
    order = svc.checkout(uid)
    expect_status(403, lambda: svc.get_order(other, order['id']))


def test_unavailable_item_remains_visible_and_removable(setup):
    # Regression test candidate: previously GET /cart failed with 409 as soon
    # as a menu item became unavailable, trapping it in the customer's cart.
    svc, repo, items, uid = setup
    svc.add(uid, 'a', 1)
    items.values['a'].available = False
    assert svc.cart(uid)['items'][0]['item_id'] == 'a'
    expect_status(409, lambda: svc.checkout(uid))
    assert svc.remove(uid, 'a')['items'] == []


def test_unavailable_item_cannot_be_added_to_new_cart(setup):
    svc, repo, items, uid = setup
    items.values['a'].available = False
    expect_status(409, lambda: svc.add(uid, 'a', 1))
