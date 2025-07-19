# /meu_projeto/backend/main.py (VERSÃO COM SSE)

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

# --- NOVO SISTEMA DE BROADCAST PARA SSE ---
# Cada cliente que se conectar terá sua própria fila de mensagens.
# Quando uma API for chamada, a mensagem será colocada em TODAS as filas.
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


# --- ENDPOINT SSE ---
# O cliente se conectará aqui para "escutar" os eventos
@app.get("/stream")
async def event_stream(request: Request):
    queue = asyncio.Queue()
    broadcaster.add_queue(queue)
    
    async def event_generator():
        try:
            while True:
                # Se o cliente desconectar, o await vai levantar uma exceção
                if await request.is_disconnected():
                    break
                
                # Espera por uma nova mensagem na fila e a envia para o cliente
                message = await queue.get()
                yield message
        finally:
            # Garante que a fila seja removida quando o cliente desconectar
            broadcaster.remove_queue(queue)
            logging.info("Cliente SSE desconectado.")

    return EventSourceResponse(event_generator())


# --- ROTA DA PÁGINA INICIAL ---
@app.get("/", response_class=FileResponse)
async def read_index():
    return "frontend/index.html"


# --- ENDPOINTS DA API (ATUALIZADOS) ---
# Agora eles usam o 'broadcaster' para enviar mensagens
@app.post("/api/falar")
async def api_falar(body: dict):
    texto = body.get("texto", "Nenhum texto fornecido")
    mensagem = {"action": "speak", "payload": texto}
    await broadcaster.broadcast(json.dumps(mensagem))
    return {"status": "comando de fala enviado", "texto": texto}

@app.post("/api/alerta")
async def api_alerta(body: dict):
    mensagem_alerta = body.get("mensagem", "Alerta geral!")
    sirene_msg = {"action": "siren", "payload": "play"}
    await broadcaster.broadcast(json.dumps(sirene_msg))
    
    modal_msg = {"action": "alert", "payload": mensagem_alerta}
    await broadcaster.broadcast(json.dumps(modal_msg))
    return {"status": "comando de alerta enviado", "mensagem": mensagem_alerta}

@app.post("/api/parar_sirene")
async def api_parar_sirene():
    mensagem = {"action": "siren", "payload": "stop"}
    await broadcaster.broadcast(json.dumps(mensagem))
    return {"status": "comando para parar sirene enviado"}


# Mount para servir arquivos estáticos como sirene.mp3
app.mount("/static", StaticFiles(directory="frontend"), name="static")
