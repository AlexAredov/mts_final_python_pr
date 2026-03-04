from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.schemas import (
    IncomingSeller,
    ReturnedAllSellers,
    ReturnedSeller,
    ReturnedSellerWithBooks,
    UpdateSeller,
)
from src.services import SellerService

sellers_router = APIRouter(prefix="/seller", tags=["seller"])

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(seller: IncomingSeller, session: DBSession):
    try:
        created_seller = await SellerService(session).add_seller(seller)
        return created_seller
    except IntegrityError:
        await session.rollback()
        return ORJSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Seller with this e_mail already exists"},
        )


@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    sellers = await SellerService(session).get_all_sellers()
    return {"sellers": sellers}


@sellers_router.get("/{seller_id}", response_model=ReturnedSellerWithBooks)
async def get_single_seller(seller_id: int, session: DBSession):
    seller = await SellerService(session).get_single_seller(seller_id)
    if not seller:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return seller


@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, updated_seller: UpdateSeller, session: DBSession):
    try:
        seller = await SellerService(session).update_seller(seller_id, updated_seller)
    except IntegrityError:
        await session.rollback()
        return ORJSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "Seller with this e_mail already exists"},
        )
    if not seller:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return seller


@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    is_deleted = await SellerService(session).delete_seller(seller_id)
    if not is_deleted:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
