

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from app import models, schemas
from app.utils import haversine_distance

logger = logging.getLogger(__name__)



def create_address(db: Session, address_in: schemas.AddressCreate) -> models.Address:
    """
    Persist a new address record to the database.

    Args:
        db         : Active SQLAlchemy database session.
        address_in : Validated Pydantic schema containing the new address data.

    Returns:
        The newly created Address ORM instance (with auto-generated id & timestamps).
    """
    try:
        db_address = models.Address(**address_in.model_dump())
        db.add(db_address)
        db.commit()
        db.refresh(db_address)  
        logger.info("Created new address with id=%d: %s, %s", db_address.id, db_address.street, db_address.city)
        return db_address
    except Exception as e:
        logger.error("Error creating address: %s", str(e), exc_info=True)
        db.rollback()
        raise




def get_address(db: Session, address_id: int) -> Optional[models.Address]:
    """
    Retrieve a single address by its primary key.

    Args:
        db         : Active SQLAlchemy database session.
        address_id : Primary key of the address to retrieve.

    Returns:
        The Address ORM instance, or None if not found.
    """
    try:
        logger.debug("Fetching address with id=%d", address_id)
        return db.query(models.Address).filter(models.Address.id == address_id).first()
    except Exception as e:
        logger.error("Error fetching address id=%d: %s", address_id, str(e), exc_info=True)
        raise




def get_addresses(db: Session, skip: int = 0, limit: int = 100) -> List[models.Address]:
    """
    Retrieve a paginated list of all addresses.

    Args:
        db    : Active SQLAlchemy database session.
        skip  : Number of records to skip (for pagination offset).
        limit : Maximum number of records to return (page size).

    Returns:
        A list of Address ORM instances.
    """
    try:
        logger.debug("Fetching addresses — skip=%d, limit=%d", skip, limit)
        return db.query(models.Address).offset(skip).limit(limit).all()
    except Exception as e:
        logger.error("Error fetching addresses: %s", str(e), exc_info=True)
        raise


def get_addresses_within_distance(
    db: Session,
    latitude: float,
    longitude: float,
    distance_km: float,
) -> List[models.Address]:
    """
    Retrieve all addresses within a given radius from a center point.

    Strategy:
        1. Fetch all addresses from the database.
        2. Filter in Python using the Haversine formula.

    Note:
        For large datasets, consider a spatial extension (e.g., SpatiaLite) or
        a bounding-box pre-filter to reduce the number of in-memory calculations.

    Args:
        db          : Active SQLAlchemy database session.
        latitude    : Center point latitude in decimal degrees.
        longitude   : Center point longitude in decimal degrees.
        distance_km : Search radius in kilometers.

    Returns:
        A list of Address ORM instances within the specified distance.
    """
    try:
        logger.debug(
            "Searching addresses within %.2f km of (%.4f, %.4f)",
            distance_km, latitude, longitude,
        )
        all_addresses = db.query(models.Address).all()

        nearby = [
            addr for addr in all_addresses
            if haversine_distance(latitude, longitude, addr.latitude, addr.longitude) <= distance_km
        ]

        logger.info(
            "Found %d address(es) within %.2f km of (%.4f, %.4f)",
            len(nearby), distance_km, latitude, longitude,
        )
        return nearby
    except Exception as e:
        logger.error("Error fetching nearby addresses: %s", str(e), exc_info=True)
        raise




def update_address(
    db: Session,
    db_address: models.Address,
    address_in: schemas.AddressUpdate,
) -> models.Address:
    """
    Apply partial or full updates to an existing address record.

    Only the fields explicitly provided in `address_in` (non-None values) are
    updated, preserving existing values for omitted fields.

    Args:
        db         : Active SQLAlchemy database session.
        db_address : The existing ORM instance to update.
        address_in : Validated Pydantic schema with the new field values.

    Returns:
        The updated Address ORM instance.
    """
    try:
       
        update_data = address_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_address, field, value)

        db.commit()
        db.refresh(db_address)
        logger.info("Updated address id=%d with fields: %s", db_address.id, list(update_data.keys()))
        return db_address
    except Exception as e:
        logger.error("Error updating address id=%d: %s", db_address.id, str(e), exc_info=True)
        db.rollback()
        raise




def delete_address(db: Session, db_address: models.Address) -> None:
    """
    Delete an address record from the database.

    Args:
        db         : Active SQLAlchemy database session.
        db_address : The ORM instance to delete.
    """
    try:
        logger.info("Deleting address id=%d (%s, %s)", db_address.id, db_address.street, db_address.city)
        db.delete(db_address)
        db.commit()
    except Exception as e:
        logger.error("Error deleting address id=%d: %s", db_address.id, str(e), exc_info=True)
        db.rollback()
        raise
