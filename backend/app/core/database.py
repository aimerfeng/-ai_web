from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLite Configuration for concurrent access
# check_same_thread=False is needed for SQLite in async context
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

async def init_db():
    """Initialize database and enable WAL mode for SQLite."""
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            
            # Enable WAL mode
            await conn.execute(sqlalchemy.text("PRAGMA journal_mode=WAL"))
            await conn.execute(sqlalchemy.text("PRAGMA synchronous=NORMAL"))
            await conn.execute(sqlalchemy.text("PRAGMA busy_timeout=5000"))
            logger.info("Database initialized and WAL mode enabled.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

# Fix import for text
import sqlalchemy
