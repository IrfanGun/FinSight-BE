from fastapi import FastAPI

from app.modules.transactions.adapters import orm as transaction_orm  # noqa: F401
from app.modules.transactions.entrypoints.api import router as transactions_router
from app.modules.users.adapters import orm as user_orm  # noqa: F401
from app.modules.users.entrypoints.api import router as users_router
from app.modules.ai.entrypoints.api import router as ai_router
from app.shared.config import get_settings


settings = get_settings()
app = FastAPI(title=settings.app_name)

app.include_router(users_router)
app.include_router(transactions_router)
app.include_router(ai_router)


@app.get("/")
def healthcheck():
    return {"message": f"{settings.app_name} is running"}
