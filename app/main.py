from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import logging
from app import models, schemas
from app.services import TronService, DatabaseService
from app.database import engine, get_db

def get_tron_service():
    return TronService()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

    logger.info("Выключение")
    engine.dispose()

@app.post("/address-info/", response_model=schemas.AddressRequestResponse)
async def get_address_info(
    address: schemas.AddressRequestCreate,
    db: AsyncSession = Depends(get_db),
    tron_service: TronService = Depends(get_tron_service) 
):
    db_service = DatabaseService(tron_service=tron_service) 
    try:
        return await db_service.create_address_request(db, address.address)
    except Exception as e:
        logger.error(f"Error: {str(e)}") 
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/address-requests/", response_model=schemas.PaginatedResponse)
async def get_address_requests(
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(get_db),
    tron_service: TronService = Depends(get_tron_service)  
):
    if page < 1 or size < 1:
        raise HTTPException(
            status_code=400,
            detail="Номер страницы и размер должны быть положительными числами"
        )
    
    db_service = DatabaseService(tron_service=tron_service)  
    skip = (page - 1) * size
    items = await db_service.get_address_requests(db, skip=skip, limit=size)
    total = await db_service.get_total_requests(db)
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size
    }