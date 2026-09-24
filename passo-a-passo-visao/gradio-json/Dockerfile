FROM python:3.11-slim

# ARG existe apenas durante o build e não vai para a imagem final;
# ENV persiste e fica disponível para o processo em execução.
ARG GRADIO_SERVER_PORT=7860
ENV GRADIO_SERVER_PORT=${GRADIO_SERVER_PORT}

# Sem isto o Python bufferiza a saída e "docker compose logs" aparece
# vazio ou atrasado — o aluno conclui que o contêiner travou.
ENV PYTHONUNBUFFERED=1

WORKDIR /work

# 1º as dependências — camada estável
COPY requirements.txt /work/requirements.txt
RUN pip install --no-cache-dir -r /work/requirements.txt

# 2º o código — camada volátil
COPY app-gradio.py /work/

EXPOSE 7860

CMD ["python", "/work/app-gradio.py"]
