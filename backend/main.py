# /meu_projeto/backend/main.py

import json
import logging
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)

# Criação da aplicação FastAPI
app = FastAPI()

# Rota explícita para a página inicial e Health Check
@app.get("/", response_class=FileResponse)
async def read_index():
    return "frontend/index.html"

# Endpoint de Health Check secundário
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Gerenciador de conexões WebSocket
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

# Endpoint do WebSocket
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

# Endpoints da API
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

# Mount para servir arquivos estáticos como sirene.mp3
app.mount("/static", StaticFiles(directory="frontend"), name="static")
