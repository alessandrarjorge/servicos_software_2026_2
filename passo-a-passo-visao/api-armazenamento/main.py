import os, sqlite3
from datetime import datetime, timezone
from fastapi import FastAPI, File, Form, UploadFile
DIRETORIO_DADOS = os.getenv("DIRETORIO_DADOS", "/dados")
DB_PATH = os.path.join(DIRETORIO_DADOS, "banco.db")
os.makedirs(DIRETORIO_DADOS, exist_ok=True)

app = FastAPI(title = "Servico de Armazenamento")

import os, sqlite3
from datetime import datetime, timezone
from fastapi import FastAPI, File, Form, UploadFile
 
# /dados e o ponto de montagem do volume nomeado
DIRETORIO_DADOS = os.getenv("DIRETORIO_DADOS", "/dados")
DB_PATH = os.path.join(DIRETORIO_DADOS, "banco.db")
os.makedirs(DIRETORIO_DADOS, exist_ok=True)
 
app = FastAPI(title="Servico de Armazenamento")
 
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS imagens (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_arquivo TEXT NOT NULL,
        rotulo       TEXT NOT NULL,
        criado_em    TEXT NOT NULL)""")
    conn.commit()
    conn.close()
 
init_db()

@app.get("/")
def status():
    # endpoint leve, usado pelo healthcheck
    return {"status": "ok"}

@app.post("/salvar")
async def salvar_dados(file: UploadFile = File(...), rotulo: str = Form(...)):
    # basename impede que "../../etc/senha" escreva fora de /dados
    nome_seguro = os.path.basename(file.filename or "imagem.png")
    caminho = os.path.join(DIRETORIO_DADOS, nome_seguro)
    with open(caminho, "wb") as destino:
        destino.write(await file.read())
 
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO imagens (nome_arquivo, rotulo, criado_em) VALUES (?, ?, ?)",
        (nome_seguro, rotulo, datetime.now(timezone.utc).isoformat()))
    conn.commit(); conn.close()
    return {"mensagem": "Imagem e rotulo armazenados"}

@app.get("/imagens")            # prova que o volume persiste
def listar_imagens():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    linhas = conn.execute(
        "SELECT id, nome_arquivo, rotulo, criado_em FROM imagens ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return {"total" : len(linhas), "imagens": [dict(l) for l in linhas]}