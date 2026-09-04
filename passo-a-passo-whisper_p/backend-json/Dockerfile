FROM python:3.11-slim

WORKDIR /code

# ffmpeg é dependência de SISTEMA (não vem pelo pip): o Whisper o usa
# para decodificar o áudio recebido. Esquecê-lo produz um erro em
# tempo de execução, na primeira transcrição — nunca no build.
# O "rm -rf" precisa estar na MESMA instrução RUN: em outra camada, o
# conteúdo já estaria gravado e a imagem não encolheria.
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# 1º as dependências — camada estável, quase sempre reaproveitada do cache
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 2º o código — camada volátil, a única reconstruída a cada edição
COPY ./app /code/app

EXPOSE 8080

# --host 0.0.0.0 é OBRIGATÓRIO. O padrão do uvicorn é 127.0.0.1, que
# só aceita conexões de dentro do próprio contêiner — nenhum outro
# contêiner conseguiria falar com esta API.
CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8080"]
