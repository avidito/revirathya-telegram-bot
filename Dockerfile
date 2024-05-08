FROM python:3.8

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ /app/src
ENTRYPOINT ["python", "-m", "src.main"]