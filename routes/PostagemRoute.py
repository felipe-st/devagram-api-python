import os
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Header, UploadFile

from middlewares.JWTMiddleware import verificar_token
from models.PostagemModel import PostagemCriarModel

router = APIRouter()

@router.post("/", response_description="Rota para criar uma nova postagem.")
async def rota_criar_postagem(file: UploadFile, usuario: PostagemCriarModel = Depends(PostagemCriarModel)):
    caminho_foto = f'files/foto-{datetime.now().strftime("%H%M%S")}.jpg'

    with open(caminho_foto, 'wb+') as arquivo:
        arquivo.write(file.file.read())

   # resultado = await registrar_usuario(usuario, caminho_foto)

    os.remove(caminho_foto)


@router.get(
    '/',
    response_description='Rota para listar as postagens',
    dependencies=[Depends(verificar_token)]
    )
async def listar_postagens(Authorization: str = Header(default='')):
    try:
        return {
            "teste": "ok"
        }
    except:
        raise HTTPException(status_code=500, detail='Erro interno do servidor.')


@router.get(
    '/me',
    response_description='Rota para listar as postagens do usuario',
    dependencies=[Depends(verificar_token)]
    )
async def buscar_info_usuario_logado(Authorization: str = Header(default='')):
    try:
        return {
            "teste": "ok"
        }
    except:
        raise HTTPException(status_code=500, detail='Erro interno do servidor.')