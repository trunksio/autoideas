FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY src/ ./src/

# Install dependencies using uv
RUN uv pip install --system -e .

# Make worker script executable
RUN chmod +x /app/src/worker.py

# Run the worker directly
CMD ["python", "/app/src/worker.py"]