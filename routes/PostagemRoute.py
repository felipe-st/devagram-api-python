import os
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Header, UploadFile, Body

from middlewares.JWTMiddleware import verificar_token
from models.ComentarioModel import ComentarioCriarModel
from models.PostagemModel import PostagemCriarModel
from services.AuthService import decodificar_token_jwt
from services.UsuarioService import UsuarioService
from services.PostagemService import PostagemService

router = APIRouter()

usuarioService = UsuarioService()
postagemService = PostagemService()


@router.post(
    "/",
    response_description="Rota para criar uma nova postagem.",
    dependencies=[Depends(verificar_token)]
)
async def rota_criar_postagem(Authorization: str = Header(default=''), postagem: PostagemCriarModel = Depends(PostagemCriarModel)):
    try:
        token = Authorization.split(' ')[1]
        payload = decodificar_token_jwt(token)
        resultado_usuario = await usuarioService.buscar_usuario_logado(payload["usuario_id"])
        usuario_logado = resultado_usuario["dados"]

        resultado = await postagemService.cadastrar_postagem(postagem, usuario_logado["id"])

        if not resultado["status"] == 201:
            raise HTTPException(status_code=resultado["status"], detail=resultado.mensagem)

        return resultado

    except Exception as erro:
        raise erro


@router.get(
    '/',
    response_description='Rota para listar as postagens',
    dependencies=[Depends(verificar_token)]
    )
async def listar_postagens():
    try:
        resultado = await postagemService.listar_postagens()

        if not resultado["status"] == 200:
            raise HTTPException(status_code=resultado["status"], detail=resultado["mensagem"])

        return resultado
    except:
        raise HTTPException(status_code=500, detail='Erro interno do servidor.')


@router.put('/curtir/{postagem_id}',
            response_description="Rota para curtir/descurtir uma postagem",
            dependencies=[Depends(verificar_token)]
)
async def curtir_descurtir_postagem(postagem_id: str, Authorization: str = Header(default='')):
    token = Authorization.split(' ')[1]
    payload = decodificar_token_jwt(token)
    resultado_usuario = await usuarioService.buscar_usuario_logado(payload["usuario_id"])
    usuario_logado = resultado_usuario["dados"]

    resultado = await postagemService.curtir_descurtir(postagem_id, usuario_logado["id"])

    if not resultado["status"] == 200:
        raise HTTPException(status_code=resultado["status"], detail=resultado["mensagem"])

    return resultado


@router.put('/comentar/{postagem_id}',
            response_description="Rota para criar um comentario em uma postagem",
            dependencies=[Depends(verificar_token)]
)
async def comentar_postagem(postagem_id: str, Authorization: str = Header(default=''), comentario_model: ComentarioCriarModel = Body(...)):
    token = Authorization.split(' ')[1]
    payload = decodificar_token_jwt(token)
    resultado_usuario = await usuarioService.buscar_usuario_logado(payload["usuario_id"])
    usuario_logado = resultado_usuario["dados"]

    resultado = await postagemService.criar_comentario(postagem_id, usuario_logado["id"], comentario_model.comentario)

    if not resultado["status"] == 200:
        raise HTTPException(status_code=resultado["status"], detail=resultado["mensagem"])

    return resultado