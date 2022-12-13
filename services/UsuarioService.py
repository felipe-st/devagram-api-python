import os
from datetime import datetime

from bson import ObjectId

from models.UsuarioModel import UsuarioCriarModel, UsuarioAtualizarModel
from providers.AWSProvider import AWSProvider
from repositories.UsuarioRepository import UsuarioRepository
from repositories.PostagemRepository import PostagemRepository

awsProvider = AWSProvider()
usuarioRepository = UsuarioRepository()
postagemRepository = PostagemRepository()

class UsuarioService:
    async def registrar_usuario(self, usuario: UsuarioCriarModel, caminho_foto):
        try:
            usuario_encontrado = await usuarioRepository.buscar_usuario_por_email(usuario.email)

            if usuario_encontrado:
                return {
                    "mensagem": f'E-mail {usuario.email} já cadastrado no sistema',
                    "dados": "",
                    "status": 400
                }
            else:
                novo_usuario = await usuarioRepository.criar_usuario(usuario)

                url_foto = awsProvider.upload_arquivo_s3(
                    f'fotos-perfil/{novo_usuario["id"]}.png',
                    caminho_foto
                )

                novo_usuario = await usuarioRepository.atualizar_usuario(novo_usuario["id"], {"foto": url_foto})

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


    async def buscar_usuario(self, id: str):
        try:
            usuario_encontrado = await usuarioRepository.buscar_usuario(id)

            if usuario_encontrado:
                postagens_encontradas = await postagemRepository.listar_postagens_usuario(id)

                usuario_encontrado["total_seguidores"] = len(usuario_encontrado["seguidores"])
                usuario_encontrado["total_seguindo"] = len(usuario_encontrado["seguindo"])
                usuario_encontrado["postagens"] = postagens_encontradas
                usuario_encontrado["total_postagens"] = len(postagens_encontradas)

     #       if usuario_encontrado:
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


    async def listar_usuarios(self, nome):
        try:
            usuario_encontrado = await usuarioRepository.listar_usuarios(nome)

            for usuario in usuario_encontrado:
                usuario["total_seguindo"] = len(usuario["seguindo"])
                usuario["total_seguidores"] = len(usuario["seguidores"])

            return {
                "mensagem": "Usuários listados com sucesso",
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



    async def atualizar_usuario_logado(self, id, usuario_atualizar: UsuarioAtualizarModel):
        try:
            usuario_encontrado = await usuarioRepository.buscar_usuario(id)

            if usuario_encontrado:
                usuario_dict = usuario_atualizar.__dict__

                try:
                    caminho_foto = f'files/foto-{datetime.now().strftime("%H%M%S")}.jpg'

                    with open(caminho_foto, 'wb+') as arquivo:
                        arquivo.write(usuario_atualizar.foto.file.read())
                    url_foto = awsProvider.upload_arquivo_s3(
                        f'fotos-perfil/{id}.png',
                        caminho_foto
                    )
                    os.remove(caminho_foto)

                except Exception as erro:
                    print(erro)
                usuario_dict['foto'] = url_foto if url_foto is not None else usuario_dict['foto']
                usuario_atualizado = await usuarioRepository.atualizar_usuario(id, usuario_dict)

                return {
                    "mensagem": f'Usuario atualizado',
                    "dados": usuario_atualizado,
                    "status": 200
                }
            else:
                return {
                    "mensagem": f"Usuário com o id {id} não foi encontrado.",
                    "dados": "",
                    "status": 404
                }
        except Exception as erro:
            print(erro)

            return {
                "mensagem": "Erro interno no servidor",
                "dados": str(erro),
                "status": 500
            }


    async def follow_unfollow_usuario(self, usuario_logado_id, usuario_seguido_id):
        try:
            usuario_seguido_encontrado = await usuarioRepository.buscar_usuario(usuario_seguido_id)
            usuario_logado_encontrado = await usuarioRepository.buscar_usuario(usuario_logado_id)

            if usuario_seguido_encontrado["seguidores"].count(usuario_logado_id) > 0:
                usuario_seguido_encontrado["seguidores"].remove(usuario_logado_id)
                usuario_logado_encontrado["seguindo"].remove(usuario_seguido_id)
            else:
                usuario_seguido_encontrado["seguidores"].append(ObjectId(usuario_logado_id))
                usuario_logado_encontrado["seguindo"].append(ObjectId(usuario_seguido_id))

            await usuarioRepository.atualizar_usuario(
                usuario_seguido_encontrado["id"],
                {"seguidores": usuario_seguido_encontrado["seguidores"]})
            await usuarioRepository.atualizar_usuario(usuario_logado_encontrado["id"], {
                "seguindo": usuario_logado_encontrado["seguindo"]})

            return {
                "mensagem": "Requisição realizada com sucesso!",
                "dados": "",
                "status": 200
            }

        except Exception as error:
            return {
                "mensagem": "Erro interno no servidor",
                "dados": str(error),
                "status": 500
            }
