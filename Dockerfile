# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install pipeline as package
RUN pip install -e .

# Install Git and other dependencies
RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y nmap
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Start an interactive shell
CMD ["bash"]
