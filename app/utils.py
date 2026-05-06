"""
utils.py
--------
Utility functions for the address book application.

Currently provides:
    - haversine_distance : Calculates the great-circle distance between two
                           geographic coordinates using the Haversine formula.
"""

import math
import logging

logger = logging.getLogger(__name__)

# Earth's mean radius in kilometers (WGS-84 standard)
EARTH_RADIUS_KM = 6371.0


def haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """
    Calculate the great-circle distance between two points on the Earth
    using the Haversine formula.

    The Haversine formula determines the shortest distance over the Earth's
    surface between two points, giving an "as-the-crow-flies" distance between
    the points (ignoring any hills or obstacles).

    Args:
        lat1 (float): Latitude of the first point in decimal degrees.
        lon1 (float): Longitude of the first point in decimal degrees.
        lat2 (float): Latitude of the second point in decimal degrees.
        lon2 (float): Longitude of the second point in decimal degrees.

    Returns:
        float: Distance between the two points in kilometers.

    References:
        https://en.wikipedia.org/wiki/Haversine_formula
    """
    try:
        # Convert decimal degrees to radians
        lat1_r, lon1_r, lat2_r, lon2_r = map(math.radians, [lat1, lon1, lat2, lon2])

        # Differences in coordinates
        delta_lat = lat2_r - lat1_r
        delta_lon = lon2_r - lon1_r

        # Haversine formula
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        distance = EARTH_RADIUS_KM * c

        logger.debug(
            "Haversine distance between (%.4f, %.4f) and (%.4f, %.4f) = %.4f km",
            lat1, lon1, lat2, lon2, distance,
        )
        return distance
    except Exception as e:
        logger.error("Error calculating haversine distance: %s", str(e), exc_info=True)
        raise
