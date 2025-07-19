# /meu_projeto/backend/main.py (VERSÃO COM PAINEL DE SERVIDORES)

import asyncio
import json
import logging
from typing import List

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sse_starlette.sse import EventSourceResponse

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)

# Criação da aplicação FastAPI
app = FastAPI()

# --- Sistema de Broadcast para SSE (sem alterações) ---
class Broadcaster:
    def __init__(self):
        self.queues: List[asyncio.Queue] = []
    def add_queue(self, queue: asyncio.Queue):
        self.queues.append(queue)
    def remove_queue(self, queue: asyncio.Queue):
        self.queues.remove(queue)
    async def broadcast(self, message: str):
        for queue in self.queues:
            await queue.put(message)

broadcaster = Broadcaster()

# --- Endpoint SSE (sem alterações) ---
@app.get("/stream")
async def event_stream(request: Request):
    queue = asyncio.Queue()
    broadcaster.add_queue(queue)
    async def event_generator():
        try:
            while True:
                if await request.is_disconnected(): break
                message = await queue.get()
                yield message
        finally:
            broadcaster.remove_queue(queue)
            logging.info("Cliente SSE desconectado.")
    return EventSourceResponse(event_generator())

# --- Rota da Página Inicial (sem alterações) ---
@app.get("/", response_class=FileResponse)
async def read_index():
    return "frontend/index.html"

# --- Endpoints da API ---

# Endpoints antigos (falar, alerta) continuam funcionando
@app.post("/api/falar")
async def api_falar(body: dict):
    texto = body.get("texto", "Nenhum texto fornecido")
    mensagem = {"action": "speak", "payload": texto}
    await broadcaster.broadcast(json.dumps(mensagem))
    return {"status": "comando de fala enviado"}

@app.post("/api/alerta")
async def api_alerta(body: dict):
    mensagem_alerta = body.get("mensagem", "Alerta geral!")
    sirene_msg = {"action": "siren", "payload": "play"}
    await broadcaster.broadcast(json.dumps(sirene_msg))
    modal_msg = {"action": "alert", "payload": mensagem_alerta}
    await broadcaster.broadcast(json.dumps(modal_msg))
    return {"status": "comando de alerta enviado"}

@app.post("/api/parar_sirene")
async def api_parar_sirene():
    mensagem = {"action": "siren", "payload": "stop"}
    await broadcaster.broadcast(json.dumps(mensagem))
    return {"status": "comando para parar sirene enviado"}


# --- NOVO ENDPOINT PARA ATUALIZAR STATUS DO SERVIDOR ---
@app.post("/api/server-status")
async def update_server_status(body: dict):
    server_id = body.get("server_id")
    status = body.get("status") # ex: "normal", "overloaded", "down"

    if server_id is None or status is None:
        return {"error": "server_id e status são obrigatórios"}, 400

    # Cria a mensagem para o frontend
    mensagem = {
        "action": "update_server",
        "payload": {
            "id": server_id,
            "status": status
        }
    }
    await broadcaster.broadcast(json.dumps(mensagem))
    return {"status": f"Status do servidor {server_id} atualizado para {status}"}


# Mount para servir arquivos estáticos (sem alterações)
app.mount("/static", StaticFiles(directory="frontend"), name="static")
