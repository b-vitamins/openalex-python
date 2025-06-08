"""Geographic information for a location."""
from __future__ import annotations


class Geo:
    """Basic geographic metadata."""

    def __init__(
        self,
        *,
        city: str | None = None,
        geonames_city_id: str | None = None,
        region: str | None = None,
        country_code: str | None = None,
        country: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> None:
        self.city = city
        self.geonames_city_id = geonames_city_id
        self.region = region
        self.country_code = country_code
        self.country = country
        self.latitude = latitude
        self.longitude = longitude
