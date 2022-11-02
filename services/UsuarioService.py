from models.UsuarioModel import UsuarioCriarModel
from providers.AWSProvider import AWSProvider
from repositories.UsuarioRepository import (
    criar_usuario,
    buscar_usuario_por_email,
    buscar_usuario,
    listar_usuarios,
    atualizar_usuario,
    deletar_usuario
)

awsProvider = AWSProvider()

async def registrar_usuario(usuario: UsuarioCriarModel, caminho_foto):
    try:
        usuario_encontrado = await buscar_usuario_por_email(usuario.email)

        if usuario_encontrado:
            return {
                "mensagem": f'E-mail {usuario.email} já cadastrado no sistema',
                "dados": "",
                "status": 400
            }
        else:
            novo_usuario = await criar_usuario(usuario)

            url_foto = awsProvider.upload_arquivo_s3(
                f'fotos-perfil/{novo_usuario["id"]}.png',
                caminho_foto
            )

            novo_usuario = await atualizar_usuario(novo_usuario["id"], {"foto": url_foto})

            print(novo_usuario)

            return {
                "mensagem": "Usuario cadastrado com sucesso",
                "dados": novo_usuario,
                "status": 201
            }
    except Exception as error:
        return {
            "mensagem": "Erro interno no servidor",
            "dados": str(error),
            "status": 500
        }


async def buscar_usuario_logado(id: str):
    try:
        usuario_encontrado = await buscar_usuario(id)

        if usuario_encontrado:
            return {
                "mensagem": f'Usuario encontrado',
                "dados": usuario_encontrado,
                "status": 200
            }
    except Exception as erro:
        print(erro)
        return {
            "mensagem": "Erro interno no servidor",
            "dados": str(erro),
            "status": 500
        }
