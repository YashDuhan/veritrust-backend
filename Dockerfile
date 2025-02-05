FROM python:3.11-slim

WORKDIR /app

# Install Git and clean up unnecessary package lists to reduce image size
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set an environment variable to indicate that this is running inside a dev container
ENV IS_DEVCONTAINER=true

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Start the application with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
