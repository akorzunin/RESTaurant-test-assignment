from fastapi.encoders import jsonable_encoder
from utils.password import hash_password

### USERS
async def create_user(db, user):
    user = jsonable_encoder(user)
    existed_user = await db.users.find_one(dict(username=user['username']))
    if not existed_user:
        user['hashed_password'] = hash_password(user['hashed_password'])
        new_user = await db["users"].insert_one(user)
        return True, await db["users"].find_one({"_id": new_user.inserted_id})
    return False, existed_user

async def get_user_by_username(db, username: str):
    return await db["users"].find_one(dict(username=username))

async def update_user(db, id, user):
    # filter all empty fields
    if user := {k: v for k, v in user.dict().items() if v is not None}:
        update_result = await db["users"].update_one({"_id": id}, {"$set": user})

    if update_result.modified_count == 1:
        if (
            updated_user := await db["users"].find_one({"_id": id})
        ) is not None:
            return updated_user

    if (existing_user := await db["users"].find_one({"_id": id})) is not None:
        return existing_user

async def delete_user_by_id(db, user_id: str) -> bool:
    if await db["users"].delete_one({"_id": user_id}):
        return True
    return False

### TABLES
async def create_table(db, table):
    table = jsonable_encoder(table)
    existed_table = await db.tables.find_one(dict(table_name=table['table_name']))
    if not existed_table:
        new_table = await db["tables"].insert_one(table)
        return True, await db["tables"].find_one({"_id": new_table.inserted_id})
    return False, existed_table

async def update_table(db, id, table):
    # filter all empty fields
    if table := {k: v for k, v in table.dict().items() if v is not None}:
        update_result = await db["tables"].update_one({"_id": id}, {"$set": table})

    if update_result.modified_count == 1:
        if (
            updated_table := await db["tables"].find_one({"_id": id})
        ) is not None:
            return updated_table

    if (existing_table := await db["tables"].find_one({"_id": id})) is not None:
        return existing_table

async def delete_table_by_id(db, table_id: str) -> bool:
    if await db["tables"].delete_one({"_id": table_id}):
        return True
    return False
