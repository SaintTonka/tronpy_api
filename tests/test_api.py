import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services import TronService, DatabaseService
from unittest.mock import AsyncMock
from app.models import AddressRequest
from app.schemas import AddressInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

@pytest.mark.anyio
async def test_create_address_request(session: AsyncSession):
    mock_tron_service = AsyncMock(spec=TronService)

    mock_tron_service.get_address_info.return_value = AddressInfo(
        address="TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj",
        bandwidth=5000,
        energy=10000,
        trx_balance=150.5
    )

    db_service = DatabaseService(tron_service=mock_tron_service)

    address = "TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj"
    request = await db_service.create_address_request(session, address)
    
    assert request.address == address
    assert request.bandwidth == 5000
    assert request.energy == 10000
    assert request.trx_balance == 150.5

    mock_tron_service.get_address_info.assert_called_once_with(address)

@pytest.mark.anyio
async def test_create_address_request_invalid(session: AsyncSession):
    mock_tron_service = AsyncMock(spec=TronService)
    mock_tron_service.get_address_info.return_value = AddressInfo(
        address="invalid_address",
        bandwidth=None,
        energy=None,
        trx_balance=None
    )
    
    db_service = DatabaseService(tron_service=mock_tron_service)

    with pytest.raises(ValueError, match="Invalid address"):
        await db_service.create_address_request(session, "invalid_address")

@pytest.mark.anyio
async def test_get_address_requests(client, session: AsyncSession, clean_db):
    test_addresses = [f"TEST_ADDR_{i}" for i in range(5)]
    test_data = [AddressRequest(address=addr) for addr in test_addresses]
    session.add_all(test_data)
    await session.commit()
    try:
        db_service = DatabaseService(tron_service=TronService())
        requests = await db_service.get_address_requests(session, skip=0, limit=2)
        total = await db_service.get_total_requests(session)
        assert len(requests) == 2
        assert total == 5
        returned_addresses = {req.address for req in requests}
        assert all(addr in test_addresses for addr in returned_addresses)
        assert len(returned_addresses) == 2        
    finally:
        await session.execute(delete(AddressRequest))
        await session.commit()