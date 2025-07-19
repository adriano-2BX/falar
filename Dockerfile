# /meu_projeto/Dockerfile

# Estágio 1: Usar uma imagem base oficial do Python.
# python:3.9-slim é uma boa escolha por ser leve.
FROM python:3.9-slim

# Estágio 2: Definir o diretório de trabalho dentro do container.
# Todas as ações seguintes acontecerão dentro de /app.
WORKDIR /app

# Estágio 3: Copiar e instalar as dependências.
# Copiamos o requirements.txt primeiro para aproveitar o cache do Docker.
COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Estágio 4: Copiar os arquivos da aplicação para o container.
# Copia o código do backend para o diretório de trabalho /app.
COPY ./backend/ .
# Copia o código do frontend para uma subpasta /app/frontend.
# Isso é crucial para que o StaticFiles do FastAPI encontre os arquivos.
COPY ./frontend/ ./frontend/

# Estágio 5: Expor a porta que a aplicação vai rodar.
# O Uvicorn vai rodar na porta 8000 dentro do container.
EXPOSE 8000

# Estágio 6: Definir o comando para iniciar a aplicação.
# Inicia o servidor Uvicorn, fazendo-o escutar em todas as interfaces (--host 0.0.0.0)
# na porta 8000, que é a que expomos.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
