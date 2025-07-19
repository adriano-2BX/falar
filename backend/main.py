# /meu_projeto/backend/main.py (VERSÃO DE TESTE MÍNIMA)

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Aplicação mínima no ar!"}
