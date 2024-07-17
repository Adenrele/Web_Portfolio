# Use the official Python image from the Docker Hub
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a directory for the application
WORKDIR /Code

# Install dependencies
COPY requirements.txt /Code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . /Code

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD ["python", "main.py"]
