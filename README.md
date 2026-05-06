# 📍 Address Book API

A RESTful API for managing an address book, built with **FastAPI** and **SQLite**.

## Features

-  **Create** addresses with full validation (coordinates, required fields)
-  **Read** a single address or a paginated list of all addresses
-  **Update** addresses (partial updates supported — only send what you want to change)
-  **Delete** addresses
-  **Find nearby addresses** within a given distance (km) using the Haversine formula
-  **SQLite** persistence — zero configuration required
-  **Swagger UI** auto-generated at `/docs`
-  Structured logging throughout
-  Pydantic v2 validation with descriptive error messages

---

## Project Structure

```
address-book/
├── app/
│   ├── crud/                # Modular Data Access Layer
│   │   ├── __init__.py
│   │   └── address.py       # CRUD operations for addresses
│   ├── routers/             # API Route definitions ONLY
│   │   ├── __init__.py
│   │   └── addresses.py
│   ├── main.py              # Application entry point
│   ├── database.py          # SQLAlchemy setup
│   ├── models.py            # ORM models
│   ├── schemas.py           # Pydantic validation models
│   └── utils.py             # Haversine & helper functions
├── tests/                   # Automated Test Suite
│   ├── conftest.py          # Pytest fixtures & DB mocking
│   ├── test_api_addresses.py # API integration tests
│   └── test_crud_addresses.py # CRUD unit tests
├── requirements.txt
└── README.md
```

---

## How to Run

Follow these exact terminal commands to set up and execute the application:

### 1. Navigate to the project directory
```bash
cd address-book
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the development server
```bash
uvicorn app.main:app --reload
```

The API will be available at: **http://127.0.0.1:8000**

Navigate to **http://127.0.0.1:8000/docs** in your browser to explore and test all endpoints interactively.

---

## Automated Testing

The project includes a comprehensive test suite using **pytest** and **httpx**.

### Run all tests:
```bash
pytest
```

The tests use an **in-memory SQLite database**, ensuring they are fast and do not affect your local `address_book.db` file.

The API will be available at: **http://127.0.0.1:8000**

### 5. Open the Swagger UI

Navigate to **http://127.0.0.1:8000/docs** in your browser to explore and test all endpoints interactively.

---

## API Endpoints

| Method    | Endpoint              | Description                                      |
|-----------|-----------------------|--------------------------------------------------|
| `POST`    | `/addresses/`         | Create a new address                             |
| `GET`     | `/addresses/`         | List all addresses (supports `skip` & `limit`)   |
| `GET`     | `/addresses/nearby`   | Find addresses within a radius (km)              |
| `GET`     | `/addresses/{id}`     | Get a single address by ID                       |
| `PATCH`   | `/addresses/{id}`     | Partially update an address (send only changed fields) |
| `DELETE`  | `/addresses/{id}`     | Delete an address                                |

---

## Example Requests

### Create an address

```bash
curl -X POST http://127.0.0.1:8000/addresses/ \
  -H "Content-Type: application/json" \
  -d '{
    "street": "Damrak 1",
    "city": "Amsterdam",
    "state": "North Holland",
    "country": "Netherlands",
    "postal_code": "1012 LG",
    "latitude": 52.3764,
    "longitude": 4.8997
  }'
```

### Find nearby addresses

```bash
curl "http://127.0.0.1:8000/addresses/nearby?latitude=52.3764&longitude=4.8997&distance_km=10"
```

### Update an address (partial)

```bash
curl -X PATCH http://127.0.0.1:8000/addresses/1 \
  -H "Content-Type: application/json" \
  -d '{"city": "Rotterdam"}'
```

### Delete an address

```bash
curl -X DELETE http://127.0.0.1:8000/addresses/1
```

---

## Coordinate Validation

- **Latitude**: must be between `-90.0` and `90.0`
- **Longitude**: must be between `-180.0` and `180.0`

Invalid coordinates return a `422 Unprocessable Entity` response with detailed error messages.

---

## Distance Calculation

The `/addresses/nearby` endpoint uses the **Haversine formula** to calculate the great-circle distance between the provided center coordinates and every stored address, returning only those within the specified radius.

---

## Technology Stack

| Library      | Purpose                            |
|--------------|------------------------------------|
| FastAPI      | Web framework + automatic Swagger  |
| Uvicorn      | ASGI server                        |
| SQLAlchemy   | ORM + database abstraction layer   |
| Pydantic v2  | Request/response validation        |
| SQLite       | Embedded database (no setup needed)|
