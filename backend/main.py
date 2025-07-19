# /meu_projeto/backend/main.py

import asyncio
import json
import logging
from typing import List, Optional

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)

# A linha crucial que estava faltando ou fora de ordem
app = FastAPI()


# --- MODELO DE DADOS Pydantic ---
class ServerData(BaseModel):
    id: int = Field(..., gt=0)
    name: Optional[str] = "Servidor"
    status: str
    cpu_load: Optional[float] = Field(None, ge=0, le=100)
    ram_usage: Optional[float] = Field(None, ge=0, le=100)
    disk_space: Optional[float] = Field(None, ge=0, le=100)
    uptime: Optional[str] = "N/A"
    last_error: Optional[str] = None


# --- Sistema de Broadcast para SSE ---
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


# --- Endpoints da Aplicação ---

# Rota para a página inicial
@app.get("/", response_class=FileResponse)
async def read_index():
    return "frontend/index.html"

# Endpoint SSE para comunicação em tempo real
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

# Endpoint para atualizar o status de um servidor
@app.post("/api/server-status")
async def update_server_status(data: ServerData):
    mensagem = {
        "action": "update_server",
        "payload": data.dict()
    }
    await broadcaster.broadcast(json.dumps(mensagem))
    return {"status": f"Dados do servidor {data.id} recebidos com sucesso"}


# Mount para servir arquivos estáticos como sirene.mp3 etc.
app.mount("/static", StaticFiles(directory="frontend"), name="static")
