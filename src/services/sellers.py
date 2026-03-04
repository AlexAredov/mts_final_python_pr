from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.sellers import Seller
from src.schemas.users import IncomingSeller, UpdateSeller


class SellerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_seller(self, seller: IncomingSeller) -> Seller:
        new_seller = Seller(
            first_name=seller.first_name,
            last_name=seller.last_name,
            e_mail=seller.e_mail,
            password=seller.password,
        )
        self.session.add(new_seller)
        await self.session.flush()
        return new_seller

    async def get_all_sellers(self) -> list[Seller]:
        result = await self.session.execute(select(Seller))
        return result.scalars().all()

    async def get_by_email_and_password(self, e_mail: str, password: str) -> Seller | None:
        query = select(Seller).where(Seller.e_mail == e_mail, Seller.password == password)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_single_seller(self, seller_id: int) -> Seller | None:
        query = select(Seller).options(selectinload(Seller.books)).where(Seller.id == seller_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_seller(self, seller_id: int, new_seller_data: UpdateSeller) -> Seller | None:
        if seller := await self.session.get(Seller, seller_id):
            seller.first_name = new_seller_data.first_name
            seller.last_name = new_seller_data.last_name
            seller.e_mail = new_seller_data.e_mail
            await self.session.flush()
            return seller

    async def delete_seller(self, seller_id: int) -> bool:
        seller = await self.session.get(Seller, seller_id)
        if not seller:
            return False
        await self.session.delete(seller)
        return True
