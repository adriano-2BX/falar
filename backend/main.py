# /meu_projeto/backend/main.py

import json
import logging
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

# Configura um logger básico para vermos as mensagens no log do EasyPanel
logging.basicConfig(level=logging.INFO)

app = FastAPI()

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
    # --- ATUALIZAÇÃO IMPORTANTE AQUI ---
    except Exception as e:
        # Captura qualquer outro erro inesperado que possa ocorrer
        logging.error(f"Erro inesperado na conexão com {websocket.client.host}: {e}")
        manager.disconnect(websocket)

# ... (o resto do código da API continua igual)
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

app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
