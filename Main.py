from fastapi import FastAPI
from routes.UsuarioRoute import router as UsuarioRoute
from pydantic import BaseModel

app = FastAPI()

app.include_router(UsuarioRoute, tags=["Usuário"], prefix="/api/usuario")

@app.get("/api/health", tags=["Health"])
async def health():
    return {
        "status": "OK!"
    }