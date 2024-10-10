# Use the SecretFlow base image
FROM secretflow/secretflow-anolis8:latest

# Set the working directory inside the container
WORKDIR /code

# Copy the requirements.txt file to the container
COPY ./requirements.txt /code/requirements.txt

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the app directory (containing your FastAPI app) to the container
COPY ./app /code/app
COPY ./src /code/src

# Expose port 80 (since you want to run on this port)
EXPOSE 80

# Use Uvicorn with hot reloading for development
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]