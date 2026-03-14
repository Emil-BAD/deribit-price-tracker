from fastapi import FastAPI

from app.api.routes import router as price_router

app = FastAPI(title="Deribit Price Tracker")
app.include_router(price_router)
