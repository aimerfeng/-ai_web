import asyncio
from app.core.database import init_db, async_session_maker
from app.models.user import User
from app.services.auth_service import AuthService
from sqlalchemy import select

async def create_user(username, password):
    await init_db()
    
    async with async_session_maker() as db:
        # Check if user exists
        result = await db.execute(select(User).where(User.username == username))
        if result.scalar_one_or_none():
            print(f"User '{username}' already exists.")
            return

        hashed_password = AuthService.get_password_hash(password)
        new_user = User(
            username=username,
            password_hash=hashed_password
        )
        
        db.add(new_user)
        await db.commit()
        print(f"User '{username}' created successfully.")

if __name__ == "__main__":
    asyncio.run(create_user("admin", "123456"))
