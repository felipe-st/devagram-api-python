from fastapi import APIRouter, Body, HTTPException, Depends

from middlewares.JWTMiddleware import verificar_token
from models.UsuarioModel import UsuarioModel, UsuarioCriarModel
from services.UsuarioService import (
    registrar_usuario,
    buscar_usuario
)

router = APIRouter()

@router.post("/", response_description="Rota para criar um novo usuário.")
async def rota_criar_usuario(usuario: UsuarioCriarModel = Body(...)):
    resultado = await registrar_usuario(usuario)

    if not resultado['status'] == 201:
        raise HTTPException(status_code=resultado['status'], detail=resultado['mensagem'])

    return resultado

@router.get(
    '/me',
    response_description='Rota para buscar as informações do usuário logado',
    dependencies=[Depends(verificar_token)]
    )
async def buscar_info_usuario_logado():
    try:
        return {
            "mensagem": "teste"
        }

        #usuario = buscar_usuario(id)
    except:
        raise HTTPException(status_code=500, detail='Erro interno do servidor.')