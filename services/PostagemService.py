import json
import os
from datetime import datetime

from bson import ObjectId

from models.UsuarioModel import UsuarioCriarModel, UsuarioAtualizarModel
from providers.AWSProvider import AWSProvider
from repositories.PostagemRepository import PostagemRepository

awsProvider = AWSProvider()
postagemRepository = PostagemRepository()

class PostagemService:
    async def cadastrar_postagem(self, postagem, usuario_id):
        try:
            postagem_criada = await postagemRepository.criar_postagem(postagem, usuario_id)

            try:
                caminho_foto = f'files/foto-{datetime.now().strftime("%H%M%S")}.png'

                with open(caminho_foto, 'wb+') as arquivo:
                    arquivo.write(postagem.foto.file.read())
                url_foto = awsProvider.upload_arquivo_s3(
                    f'fotos-postagem/{postagem_criada["id"]}.png',
                    caminho_foto
                )

                nova_postagem = await postagemRepository.atualizar_postagem(postagem_criada["id"], {"foto": url_foto})

                os.remove(caminho_foto)

            except Exception as erro:
                print(erro)

            return {
                "mensagem": "Postagem criado com sucesso",
                "dados": nova_postagem,
                "status": 201
            }

        except Exception as error:
            return {
                "mensagem": "Erro interno no servidor",
                "dados": str(error),
                "status": 500
            }


    async def listar_postagens(self):
        try:
            postagens = await postagemRepository.listar_postagens()

            for p in postagens:
                p["total_curtidas"] = len(p["curtidas"])

            return {
                "mensagem": "Postagens listadas com sucesso",
                "dados": postagens,
                "status": 200
            }
        except Exception as erro:
            print(erro)
            return {
                "mensagem": "Erro interno no servidor",
                "dados": str(erro),
                "status": 500
            }


    async def listar_postagens_usuario(self, usuario_id):
        try:
            postagens = await postagemRepository.listar_postagens_usuario(usuario_id)

            for p in postagens:
                p["total_curtidas"] = len(p["curtidas"])
                p["total_comentarios"] = len(p["comentarios"])

            return {
                "mensagem": "Postagens listadas com sucesso",
                "dados": postagens,
                "status": 200
            }
        except Exception as erro:
            print(erro)
            return {
                "mensagem": "Erro interno no servidor",
                "dados": str(erro),
                "status": 500
            }



    async def curtir_descurtir(self, postagem_id, usuario_id):
        try:
            postagem_encontrada = await postagemRepository.buscar_postagem(postagem_id)

            if postagem_encontrada["curtidas"].count(usuario_id) > 0:
                postagem_encontrada["curtidas"].remove(usuario_id)
            else:
                postagem_encontrada["curtidas"].append(ObjectId(usuario_id))

            postagem_atualizada = await postagemRepository.atualizar_postagem(
                postagem_encontrada["id"],
                {"curtidas": postagem_encontrada["curtidas"]}
            )


            return {
                "mensagem": "Postagem curtida com sucesso",
                "dados": postagem_atualizada,
                "status": 200
            }

        except Exception as error:
            return {
                "mensagem": "Erro interno no servidor",
                "dados": str(error),
                "status": 500
            }


    async def criar_comentario(self, postagem_id, usuario_id, comentario):
        try:
            postagem_encontrada = await postagemRepository.buscar_postagem(postagem_id)

            postagem_encontrada["comentarios"].append({
                "comentario_id": ObjectId(),
                "usuario_id": ObjectId(usuario_id),
                "comentario:": comentario
            })

            postagem_atualizada = await postagemRepository.atualizar_postagem(
                postagem_encontrada["id"],
                {"comentarios": postagem_encontrada["comentarios"]}
            )


            return {
                "mensagem": "Comentario criado com sucesso",
                "dados": postagem_atualizada,
                "status": 200
            }

        except Exception as error:
            return {
                "mensagem": "Erro interno no servidor",
                "dados": str(error),
                "status": 500
            }


    async def deletar_comentario(self, postagem_id, usuario_id, comentario_id):
        try:
            postagem_encontrada = await postagemRepository.buscar_postagem(postagem_id)

            for comentario in postagem_encontrada["comentarios"]:
                if comentario["comentario_id"] == comentario_id:
                    if not (comentario["usuario_id"] == usuario_id or postagem_encontrada['usuario_id'] == usuario_id):
                        return {
                                "mensagem": "Requisição inválida",
                                "dados": "",
                                "status": 401
                        }

                    postagem_encontrada["comentarios"].remove(comentario)

            postagem_atualizada = await postagemRepository.atualizar_postagem(postagem_encontrada["id"], {"comentarios": postagem_encontrada["comentarios"]})


            return {
                "mensagem": "Comentario deletado com sucesso",
                "dados": postagem_atualizada,
                "status": 200
            }

        except Exception as error:
            return {
                "mensagem": "Erro interno no servidor",
                "dados": str(error),
                "status": 500
            }

    async def atualizar_comentario(self, postagem_id, usuario_id, comentario_id, comentario_atualizado):
        try:
            postagem_encontrada = await postagemRepository.buscar_postagem(postagem_id)

            for comentario in postagem_encontrada["comentarios"]:
                if comentario["comentario_id"] == comentario_id:
                    if not comentario["usuario_id"] == usuario_id:
                        return {
                            "mensagem": "Requisição inválida",
                            "dados": "",
                            "status": 401
                        }

                    comentario["comentario"] = comentario_atualizado

            postagem_atualizada = await postagemRepository.atualizar_postagem(postagem_encontrada["id"],
                                                                              {"comentarios": postagem_encontrada["comentarios"]})

            return {
                "mensagem": "Comentario atualizado com sucesso",
                "dados": postagem_atualizada,
                "status": 200
            }

        except Exception as error:
            return {
                "mensagem": "Erro interno no servidor",
                "dados": str(error),
                "status": 500
            }

    async def deletar_postagem(self, postagem_id, usuario_id):
        try:
            postagem_encontrada = await postagemRepository.buscar_postagem(postagem_id)

            if not postagem_encontrada:
                return {
                    "mensagem": "Postagem não encontrada",
                    "dados": "",
                    "status": 404
                }

            if not postagem_encontrada["usuario_id"] == usuario_id:
                return {
                    "mensagem": "Não é possível realizar essa requisição",
                    "dados": "",
                    "status": 401
                }

            await postagemRepository.deletar_postagem(postagem_id)

            return {
                "mensagem": "Postagem deletada com sucesso!",
                "dados": "",
                "status": 200
            }

        except Exception as error:
            return {
                "mensagem": "Erro interno no servidor",
                "dados": str(error),
                "status": 500
            }
