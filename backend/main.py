# /meu_projeto/backend/main.py

import json
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

# --- Bloco Principal da Aplicação ---
app = FastAPI()


# --- Gerenciador de Conexões WebSocket ---
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


# --- Endpoints da Aplicação ---

# Endpoint WebSocket: o frontend se conecta aqui
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Mantém a conexão viva aguardando mensagens (não faremos nada com elas)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Endpoint da API para acionar a fala
@app.post("/api/falar")
async def api_falar(body: dict):
    texto = body.get("texto", "Nenhum texto fornecido")
    mensagem = {"action": "speak", "payload": texto}
    await manager.broadcast(json.dumps(mensagem))
    return {"status": "comando de fala enviado", "texto": texto}

# Endpoint da API para acionar o alerta (modal + sirene)
@app.post("/api/alerta")
async def api_alerta(body: dict):
    mensagem_alerta = body.get("mensagem", "Alerta geral!")
    sirene_msg = {"action": "siren", "payload": "play"}
    await manager.broadcast(json.dumps(sirene_msg))
    
    modal_msg = {"action": "alert", "payload": mensagem_alerta}
    await manager.broadcast(json.dumps(modal_msg))
    
    return {"status": "comando de alerta enviado", "mensagem": mensagem_alerta}

# Endpoint da API para parar a sirene
@app.post("/api/parar_sirene")
async def api_parar_sirene():
    mensagem = {"action": "siren", "payload": "stop"}
    await manager.broadcast(json.dumps(mensagem))
    return {"status": "comando para parar sirene enviado"}


# --- ATUALIZAÇÃO IMPORTANTE ---
# Esta linha instrui o FastAPI a servir os arquivos estáticos (HTML, CSS, JS, MP3)
# da pasta 'frontend'. Ele deve ser colocado no final, após a definição de todas as rotas da API.
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
