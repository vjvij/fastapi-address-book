import pytest
from app.crud import address as crud
from app import schemas

def test_crud_create_address(session):
    address_in = schemas.AddressCreate(
        street="CRUD St",
        city="CRUD City",
        state="CS",
        country="CL",
        latitude=10.0,
        longitude=10.0
    )
    db_address = crud.create_address(db=session, address_in=address_in)
    assert db_address.id is not None
    assert db_address.street == "CRUD St"

def test_crud_get_address(session):
    address_in = schemas.AddressCreate(
        street="Get Me",
        city="C",
        state="S",
        country="C",
        latitude=0,
        longitude=0
    )
    db_address = crud.create_address(db=session, address_in=address_in)
    fetched = crud.get_address(db=session, address_id=db_address.id)
    assert fetched.id == db_address.id
    assert fetched.street == "Get Me"

def test_crud_update_address(session):
    address_in = schemas.AddressCreate(
        street="Old",
        city="C",
        state="S",
        country="C",
        latitude=0,
        longitude=0
    )
    db_address = crud.create_address(db=session, address_in=address_in)
    update_in = schemas.AddressUpdate(street="New")
    updated = crud.update_address(db=session, db_address=db_address, address_in=update_in)
    assert updated.street == "New"

def test_crud_delete_address(session):
    address_in = schemas.AddressCreate(
        street="Bye",
        city="C",
        state="S",
        country="C",
        latitude=0,
        longitude=0
    )
    db_address = crud.create_address(db=session, address_in=address_in)
    crud.delete_address(db=session, db_address=db_address)
    assert crud.get_address(db=session, address_id=db_address.id) is None
