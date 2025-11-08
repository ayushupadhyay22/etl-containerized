FROM python:3.10-slim-buster 
# Use a lightweight Python image

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# No CMD here, as it's defined in docker-compose.yml
