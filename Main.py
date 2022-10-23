from fastapi import FastAPI
from routes.UsuarioRoute import router as UsuarioRoute
from routes.AutenticacaoRoute import router as AutenticacaoRoute

app = FastAPI()

app.include_router(UsuarioRoute, tags=["Usuário"], prefix="/api/usuario")
app.include_router(AutenticacaoRoute, tags=["Autenticacao"], prefix="/api/auth")

@app.get("/api/health", tags=["Health"])
async def health():
    return {
        "status": "OK!"
    }