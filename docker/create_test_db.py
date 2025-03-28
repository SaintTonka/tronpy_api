import asyncpg
import asyncio
import os
import sys

async def create_test_db():
    conn = None
    try:
        conn = await asyncpg.connect(
            user="postgres",
            password=os.getenv("POSTGRES_PASSWORD"),
            host="db",
            port=5432,
            database="postgres"
        )

        db_exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = 'test_db'"
        )
        
        if not db_exists:
            await conn.execute("CREATE DATABASE test_db")
            print("Test database created successfully")
        else:
            print("Test database already exists")
            
    except Exception as e:
        print(f"Error creating test database: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(create_test_db())