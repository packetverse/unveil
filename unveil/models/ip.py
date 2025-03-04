from typing import Optional
from pydantic.dataclasses import dataclass
from pydantic import Field, model_validator


@dataclass
class IPv4:
    ip: str
    aso: Optional[str] = None
    asn: Optional[int] = None
    continent: Optional[str] = None
    cc: Optional[str] = Field(None, serialization_alias="country_code")
    country: Optional[str] = None
    city: Optional[str] = None
    postal: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = Field(None, serialization_alias="tz")
    loc: Optional[str] = None
    region: Optional[str] = None

    @model_validator(mode="after")
    def parse_location(self):
        try:
            loc = self.loc
            if "," in loc:
                lat, lon = loc.split(",")
                self.latitude = lat
                self.longitude = lon
                del self.loc
            return self
        except Exception:
            # should be logged implement later
            # print(f"Error: {e}")
            pass


@dataclass
class IPv6: ...


# make specific models for the API responses
@dataclass
class GeoJS: ...
