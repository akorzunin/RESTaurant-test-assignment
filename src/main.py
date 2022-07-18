
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from routes.mail import router as mail_router
from routes.admin import router as admin_router
from routes.user import router as user_router
from routes.db_routes import router as db_router
from routes.table import router as table_router

from metadata import tags_metadata
app = FastAPI(
    openapi_tags=tags_metadata,
    # routes=routes,
)
app.include_router(
    router=mail_router,
    prefix="/mail",
    tags=["Mail"],
)
app.include_router(
    router=admin_router,
    prefix="/admin",
    tags=["Admin"],
)
app.include_router(
    router=user_router,
    prefix="/user",
    tags=["User"],
)
app.include_router(
    router=table_router,
    prefix="/table",
    tags=["Table"],
)
app.include_router(
    router=db_router,
    prefix="/db",
    tags=["Db"],
)


@app.get("/")
async def docs_redirect():
    return RedirectResponse(url='/docs')



if __name__ == '__main__':
    import uvicorn
    from config import uvicorn_conf
    uvicorn.run(
        **uvicorn_conf,
    )