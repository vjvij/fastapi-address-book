def test_create_address(client):
    """Test creating a new address."""
    response = client.post(
        "/addresses/",
        json={
            "street": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "country": "Testland",
            "latitude": 52.0,
            "longitude": 4.0,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["street"] == "123 Test St"
    assert "id" in data


def test_list_addresses(client):
    """Test listing all addresses."""
    # Create two addresses
    client.post(
        "/addresses/",
        json={
            "street": "A1",
            "city": "C1",
            "state": "S1",
            "country": "CN",
            "latitude": 0,
            "longitude": 0,
        },
    )
    client.post(
        "/addresses/",
        json={
            "street": "A2",
            "city": "C2",
            "state": "S2",
            "country": "CN",
            "latitude": 1,
            "longitude": 1,
        },
    )

    response = client.get("/addresses/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_address_by_id(client):
    """Test retrieving a single address by its ID."""
    post_resp = client.post(
        "/addresses/",
        json={
            "street": "Find Me",
            "city": "C1",
            "state": "S1",
            "country": "CN",
            "latitude": 10,
            "longitude": 10,
        },
    )
    address_id = post_resp.json()["id"]

    response = client.get(f"/addresses/{address_id}")
    assert response.status_code == 200
    assert response.json()["street"] == "Find Me"


def test_get_nonexistent_address(client):
    """Test 404 response for missing address."""
    response = client.get("/addresses/9999")
    assert response.status_code == 404


def test_nearby_search(client):
    """Test finding addresses within a radius."""
    # Point A: Amsterdam (approx)
    client.post(
        "/addresses/",
        json={
            "street": "Amsterdam",
            "city": "AMS",
            "state": "NH",
            "country": "NL",
            "latitude": 52.3676,
            "longitude": 4.9041,
        },
    )
    # Point B: Utrecht (approx ~35km from AMS)
    client.post(
        "/addresses/",
        json={
            "street": "Utrecht",
            "city": "UTR",
            "state": "UT",
            "country": "NL",
            "latitude": 52.0907,
            "longitude": 5.1214,
        },
    )

    # Search within 10km of AMS — should only find Amsterdam
    resp_small = client.get("/addresses/nearby?latitude=52.3676&longitude=4.9041&distance_km=10")
    assert len(resp_small.json()) == 1
    assert resp_small.json()[0]["street"] == "Amsterdam"

    # Search within 50km of AMS — should find both
    resp_large = client.get("/addresses/nearby?latitude=52.3676&longitude=4.9041&distance_km=50")
    assert len(resp_large.json()) == 2


def test_update_address(client):
    """Test partially updating an address."""
    post_resp = client.post(
        "/addresses/",
        json={
            "street": "Old Street",
            "city": "Old City",
            "state": "S",
            "country": "C",
            "latitude": 0,
            "longitude": 0,
        },
    )
    address_id = post_resp.json()["id"]

    # Update only the city
    update_resp = client.patch(f"/addresses/{address_id}", json={"city": "New City"})
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["city"] == "New City"
    assert data["street"] == "Old Street"  # Unchanged


def test_delete_address(client):
    """Test deleting an address."""
    post_resp = client.post(
        "/addresses/",
        json={
            "street": "Delete Me",
            "city": "C",
            "state": "S",
            "country": "C",
            "latitude": 0,
            "longitude": 0,
        },
    )
    address_id = post_resp.json()["id"]

    del_resp = client.delete(f"/addresses/{address_id}")
    assert del_resp.status_code == 204

    # Verify it's gone
    get_resp = client.get(f"/addresses/{address_id}")
    assert get_resp.status_code == 404


def test_invalid_coordinates(client):
    """Test that invalid coordinates are rejected (validation test)."""
    response = client.post(
        "/addresses/",
        json={
            "street": "Bad Coords",
            "city": "C",
            "state": "S",
            "country": "C",
            "latitude": 100,  # Max is 90
            "longitude": 0,
        },
    )
    assert response.status_code == 422
