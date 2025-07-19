# /meu_projeto/Dockerfile

# ... (todo o início do Dockerfile permanece o mesmo) ...

# SUBSTITUA A LINHA CMD ANTIGA POR ESTA:
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
