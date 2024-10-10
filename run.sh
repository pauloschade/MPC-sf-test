#!/bin/bash

# Set the image name
IMAGE_NAME="fastapi-app-secretflow-app"

# Step 1: Build the Docker image
echo "Building Docker image: $IMAGE_NAME"
docker build -t $IMAGE_NAME .

# Check if the build was successful
if [ $? -eq 0 ]; then
    echo "Docker image built successfully!"
else
    echo "Failed to build Docker image. Exiting."
    exit 1
fi

# Step 2: Run the Docker container
echo "Running the Docker container on port 80..."
docker run -it -p 80:80 $IMAGE_NAME

# Check if the container is running
if [ $? -eq 0 ]; then
    echo "Container is running at http://localhost:80"
else
    echo "Failed to run the Docker container."
    exit 1
fi