import os
from datetime import datetime

from fastapi import APIRouter, Body, HTTPException, Depends, Header, UploadFile

from middlewares.JWTMiddleware import verificar_token
from models.UsuarioModel import UsuarioModel, UsuarioCriarModel, UsuarioAtualizarModel
from services.AuthService import decodificar_token_jwt
from services.UsuarioService import UsuarioService

router = APIRouter()
usuarioService = UsuarioService()

@router.post("/", response_description="Rota para criar um novo usuário.")
async def rota_criar_usuario(file: UploadFile, usuario: UsuarioCriarModel = Depends(UsuarioCriarModel)):
    caminho_foto = f'files/foto-{datetime.now().strftime("%H%M%S")}.jpg'

    with open(caminho_foto, 'wb+') as arquivo:
        arquivo.write(file.file.read())

    resultado = await usuarioService.registrar_usuario(usuario, caminho_foto)

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

        resultado = await usuarioService.buscar_usuario_logado(payload["usuario_id"])

        if not resultado['status'] == 200:
            raise HTTPException(status_code=resultado['status'], detail=resultado['mensagem'])

        return resultado
    except:
        raise HTTPException(status_code=500, detail='Erro interno do servidor.')


@router.put(
    '/me',
    response_description='Rota para atualizar as informações do usuário logado',
    dependencies=[Depends(verificar_token)]
    )
async def atualizar_usuario_logado(Authorization: str = Header(default=''), usuario_atualizar: UsuarioAtualizarModel = Depends(UsuarioAtualizarModel)):
    try:
        token = Authorization.split(' ')[1]

        payload = decodificar_token_jwt(token)

        resultado = await usuarioService.atualizar_usuario_logado(payload["usuario_id"], usuario_atualizar)

        if not resultado['status'] == 200:
            raise HTTPException(status_code=resultado['status'], detail=resultado['mensagem'])

        return resultado
    except:
        raise HTTPException(status_code=500, detail='Erro interno do servidor.')


@router.put('/seguir/{usuario_id}',
            response_description="Rota para follow/unfollow em um usuario",
            dependencies=[Depends(verificar_token)]
)
async def follow_unfollow_uusario(usuario_id: str, Authorization: str = Header(default='')):
    token = Authorization.split(' ')[1]
    payload = decodificar_token_jwt(token)
    resultado_usuario = await usuarioService.buscar_usuario_logado(payload["usuario_id"])
    usuario_logado = resultado_usuario["dados"]

    resultado = await usuarioService.follow_unfollow_usuario(usuario_logado["id"], usuario_id)

    if not resultado["status"] == 200:
        raise HTTPException(status_code=resultado["status"], detail=resultado["mensagem"])

    return resultado
