FROM python:3.12

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Ajoutez d'autres dépendances si nécessaire

CMD ["pytest"]