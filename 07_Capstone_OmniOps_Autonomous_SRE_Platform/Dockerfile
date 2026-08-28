# Multi-stage minimal production Dockerfile for Google Cloud Run
FROM python:3.11-slim as builder

WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim as runner
WORKDIR /app

# Security: Non-root user
RUN addgroup --system appgroup && adduser --system --group appuser

COPY --from=builder /root/.local /home/appuser/.local
COPY app/ /app/

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

USER appuser
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
