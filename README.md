# COSC 310 Group 16

## Project Overview

This project is a restaurant ordering system developed using Python and FastAPI for COSC 310.

For Milestone 2, we integrated the customer, restaurant, menu, shopping cart, and order features into one working application.

Customers can register, log in, browse restaurants, view menu items, manage their cart, place orders, and check their order history.

The project also includes administrator permissions for managing restaurant and menu information.

## Requirements

- Python 3.12
- pip
- Git

## Setup Instructions

Clone the repository and open the project directory.

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Running the Application

From the project root, run:

```powershell
python -m uvicorn app.main:app --reload
```

After starting the server, open the following pages:

| Page | URL |
|---|---|
| Main page | http://127.0.0.1:8000/ |
| M2 application | http://127.0.0.1:8000/m2.html |
| Restaurant details frontend | http://127.0.0.1:8000/restaurant.html |
| Swagger API documentation | http://127.0.0.1:8000/docs |

Press `Ctrl+C` in the terminal to stop the server.

## Main Features

### Customer

Customers can:

- Register a new account.
- Log in using their email and password.
- View and update their profile.
- Deactivate their account.
- Browse restaurants and their menus.
- Add items to the shopping cart.
- Update item quantities or remove items.
- Complete checkout.
- View previous orders.

### Restaurant and Menu

The system supports:

- Viewing restaurant information.
- Searching and filtering restaurants.
- Viewing restaurant menus and item details.
- Creating and updating restaurants with administrator permissions.
- Creating and updating menu items with administrator permissions.
- Managing menu item availability.

### Shopping Cart and Checkout

The shopping cart allows customers to add, update, and remove items.

A cart can only contain items from one restaurant at a time. Quantities must be positive, and unavailable menu items cannot be added.

Before creating an order, the checkout process checks the customer, restaurant, and menu items again.

The order total is calculated using the current menu prices. After checkout, the order is saved and the cart is cleared.

Previous orders keep their saved prices and delivery addresses even if the menu or customer profile changes later.

## API Endpoints

### General and Restaurant APIs

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check API status |
| GET | `/restaurants` | List and search restaurants |
| GET | `/restaurants/{restaurant_id}` | Get restaurant details |
| POST | `/restaurants` | Create a restaurant (admin) |
| PUT | `/restaurants/{restaurant_id}` | Update a restaurant (admin) |
| GET | `/restaurants/{restaurant_id}/menu` | Get restaurant menu |
| GET | `/restaurants/{restaurant_id}/menu/{item_id}` | Get menu item details |
| POST | `/restaurants/{restaurant_id}/menu` | Create a menu item (admin) |
| PUT | `/restaurants/{restaurant_id}/menu/{item_id}` | Update a menu item (admin) |

### Customer APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/customers/register` | Register a customer |
| POST | `/customers/login` | Log in |
| GET | `/customers/me` | Get customer profile |
| PATCH | `/customers/me` | Update customer profile |
| DELETE | `/customers/me` | Deactivate customer account |

### Cart and Order APIs

| Method | Endpoint | Description |
|---|---|---|
| GET | `/cart` | View cart |
| POST | `/cart/items` | Add item to cart |
| PUT | `/cart/items/{item_id}` | Change item quantity |
| DELETE | `/cart/items/{item_id}` | Remove item |
| DELETE | `/cart` | Clear cart |
| POST | `/checkout` | Place an order |
| GET | `/orders` | List customer orders |
| GET | `/orders/{order_id}` | View order details |

The complete API documentation, including request formats and response models, is available at:

http://127.0.0.1:8000/docs

## Authentication and Authorization

The application uses bearer tokens for customer authentication.

After logging in, the customer receives an access token that is used when accessing protected endpoints.

Regular customers can manage their own profile, cart, and orders.

Creating or updating restaurant and menu information requires administrator permissions.

Protected endpoints return appropriate errors when a user is not authenticated or does not have permission.

## Data Storage

The project uses JSON files for data storage.

Restaurant and menu information is stored in the project's data directory.

Customer accounts, carts, and orders are stored in `data/commerce.json`.

The Commerce data file is created and updated locally and is excluded from Git tracking.

The repositories use JSON persistence so that saved information can be loaded again after restarting the application.

The project also includes temporary-file replacement when saving JSON data to reduce the risk of damaging an existing file during a failed write.

## Running Tests

The project uses pytest for automated testing.

Run all tests from the project root:

```powershell
python -m pytest -v
```

Or use the shorter output:

```powershell
python -m pytest -q
```

The tests cover restaurant and menu operations, customer authentication, shopping cart rules, checkout, order history, permissions, and data persistence.

Tests use temporary data files where needed to avoid changing the original project data.

The latest local test run completed with 60 passing tests.

### Code Coverage

To check Python code coverage, install pytest-cov:

```powershell
python -m pip install pytest-cov
```

Then run:

```powershell
python -m pytest --cov=app --cov-report=term-missing -q
```

The latest local coverage report showed 97% statement coverage.

### GitHub Actions

The repository includes a GitHub Actions workflow in `.github/workflows/tests.yml`.

The workflow installs the project dependencies and runs the automated tests when triggered by a push or pull request.

The M2 integration branch has been tested successfully using GitHub Actions.

## Project Structure

```text
app/
  api/
    routes/
      commerce_router.py
      item_router.py
      restaurant_router.py
  core/
    auth.py
    config.py
  repositories/
    commerce_repository.py
    item_repository.py
    json_storage.py
    restaurant_repository.py
  schemas/
    commerce.py
    cuisine.py
    item.py
    item_category.py
    restaurant.py
  services/
    commerce_service.py
    item_service.py
    restaurant_service.py
  main.py

data/
  items.json
  restaurants.json

docs/
  M2 Log.md
  PROVENANCE.md

tests/
  conftest.py
  test_admin_auth.py
  test_commerce_m2.py
  test_commerce_repository.py
  test_json_storage.py
  test_m2_api_integration.py
  test_main.py

web/
  index.html
  m2.html
  restaurant.html

.github/
  workflows/
    tests.yml

requirements.txt
README.md
```

## M2 Documentation

Development notes and technical decisions are recorded in `docs/M2 Log.md`.

AI usage and contribution records are maintained in `docs/PROVENANCE.md`.

GitHub commit history, pull requests, and the project workflow provide additional development and collaboration records.