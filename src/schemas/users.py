from pydantic import BaseModel

from .books import ReturnedBook

__all__ = [
    "IncomingSeller",
    "UpdateSeller",
    "ReturnedSeller",
    "ReturnedAllSellers",
    "ReturnedSellerWithBooks",
    "TokenRequest",
    "TokenResponse",
]


class SellerBase(BaseModel):
    first_name: str
    last_name: str
    e_mail: str


class IncomingSeller(SellerBase):
    password: str


class UpdateSeller(SellerBase):
    pass


class ReturnedSeller(SellerBase):
    id: int


class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]


class ReturnedSellerWithBooks(ReturnedSeller):
    books: list[ReturnedBook]


class TokenRequest(BaseModel):
    e_mail: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
