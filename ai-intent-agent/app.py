import uvicorn
from fastapi import FastAPI

from src.config.config import AppConfig
from src.api.routers.health_router import router as health_router
from src.api.routers.process_querry_router import router as process_query_router

app = FastAPI(
    title=f"{AppConfig.SERVICE_NAME} Trigger API",
    description="Service that triggers intent processing for hotel booking queries",
    version="1.0.0"
)

app.include_router(health_router)
app.include_router(process_query_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, timeout_keep_alive=1800)