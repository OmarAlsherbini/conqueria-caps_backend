# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install any needed packages (including netcat)
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container first to leverage Docker's caching mechanism
COPY requirements.txt .

# Install any needed packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable to disable .pyc file generation and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Declare an ARG to accept environment variables during build
ARG ENVIRONMENT

# Set the ARG as an environment variable inside the container
ENV ENVIRONMENT=${ENVIRONMENT}

# Copy the entrypoint script and make it executable
COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

# Run Alembic migrations
# RUN alembic revision --autogenerate -m "automated migration by docker"
# RUN alembic upgrade head

# Run Alembic migrations and run the FastAPI app using Uvicorn
# CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]

