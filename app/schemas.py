"""
schemas.py
----------
Pydantic schemas (v2) used for request validation and response serialization.

Schemas:
    AddressBase    : Shared fields for create/update operations.
    AddressCreate  : Used when creating a new address (all required fields).
    AddressUpdate  : Used when partially updating an address (all fields optional).
    AddressResponse: The shape of data returned to API consumers.

Note:
    Query parameters for the /nearby endpoint are declared directly in the
    router using FastAPI's Query() — no separate schema is required for those.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class AddressBase(BaseModel):
    """Shared fields common to create and update operations."""

    street: str = Field(..., min_length=1, max_length=255, description="Street name and number")
    city: str = Field(..., min_length=1, max_length=100, description="City name")
    state: str = Field(..., min_length=1, max_length=100, description="State or province")
    country: str = Field(..., min_length=1, max_length=100, description="Country name")
    postal_code: Optional[str] = Field(None, max_length=20, description="ZIP / Postal code (optional)")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees (-90 to 90)")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees (-180 to 180)")

    @field_validator("street", "city", "state", "country", mode="before")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        """Remove leading/trailing whitespace from string fields."""
        return value.strip()


class AddressCreate(AddressBase):
    """
    Schema for creating a new address.
    All fields from AddressBase are required.

    Example:
        {
            "street": "123 Main St",
            "city": "Amsterdam",
            "state": "North Holland",
            "country": "Netherlands",
            "postal_code": "1011 AB",
            "latitude": 52.3676,
            "longitude": 4.9041
        }
    """
    pass


class AddressUpdate(BaseModel):
    """
    Schema for updating an existing address.
    All fields are optional to support partial (PATCH-style) updates via PUT.
    """

    street: Optional[str] = Field(None, min_length=1, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)

    @field_validator("street", "city", "state", "country", mode="before")
    @classmethod
    def strip_whitespace(cls, value: Optional[str]) -> Optional[str]:
        """Strip whitespace from optional string fields if provided."""
        return value.strip() if value else value

    @model_validator(mode="after")
    def at_least_one_field(self) -> "AddressUpdate":
        """Ensure that at least one field is provided in an update request."""
        provided = {k: v for k, v in self.model_dump().items() if v is not None}
        if not provided:
            raise ValueError("At least one field must be provided for an update.")
        return self


class AddressResponse(AddressBase):
    """
    Schema for the address data returned to API consumers.
    Includes database-generated fields like `id` and timestamps.
    """

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


