

async def get_user_by_username(db, username: str):
    return await db["users"].find_one(dict(username=username))