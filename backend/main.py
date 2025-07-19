# /meu_projeto/backend/main.py

# ... (imports de antes) ...
from pydantic import BaseModel, Field
from typing import Optional

# --- MODELO DE DADOS Pydantic ---
# Define a estrutura dos dados completos que esperamos receber para cada servidor.
# FastAPI usará isso para validar automaticamente os dados da API.
class ServerData(BaseModel):
    id: int = Field(..., gt=0) # ID do servidor (obrigatório, maior que 0)
    name: Optional[str] = "Servidor"
    status: str # "normal", "overloaded", "down"
    cpu_load: Optional[float] = Field(None, ge=0, le=100) # Uso de CPU em %
    ram_usage: Optional[float] = Field(None, ge=0, le=100) # Uso de RAM em %
    disk_space: Optional[float] = Field(None, ge=0, le=100) # Espaço em disco usado em %
    uptime: Optional[str] = "N/A"
    last_error: Optional[str] = None

# ... (Broadcaster, SSE endpoint, etc. continuam iguais) ...

# --- ENDPOINT ATUALIZADO ---
# Agora ele recebe o modelo ServerData completo
@app.post("/api/server-status")
async def update_server_status(data: ServerData):
    # Cria a mensagem para o frontend com todos os dados recebidos
    mensagem = {
        "action": "update_server",
        "payload": data.dict() # Converte o modelo Pydantic para um dicionário
    }
    await broadcaster.broadcast(json.dumps(mensagem))
    return {"status": f"Dados do servidor {data.id} recebidos com sucesso"}

# ... (Resto dos endpoints e o mount de arquivos estáticos) ...
# O frontend agora será uma aplicação separada, então o `app.mount` e a rota "/"
# podem ser removidos se você for servir o frontend de outro lugar.
# Por enquanto, vamos manter para não quebrar o que já existe.
