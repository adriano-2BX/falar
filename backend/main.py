# backend/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List
import json

app = FastAPI()

# Classe simples para gerenciar as conexões WebSocket ativas
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

# Endpoint WebSocket: o frontend se conecta aqui
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Apenas mantém a conexão viva. A lógica é de broadcast.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- Endpoints da API ---

# Endpoint para acionar a fala
@app.post("/api/falar")
async def api_falar(body: dict):
    texto = body.get("texto", "Nenhum texto fornecido")
    # Cria uma mensagem JSON para o frontend
    mensagem = {"action": "speak", "payload": texto}
    await manager.broadcast(json.dumps(mensagem))
    return {"status": "comando de fala enviado", "texto": texto}

# Endpoint para acionar o alerta (modal + sirene)
@app.post("/api/alerta")
async def api_alerta(body: dict):
    mensagem_alerta = body.get("mensagem", "Alerta geral!")
    # Comando para tocar a sirene
    sirene_msg = {"action": "siren", "payload": "play"}
    await manager.broadcast(json.dumps(sirene_msg))
    
    # Comando para mostrar o modal com uma mensagem
    modal_msg = {"action": "alert", "payload": mensagem_alerta}
    await manager.broadcast(json.dumps(modal_msg))
    
    return {"status": "comando de alerta enviado", "mensagem": mensagem_alerta}

# Endpoint para parar a sirene
@app.post("/api/parar_sirene")
async def api_parar_sirene():
    mensagem = {"action": "siren", "payload": "stop"}
    await manager.broadcast(json.dumps(mensagem))
    return {"status": "comando para parar sirene enviado"}
