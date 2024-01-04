# Use the official Python image as the base image
FROM python:3.9

# 以下の処理を行っていくときのuser
USER root

# Set the working directory
WORKDIR /app

# Copy the rest of the application code
COPY . .

# Install the required packages
RUN pip install --trusted-host pypi.python.org -r requirements.txt


# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True


EXPOSE 80 80