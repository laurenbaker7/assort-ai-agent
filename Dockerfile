FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Create non-root user
ARG UID=10001
RUN adduser --disabled-password --gecos "" --home "/home/appuser" --shell "/sbin/nologin" --uid "${UID}" appuser

WORKDIR /home/appuser

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chown appuser:appuser /home/appuser/appointments.json

USER appuser

RUN python agent.py download-files

CMD ["python", "agent.py", "start"]
