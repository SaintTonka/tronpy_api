import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services import DatabaseService
from app.models import AddressRequest
from app.schemas import AddressInfo
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock
from sqlalchemy import select, delete

@pytest.mark.anyio
async def test_create_address_request(session: AsyncSession):
    mock_tron_service = AsyncMock()
    db_service = DatabaseService(tron_service=mock_tron_service)

    mock_tron_service.get_address_info.return_value = AddressInfo(
        address="TEST_ADDRESS",
        bandwidth=500,
        energy=1000,
        trx_balance=10.5
    )

    created_request = await db_service.create_address_request(session, "TEST_ADDRESS")

    assert created_request.address == "TEST_ADDRESS"
    assert created_request.bandwidth == 500
    assert created_request.energy == 1000
    assert created_request.trx_balance == 10.5

    result = await session.execute(select(AddressRequest).filter_by(address="TEST_ADDRESS"))
    db_record = result.scalars().first()
    assert db_record is not None
    assert db_record.address == "TEST_ADDRESS"

    mock_tron_service.get_address_info.return_value = AddressInfo(
        address="INVALID_ADDRESS",
        bandwidth=None,  
        energy=None,
        trx_balance=None
    )

    with pytest.raises(ValueError, match="Invalid address"):
        await db_service.create_address_request(session, "INVALID_ADDRESS")

    result = await session.execute(select(AddressRequest).filter_by(address="INVALID_ADDRESS"))
    db_record = result.scalars().first()
    assert db_record is None

@pytest.mark.anyio
async def test_get_address_requests(session: AsyncSession, clean_db):
    mock_tron_service = AsyncMock()
    db_service = DatabaseService(tron_service=mock_tron_service)
    try:
        for i in range(5):
            session.add(AddressRequest(address=f"TEST_ADDR_{i}"))
        await session.commit()  
        requests = await db_service.get_address_requests(session, skip=1, limit=2)
        assert len(requests) == 2       
        total = await db_service.get_total_requests(session)
        assert total == 5 
    finally:
        await session.execute(delete(AddressRequest))
        await session.commit()  