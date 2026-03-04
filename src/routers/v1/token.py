from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.configurations.security import create_access_token
from src.schemas import TokenRequest, TokenResponse
from src.services import SellerService

token_router = APIRouter(prefix="/token", tags=["token"])

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@token_router.post("/", response_model=TokenResponse)
async def create_token(payload: TokenRequest, session: DBSession):
    seller = await SellerService(session).get_by_email_and_password(payload.e_mail, payload.password)
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect e_mail or password",
        )

    token = create_access_token(subject=str(seller.id))
    return {"access_token": token, "token_type": "bearer"}
