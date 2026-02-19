FROM python:3.12

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Le modèle sera dans /code/models/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
