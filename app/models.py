"""
models.py
---------
Defines the SQLAlchemy ORM model for the Address entity.
Each Address record stores human-readable address fields plus
latitude/longitude coordinates.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.database import Base


class Address(Base):
    """
    ORM model representing an address in the SQLite database.

    Attributes:
        id          : Auto-incremented primary key.
        street      : Street name and number.
        city        : City name.
        state       : State or province.
        country     : Country name.
        postal_code : ZIP / postal code.
        latitude    : Geographic latitude (-90 to 90 degrees).
        longitude   : Geographic longitude (-180 to 180 degrees).
        created_at  : Timestamp automatically set when the record is created.
        updated_at  : Timestamp automatically updated on every modification.
    """

    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    street = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Audit timestamps — managed automatically by the database server
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<Address(id={self.id}, street='{self.street}', city='{self.city}', "
            f"lat={self.latitude}, lon={self.longitude})>"
        )
