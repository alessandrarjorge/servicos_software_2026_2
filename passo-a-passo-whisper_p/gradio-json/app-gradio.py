"""Front-end do laboratório — interface Gradio.

"""

import os

import gradio as gr
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-service:8080")
TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "600"))


def processa_audio(audio_path):
    if audio_path is None:
        return "Nenhum áudio recebido."

    with open(audio_path, "rb") as f:
        # A chave "file" tem de ser idêntica ao nome do parâmetro
        # UploadFile no back-end. É um contrato entre os dois serviços.
        files = {"file": ("audio.wav", f, "audio/wav")}
        try:
            resposta = requests.post(
                f"{BACKEND_URL}/transcrever",
                files=files,            # plural — este é o parâmetro correto
                timeout=TIMEOUT,
            )
        except requests.exceptions.RequestException as exc:
            return f"Erro de conexão com o back-end ({BACKEND_URL}): {exc}"

    if resposta.status_code != 200:
        return f"Erro no servidor: {resposta.status_code} — {resposta.text[:200]}"

    return resposta.json().get("texto", "Não foi possível extrair o texto.")


demo = gr.Interface(
    fn=processa_audio,
    inputs=gr.Audio(type="filepath", label="Grave sua voz ou envie um áudio"),
    outputs=gr.Textbox(label="Texto transcrito", lines=6),
    title="Assistente de voz com IA",
    description=(
        "Grave seu áudio. O Gradio envia o arquivo ao back-end via API HTTP, "
        "que o converte em texto usando o modelo Whisper. Os dois serviços "
        "rodam em contêineres separados e se encontram pelo nome na rede."
    ),
    flagging_mode="never",
)

if __name__ == "__main__":
    # server_name="0.0.0.0" é obrigatório pelo mesmo motivo do uvicorn:
    # sem isso o Gradio escuta apenas no loopback interno e a porta
    # publicada no host devolve página em branco.
    demo.launch(server_name="0.0.0.0", server_port=7860)
