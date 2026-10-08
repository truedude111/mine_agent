FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml requirements.txt ./
COPY agent ./agent
COPY services ./services
COPY fixtures ./fixtures

RUN pip install --no-cache-dir -r requirements.txt

ENV MINING_DATA=fixture
ENV PYTHONUNBUFFERED=1
ENV PYTHONUTF8=1

CMD ["python", "-m", "agent"]
