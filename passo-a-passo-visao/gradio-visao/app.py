import mimetypes
import os

import gradio as gr
import requests


# ------------------------------------------------------------
# Configurações
# ------------------------------------------------------------

ANALISE_URL = os.getenv(
    "ANALISE_URL",
    "http://analise-service:8081"
)

SERVER_PORT = int(
    os.getenv("VISAO_PORT", "7861")
)


# ------------------------------------------------------------
# Categorias
# ------------------------------------------------------------

categorias = [
    "Viagem",
    "Pessoas",
    "Natureza",
    "Comida",
    "Animais",
    "Objetos",
    "Documento",
    "Outro"
]


# ------------------------------------------------------------
# Função responsável por enviar a imagem para a API
# ------------------------------------------------------------

def analisa_imagem(imagem_path, categoria):

    if imagem_path is None:
        return "Nenhuma imagem enviada.", ""

    nome = os.path.basename(imagem_path)

    tipo_mime, _ = mimetypes.guess_type(imagem_path)

    if tipo_mime is None:
        tipo_mime = "application/octet-stream"

    try:

        with open(imagem_path, "rb") as f:

            files = {
                "file": (
                    nome,
                    f,
                    tipo_mime
                )
            }

            r = requests.post(
                f"{ANALISE_URL}/analisar",
                files=files,
                data={
                    "categoria": categoria
                },
                timeout=600
            )

    except requests.RequestException as e:

        return (
            "Erro de conexão com o serviço de IA:\n"
            f"{e}",
            ""
        )

    except Exception as e:

        return (
            "Erro ao abrir a imagem:\n"
            f"{e}",
            ""
        )

    # --------------------------------------------------------
    # Verifica resposta da API
    # --------------------------------------------------------

    if r.status_code != 200:

        try:
            detalhe = r.json().get(
                "detail",
                "Erro desconhecido"
            )
        except Exception:
            detalhe = r.text

        return (
            f"Erro no servidor: {r.status_code}\n"
            f"Detalhes: {detalhe}",
            ""
        )

    # --------------------------------------------------------
    # Processa resposta
    # --------------------------------------------------------

    try:
        dados = r.json()

    except Exception:
        return (
            "Erro: resposta inválida recebida da API.",
            ""
        )

    titulo = dados.get(
        "titulo",
        "Análise de imagem"
    )

    descricao = dados.get(
        "descricao",
        "Descrição não encontrada."
    )

    status_db = dados.get(
        "status_db",
        "Status do armazenamento não informado."
    )

    # --------------------------------------------------------
    # Resultado apresentado ao usuário
    # --------------------------------------------------------

    resultado = (
        f"{titulo}\n\n"
        "DESCRIÇÃO GERADA PELA IA\n\n"
        f"{descricao}\n\n"
        "CATEGORIA DA IMAGEM\n\n"
        f"{categoria}\n\n"
        "STATUS DO ARMAZENAMENTO\n\n"
        f"{status_db}"
    )

    # Retorna também a descrição separadamente,
    # para ser utilizada pela função de verificação.
    return resultado, descricao


# ------------------------------------------------------------
# Função para verificar se um texto está na descrição
# ------------------------------------------------------------

def verificar_texto(texto, descricao):

    if not descricao:
        return "⚠️ Primeiro analise uma imagem."

    if not texto or not texto.strip():
        return "⚠️ Digite uma informação para verificar."

    texto = texto.lower().strip()
    descricao = descricao.lower()

    if texto in descricao:
        return "✅ Informação encontrada na descrição."

    return "❌ Informação não encontrada na descrição."


# ------------------------------------------------------------
# Interface Gradio
# ------------------------------------------------------------

with gr.Blocks() as demo:

    gr.Markdown("# Descrição Inteligente de Imagens com IA")

    gr.Markdown(
        "Envie uma imagem e utilize inteligência artificial para analisar "
        "seu conteúdo, gerar uma descrição automática e registrar a imagem "
        "no sistema de armazenamento."
    )

    # Guarda a descrição gerada pela IA
    descricao_gerada = gr.State("")

    imagem = gr.Image(
        type="filepath",
        label="Imagem para análise"
    )

    categoria = gr.Dropdown(
        choices=categorias,
        value="Outro",
        label="Categoria da imagem"
    )

    botao_analisar = gr.Button(
        "Analisar imagem"
    )

    resultado = gr.Textbox(
        label="Resultado da análise da imagem:",
        lines=8
    )

    botao_analisar.click(
        fn=analisa_imagem,
        inputs=[
            imagem,
            categoria
        ],
        outputs=[
            resultado,
            descricao_gerada
        ]
    )

    gr.Markdown("## Verificar quais palavras contém na descrição da imagem gerada por IA")

    texto_verificacao = gr.Textbox(
        label="Digite uma palavra ou uma sequênncia de palavras para verificação",
        placeholder="Ex.: dog"
    )

    botao_verificar = gr.Button(
        "Verificar"
    )

    resultado_verificacao = gr.Textbox(
        label="Resultado da verificação"
    )

    botao_verificar.click(
        fn=verificar_texto,
        inputs=[
            texto_verificacao,
            descricao_gerada
        ],
        outputs=resultado_verificacao
    )


# ------------------------------------------------------------
# Inicialização
# ------------------------------------------------------------

if __name__ == "__main__":

    demo.launch(
        server_name="0.0.0.0",
        server_port=SERVER_PORT
    )