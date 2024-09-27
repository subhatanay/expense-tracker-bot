# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY bot /app

# Install any necessary dependencies from requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 443

# Define environment variable
ENV FLASK_APP=rest_server.py

# Command to run the Flask app
CMD ["python",  "rest_server.py"]