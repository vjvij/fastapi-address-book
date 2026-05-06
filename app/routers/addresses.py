"""
routers/addresses.py
--------------------
FastAPI router for all address-related endpoints.

Endpoints:
    POST   /addresses/          — Create a new address
    GET    /addresses/          — List all addresses (paginated)
    GET    /addresses/nearby    — Get addresses within a radius
    GET    /addresses/{id}      — Get a single address by ID
    PUT    /addresses/{id}      — Update an address (partial updates supported)
    DELETE /addresses/{id}      — Delete an address
"""

import logging
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import address as crud
from app import schemas
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"],
)



@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new address",
    description=(
        "Creates a new address record in the database. "
        "Latitude must be between -90 and 90; longitude between -180 and 180."
    ),
)
def create_address(
    address_in: schemas.AddressCreate,
    db: Annotated[Session, Depends(get_db)],
) -> schemas.AddressResponse:
    """Create and persist a new address."""
    try:
        logger.info("Request to create address: %s, %s", address_in.street, address_in.city)
        return crud.create_address(db=db, address_in=address_in)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error creating address: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the address."
        )




@router.get(
    "/",
    summary="List all addresses",
    description="Returns a paginated list of all addresses stored in the database.",
)
def list_addresses(
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0, description="Number of records to skip (offset)")] = 0,
    limit: Annotated[int, Query(ge=1, le=500, description="Maximum number of records to return")] = 100,
) -> List[schemas.AddressResponse]:
    """Retrieve a paginated list of all addresses."""
    try:
        logger.info("Request to list addresses — skip=%d, limit=%d", skip, limit)
        return crud.get_addresses(db=db, skip=skip, limit=limit)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error listing addresses: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving addresses."
        )




@router.get(
    "/nearby",
    summary="Find addresses within a given distance",
    description=(
        "Returns all addresses within `distance_km` kilometres of the provided "
        "latitude/longitude coordinates. Uses the Haversine formula for accurate "
        "great-circle distance calculation."
    ),
)
def get_nearby_addresses(
    db: Annotated[Session, Depends(get_db)],
    latitude: Annotated[float, Query(ge=-90.0, le=90.0, description="Center latitude in decimal degrees")],
    longitude: Annotated[float, Query(ge=-180.0, le=180.0, description="Center longitude in decimal degrees")],
    distance_km: Annotated[float, Query(gt=0, description="Search radius in kilometres")],
) -> List[schemas.AddressResponse]:
    """Return addresses within the specified distance from a coordinate pair."""
    try:
        logger.info(
            "Nearby search: center=(%.4f, %.4f), radius=%.2f km",
            latitude, longitude, distance_km,
        )
        return crud.get_addresses_within_distance(
            db=db,
            latitude=latitude,
            longitude=longitude,
            distance_km=distance_km,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error in nearby search: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during the nearby search."
        )




@router.get(
    "/{address_id}",
    summary="Get a single address by ID",
    description="Retrieves the full details of one address by its unique integer ID.",
)
def get_address(
    address_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> schemas.AddressResponse:
    """Fetch a single address or raise 404 if not found."""
    try:
        logger.info("Request to get address id=%d", address_id)
        db_address = crud.get_address(db=db, address_id=address_id)
        if db_address is None:
            logger.warning("Address id=%d not found", address_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Address with id={address_id} not found.",
            )
        return db_address
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error retrieving address id=%d: %s", address_id, str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the address."
        )




@router.patch(
    "/{address_id}",
    summary="Update an existing address (partial)",
    description=(
        "Partially updates an existing address. "
        "Only the fields included in the request body are modified; "
        "all other fields retain their current values. "
        "At least one field must be provided."
    ),
)
def update_address(
    address_id: int,
    address_in: schemas.AddressUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> schemas.AddressResponse:
    """Partially or fully update an existing address record."""
    try:
        logger.info("Request to update address id=%d", address_id)
        db_address = crud.get_address(db=db, address_id=address_id)
        if db_address is None:
            logger.warning("Update failed — address id=%d not found", address_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Address with id={address_id} not found.",
            )
        return crud.update_address(db=db, db_address=db_address, address_in=address_in)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error updating address id=%d: %s", address_id, str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the address."
        )




@router.delete(
    "/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an address",
    description="Permanently removes an address from the database by its ID.",
)
def delete_address(
    address_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Delete an address record, or raise 404 if it does not exist."""
    try:
        logger.info("Request to delete address id=%d", address_id)
        db_address = crud.get_address(db=db, address_id=address_id)
        if db_address is None:
            logger.warning("Delete failed — address id=%d not found", address_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Address with id={address_id} not found.",
            )
        crud.delete_address(db=db, db_address=db_address)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error deleting address id=%d: %s", address_id, str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the address."
        )
