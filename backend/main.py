# /meu_projeto/backend/main.py

import json
import logging
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO)
app = FastAPI()


# --- ATUALIZAÇÃO IMPORTANTE ---
# Adicione este endpoint de Health Check logo no início
# Ele é usado pela plataforma (EasyPanel) para verificar se a aplicação está online.
@app.get("/health")
async def health_check():
    return {"status": "ok"}


# --- O resto do código permanece o mesmo ---

class ConnectionManager:
    # ... (código do ConnectionManager sem alterações)
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
    # ... (código da API sem alterações)
    texto = body.get("texto", "Nenhum texto fornecido")
    mensagem = {"action": "speak", "payload": texto}
    await manager.broadcast(json.dumps(mensagem))
    return {"status": "comando de fala enviado", "texto": texto}


@app.post("/api/alerta")
async def api_alerta(body: dict):
    # ... (código da API sem alterações)
    mensagem_alerta = body.get("mensagem", "Alerta geral!")
    sirene_msg = {"action": "siren", "payload": "play"}
    await manager.broadcast(json.dumps(sirene_msg))
    modal_msg = {"action": "alert", "payload": mensagem_alerta}
    await manager.broadcast(json.dumps(modal_msg))
    return {"status": "comando de alerta enviado", "mensagem": mensagem_alerta}


@app.post("/api/parar_sirene")
async def api_parar_sirene():
    # ... (código da API sem alterações)
    mensagem = {"action": "siren", "payload": "stop"}
    await manager.broadcast(json.dumps(mensagem))
    return {"status": "comando para parar sirene enviado"}


app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
