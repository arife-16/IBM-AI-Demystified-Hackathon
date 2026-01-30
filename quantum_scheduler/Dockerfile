# Use an official lightweight Python image.
# `https://hub.docker.com/_/python`
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Copy local code to the container image.
COPY . ./

# List files to verify copy (for debugging)
RUN ls -la /app

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Service must listen to $PORT environment variable.
# This default value facilitates local development.
ENV PORT 8080

# Run the web service on container startup using gunicorn webserver.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
