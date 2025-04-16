import pydantic
import datetime as dt


class Address(pydantic.BaseModel):
    """
    Address data
    """
    region: str
    street: str
    zip: str


class Subject(pydantic.BaseModel):
    """
    Subject data
    """
    id: str
    name: str
    address: Address
    currency: str
    created: dt.date
    updated: dt.date
    active: bool = True
    extra: str | None = None
