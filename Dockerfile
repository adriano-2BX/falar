# Estágio 1: Construir o backend
FROM python:3.9-slim as builder

WORKDIR /app

COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./backend/ .

# Estágio 2: Imagem final com Nginx para servir frontend e backend
FROM nginx:alpine

# Copia a configuração do Nginx (ver abaixo)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia os arquivos do frontend para a pasta que o Nginx serve
COPY --from=builder /app /app
COPY ./frontend/ /usr/share/nginx/html

# Expor a porta 80
EXPOSE 80

# Um script para iniciar ambos os serviços
CMD sh -c 'cd /app && uvicorn main:app --host 0.0.0.0 --port 8000 & nginx -g "daemon off;"'
