FROM python:3.12
WORKDIR /app
COPY . .
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "api:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
