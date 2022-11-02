import os
from datetime import datetime

from fastapi import APIRouter, Body, HTTPException, Depends, Header, UploadFile

from middlewares.JWTMiddleware import verificar_token
from models.UsuarioModel import UsuarioModel, UsuarioCriarModel
from services.AuthService import decodificar_token_jwt
from services.UsuarioService import (
    registrar_usuario,
    buscar_usuario_logado
)

router = APIRouter()

@router.post("/", response_description="Rota para criar um novo usuário.")
async def rota_criar_usuario(file: UploadFile, usuario: UsuarioCriarModel = Depends(UsuarioCriarModel)):
    caminho_foto = f'files/foto-{datetime.now().strftime("%H%M%S")}.jpg'

    with open(caminho_foto, 'wb+') as arquivo:
        arquivo.write(file.file.read())

    resultado = await registrar_usuario(usuario, caminho_foto)

    os.remove(caminho_foto)

    if not resultado['status'] == 201:
        raise HTTPException(status_code=resultado['status'], detail=resultado['mensagem'])

    return resultado

@router.get(
    '/me',
    response_description='Rota para buscar as informações do usuário logado',
    dependencies=[Depends(verificar_token)]
    )
async def buscar_info_usuario_logado(Authorization: str = Header(default='')):
    try:
        token = Authorization.split(' ')[1]

        payload = decodificar_token_jwt(token)

        resultado = await buscar_usuario_logado(payload["usuario_id"])

        if not resultado['status'] == 200:
            raise HTTPException(status_code=resultado['status'], detail=resultado['mensagem'])

        return resultado
    except:
        raise HTTPException(status_code=500, detail='Erro interno do servidor.')