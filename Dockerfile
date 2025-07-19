# /meu_projeto/Dockerfile

# Estágio 1: Usar uma imagem base oficial e leve do Python.
FROM python:3.9-slim

# Estágio 2: Definir o diretório de trabalho dentro do container.
WORKDIR /app

# Estágio 3: Copiar e instalar as dependências.
COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Estágio 4: Copiar os arquivos da aplicação para o container.
COPY ./backend/ .
COPY ./frontend/ ./frontend/

# Estágio 5: Expor a porta que a aplicação vai rodar.
# A porta aqui é informativa; a porta real será definida no CMD.
EXPOSE 8000

# Estágio 6: Definir o comando para iniciar a aplicação.
# Usa a variável de ambiente $PORT se existir, caso contrário, usa 8000.
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
