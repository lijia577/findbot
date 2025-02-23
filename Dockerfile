# Use the latest Ubuntu LTS image
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update && apt-get install -y \
    wget \
    bzip2 \
    build-essential \
    git

# Download and install Miniconda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-$(arch).sh -O ~/miniconda.sh && \
    bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh

# Add conda to PATH
ENV PATH="/opt/conda/bin:$PATH"

# Create a new conda environment named 'findbot'
RUN conda create --name findbot python=3.13 -y

# Copy requirements.txt into the container
COPY requirements.txt /tmp/requirements.txt

# Install Python packages from requirements.txt into the 'findbot' environment
RUN /opt/conda/bin/conda run -n findbot pip install -r /tmp/requirements.txt
RUN /opt/conda/bin/conda init && source ~/.bashrc && /opt/conda/bin/conda activate findbot

# Set the default command to run when starting the container
CMD ["bash"]
