FROM python:3.9.6 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN python -m venv .venv
COPY requirements.txt ./
RUN .venv/bin/pip install -r requirements.txt

FROM python:3.9.6-slim
WORKDIR /app

COPY --from=builder /app/.venv .venv/
COPY . .

# Ensure we use the venv for python execution
ENV PATH="/app/.venv/bin:$PATH"

# Run your LiveKit agent
CMD ["python", "agent.py"]
