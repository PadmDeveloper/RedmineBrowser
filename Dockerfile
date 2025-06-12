## Use Playwright's official Python image (includes browsers & deps)
# FROM mcr.microsoft.com/playwright/python:1.52.0
From mcr.microsoft.com/playwright:v1.50.0-noble

# 1. Set working directory
WORKDIR /app

# NEW: Install pip
RUN apt-get update && apt-get install -y python3-pip

# 2. Copy dependency file
COPY requirements.txt ./

# 3. Install Python dependencies
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# 4. Copy application code
COPY . .

# 5. Expose port for Flask
EXPOSE 5000

# 6. Environment variables are injected at runtime (via Docker -e or Render's env settings)
#    No need to hardcode in Dockerfile.

# 7. Start both services via your runner script
CMD ["python3", "run_services.py"]
