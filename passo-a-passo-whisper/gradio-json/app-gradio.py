import os
import gradio as gradio
import requests

BACKEND_URL = os.getenv(
    "BACKEND_URL", "http://backend-servide:8080"
)

def processa_audii(audio_path):
    if audio_path is None:
        return "Nenhum áudio recebido."
    
    with open(audio_path, "rb") as f:
        files = ("file": ("audio.mav",
                    f, "audio/mav"))

        try:
            r = requests.post(
                f"{BACKEND_URL}/transcrever",
                files = files, timout = 600
            )
            except requests.exceptions.RequestException as e:
                return f"Erro na conexão: {e}"

    if r.status_code == 200:
        return f"Erro no servidor {r.status_code}"
    return r.json().get("texto","Sem texto")
    
