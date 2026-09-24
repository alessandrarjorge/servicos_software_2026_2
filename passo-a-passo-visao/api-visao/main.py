import io
import os
import requests

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from PIL import Image
from transformers import pipeline


MODELO = os.getenv(
    "MODELO_VISAO",
    "Salesforce/blip-image-captioning-base"
)

ARMAZENAMENTO_URL = os.getenv(
    "ARMAZENAMENTO_URL",
    "http://armazenamento-service:8082"
)


app = FastAPI(title="Serviço de Visão")


print(
    f"Carregando modelo de descrição de imagens: ({MODELO})...",
    flush=True
)

gerador_descricao = pipeline(
    "image-to-text",
    model=MODELO
)

print(
    "Modelo de visão carregado!",
    flush=True
)


@app.get("/")
def status():
    return {"status": "ok"}


def contextualizar_descricao(descricao, categoria):

    contextos = {
        "Viagem": "Cena relacionada a viagem ou turismo.",
        "Pessoas": "Cena que envolve pessoas.",
        "Natureza": "Cena relacionada ao ambiente natural.",
        "Comida": "Cena relacionada a alimentos ou refeições.",
        "Animais": "Cena que envolve animais.",
        "Objetos": "Cena com foco em objetos ou itens.",
        "Documento": "Imagem classificada como documento.",
        "Outro": "Descrição geral da imagem."
    }

    contexto = contextos.get(
        categoria,
        "Descrição geral da imagem."
    )

    return (
        f"{contexto} "
        f"Descrição visual: {descricao}"
    )


def gerar_titulo(categoria):

    titulos = {
        "Viagem": "Análise de imagem — Viagem",
        "Pessoas": "Análise de imagem — Pessoas",
        "Natureza": "Análise de imagem — Natureza",
        "Comida": "Análise de imagem — Comida",
        "Animais": "Análise de imagem — Animais",
        "Objetos": "Análise de imagem — Objetos",
        "Documento": "Análise de imagem — Documento",
        "Outro": "Análise de imagem — Geral"
    }

    return titulos.get(
        categoria,
        "Análise de imagem — Geral"
    )


@app.post("/analisar")
async def analisar_imagem(
    file: UploadFile = File(...),
    categoria: str = Form(...)
):

    print(
        f"Categoria recebida: {categoria}",
        flush=True
    )

    conteudo = await file.read()

    if not conteudo:
        raise HTTPException(
            status_code=400,
            detail="Nenhuma imagem foi enviada"
        )

    try:
        imagem = Image.open(
            io.BytesIO(conteudo)
        ).convert("RGB")

    except Exception:
        raise HTTPException(
            status_code=415,
            detail="Imagem inválida"
        )

    try:
        resultados = gerador_descricao(imagem)

        if not resultados:
            raise HTTPException(
                status_code=500,
                detail="O modelo não retornou uma descrição"
            )

        descricao = resultados[0]["generated_text"].strip()

    except HTTPException:
        raise

    except Exception as e:

        print(
            f"Erro ao analisar imagem: {e}",
            flush=True
        )

        raise HTTPException(
            status_code=500,
            detail="Erro ao processar a imagem com o modelo de IA"
        )

    descricao_contextualizada = contextualizar_descricao(
        descricao,
        categoria
    )

    titulo = gerar_titulo(categoria)

    print(
        f"Descrição contextualizada: {descricao_contextualizada}",
        flush=True
    )

    print(
        f"Título gerado: {titulo}",
        flush=True
    )

    files = {
        "file": (
            file.filename,
            conteudo,
            file.content_type or "application/octet-stream"
        )
    }

    data = {
        "rotulo": f"{categoria}: {descricao}"
    }

    try:
        r = requests.post(
            f"{ARMAZENAMENTO_URL}/salvar",
            files=files,
            data=data,
            timeout=60
        )

        if r.status_code == 200:
            status_db = "Salvo com sucesso"
        else:
            status_db = f"Erro ao salvar ({r.status_code})"

    except requests.RequestException as e:

        print(
            f"Falha na comunicação com armazenamento: {e}",
            flush=True
        )

        status_db = (
            "Falha na comunicação com o serviço "
            "de armazenamento"
        )

    return {
        "titulo": titulo,
        "descricao": descricao_contextualizada,
        "status_db": status_db
    }