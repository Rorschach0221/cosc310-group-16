from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.schemas.commerce import RegisterInput, LoginInput, CustomerUpdate, CartAdd, QuantityUpdate
from app.services.commerce_service import CommerceService

router = APIRouter(tags=['M2 Commerce'])
service = CommerceService()
bearer = HTTPBearer(auto_error=False)


def current(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    return service.authenticated(credentials.credentials if credentials else None)


@router.post('/customers/register', status_code=201, summary='Register a new customer')
def register(data: RegisterInput):
    return service.register(data)


@router.post('/customers/login', summary='Sign in and obtain a bearer token')
def login(data: LoginInput):
    return service.login(data.email, data.password)


@router.get('/customers/me', summary='Retrieve the authenticated customer')
def me(user=Depends(current)):
    return {k: v for k, v in user.items() if k not in ('password_hash', 'salt')}


@router.patch('/customers/me', summary='Update name or delivery address')
def update(data: CustomerUpdate, user=Depends(current)):
    return service.update_customer(user['id'], data.model_dump(exclude_none=True))


@router.delete('/customers/me', status_code=204, summary='Deactivate customer account')
def deactivate(user=Depends(current)):
    service.deactivate(user['id'])


@router.get('/cart', summary='Retrieve cart and authoritative totals')
def get_cart(user=Depends(current)):
    return service.cart(user['id'])


@router.post('/cart/items', summary='Add a menu item to the active cart')
def add_item(data: CartAdd, user=Depends(current)):
    return service.add(user['id'], data.item_id, data.quantity)


@router.put('/cart/items/{item_id}', summary='Change an item quantity')
def change_item(item_id: str, data: QuantityUpdate, user=Depends(current)):
    return service.change(user['id'], item_id, data.quantity)


@router.delete('/cart/items/{item_id}', summary='Remove an item from the cart')
def remove_item(item_id: str, user=Depends(current)):
    return service.remove(user['id'], item_id)


@router.delete('/cart', summary='Clear the active cart')
def clear_cart(user=Depends(current)):
    return service.clear(user['id'])


@router.post('/checkout', status_code=201, summary='Validate and persist order before clearing cart')
def checkout(user=Depends(current)):
    return service.checkout(user['id'])


@router.get('/orders', summary='List orders belonging to signed-in customer')
def orders(user=Depends(current)):
    return service.list_orders(user['id'])


@router.get('/orders/{order_id}', summary='Retrieve a customer order')
def order(order_id: str, user=Depends(current)):
    return service.get_order(user['id'], order_id)
