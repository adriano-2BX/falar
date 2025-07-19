# /meu_projeto/backend/main.py

import json
import logging
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse  # <-- 1. IMPORTAÇÃO ADICIONADA

logging.basicConfig(level=logging.INFO)
app = FastAPI()


# --- ATUALIZAÇÃO IMPORTANTE ---
# 2. ROTA EXPLÍCITA PARA A PÁGINA INICIAL E HEALTH CHECK
# Esta rota captura os acessos à raiz "/" e responde diretamente com o arquivo index.html.
# Isso garante uma resposta rápida e um status 200 OK para o health check do EasyPanel.
@app.get("/", response_class=FileResponse)
async def read_index():
    return "frontend/index.html"


# --- Endpoint de Health Check (Manter para garantir) ---
# Mesmo que o EasyPanel não permita configurar, não custa nada manter esta rota.
@app.get("/health")
async def health_check():
    return {"status": "ok"}


# --- O resto do código permanece o mesmo ---

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    logging.info(f"Cliente {websocket.client.host} conectado.")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logging.info(f"Cliente {websocket.client.host} desconectado.")
    except Exception as e:
        logging.error(f"Erro inesperado na conexão com {websocket.client.host}: {e}")
        manager.disconnect(websocket)

@app.post("/api/falar")
async def api_falar(body: dict):
    texto = body.get("texto", "Nenhum texto fornecido")
    mensagem = {"action": "speak", "payload": texto}
    await manager.broadcast(json.dumps(mensagem))
    return {"status": "comando de fala enviado", "texto": texto}

@app.post("/api/alerta")
async def api_alerta(body: dict):
    mensagem_alerta = body.get("mensagem", "Alerta geral!")
    sirene_msg = {"action": "siren", "payload": "play"}
    await manager.broadcast(json.dumps(sirene_msg))
    modal_msg = {"action": "alert", "payload": mensagem_alerta}
    await manager.broadcast(json.dumps(modal_msg))
    return {"status": "comando de alerta enviado", "mensagem": mensagem_alerta}

@app.post("/api/parar_sirene")
async def api_parar_sirene():
    mensagem = {"action": "siren", "payload": "stop"}
    await manager.broadcast(json.dumps(mensagem))
    return {"status": "comando para parar sirene enviado"}


# --- 3. ATUALIZAÇÃO NO MOUNT ---
# Agora o mount serve apenas para os *outros* arquivos da pasta, como sirene.mp3.
# A rota "/" já foi capturada pela função read_index() acima.
app.mount("/", StaticFiles(directory="frontend"), name="static")
