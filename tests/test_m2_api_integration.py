from fastapi.testclient import TestClient
from app.main import app
from app.api.routes.commerce_router import service
from app.repositories.commerce_repository import CommerceRepository


def test_real_menu_to_order_via_api(tmp_path, monkeypatch):
    monkeypatch.setattr(service, 'repo', CommerceRepository(tmp_path / 'commerce.json'))
    service.sessions.clear()
    client = TestClient(app)
    customer = client.post('/customers/register', json={
        'name': 'Demo', 'email': 'demo@example.com',
        'password': 'correct-horse-battery', 'address': '123 Main Street',
    })
    assert customer.status_code == 201, customer.text
    login = client.post('/customers/login', json={
        'email': 'demo@example.com', 'password': 'correct-horse-battery',
    })
    assert login.status_code == 200, login.text
    auth = {'Authorization': f"Bearer {login.json()['access_token']}"}
    menus = client.get('/restaurants/1/menu')
    assert menus.status_code == 200
    item = menus.json()[0]
    assert client.get('/cart').status_code == 401
    added = client.post('/cart/items', headers=auth, json={'item_id': item['id'], 'quantity': 2})
    assert added.status_code == 200, added.text
    assert added.json()['total_cents'] == 2 * item['price']
    checked = client.post('/checkout', headers=auth)
    assert checked.status_code == 201, checked.text
    order = checked.json()
    assert order['total_cents'] == 2 * item['price']
    assert client.get('/cart', headers=auth).json()['items'] == []
    assert client.get(f"/orders/{order['id']}", headers=auth).json()['id'] == order['id']
    assert CommerceRepository(tmp_path / 'commerce.json').read()['orders'][order['id']]['id'] == order['id']


def test_real_menu_availability_round_trip(tmp_path, monkeypatch):
    import json
    from app.repositories import item_repository
    source = item_repository.DATA_PATH
    temp = tmp_path / 'items.json'
    temp.write_text(source.read_text(encoding='utf-8'), encoding='utf-8')
    monkeypatch.setattr(item_repository, 'DATA_PATH', temp)
    monkeypatch.setattr(service, 'repo', CommerceRepository(tmp_path / 'commerce.json'))
    service.sessions.clear()
    client = TestClient(app)
    client.post('/customers/register', json={'name':'Demo','email':'other@example.com','password':'secret1234','address':'123 St'})
    token = client.post('/customers/login',json={'email':'other@example.com','password':'secret1234'}).json()['access_token']
    auth = {'Authorization':f'Bearer {token}'}
    item = client.get('/restaurants/1/menu').json()[0]
    assert client.post('/cart/items', headers=auth, json={'item_id':item['id'],'quantity':1}).status_code == 200
    data = json.loads(temp.read_text())
    for row in data:
        if row['id'] == item['id']:
            row['available'] = False
    temp.write_text(json.dumps(data), encoding='utf-8')
    assert client.get('/cart',headers=auth).status_code == 200
    assert client.post('/checkout',headers=auth).status_code == 409
    assert client.delete(f"/cart/items/{item['id']}",headers=auth).status_code == 200
