from tronpy import Tron
from tronpy.providers import HTTPProvider
from app.models import AddressRequest
from app.schemas import AddressInfo
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

class TronService:
    def __init__(self):
        network = settings.TRON_NETWORK
        if network == "mainnet":
            self.client = Tron(HTTPProvider("https://api.trongrid.io"))
        else:
            self.client = Tron(HTTPProvider("https://api.shasta.trongrid.io"))

    async def get_address_info(self, address: str) -> AddressInfo:
        try:
            account = self.client.get_account(address)
            bandwidth = account.get("free_net_limit", 0)
            energy = account.get("energy_limit", 0)
            trx_balance = self.client.from_sun(account.get("balance", 0))
            
            return AddressInfo(
                address=address,
                bandwidth=bandwidth,
                energy=energy,
                trx_balance=trx_balance
            )
        except Exception:
            return AddressInfo(address=address)

class DatabaseService:
    def __init__(self, tron_service: TronService):
        self.tron_service = tron_service

    async def create_address_request(self, db: AsyncSession, address: str):
        try:
            address_info = await self.tron_service.get_address_info(address)
            if address_info.bandwidth is None:
                raise ValueError("Invalid address")

            db_request = AddressRequest(
            address=address_info.address,
            bandwidth=address_info.bandwidth,
            energy=address_info.energy,
            trx_balance=address_info.trx_balance
            )
            db.add(db_request)
            await db.commit()
            await db.refresh(db_request)
            return db_request
        except Exception as e:
            await db.rollback()
            raise

    async def get_address_requests(
    self, db: AsyncSession, skip: int = 0, limit: int = 10
    ) -> list[AddressRequest]:
        result = await db.execute(
        select(AddressRequest)
        .order_by(AddressRequest.created_at.desc())
        .offset(skip)
        .limit(limit)
        )
        return result.scalars().all()

    async def get_total_requests(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count(AddressRequest.id)))
        return result.scalar()