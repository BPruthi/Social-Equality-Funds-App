# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV CONDA_DIR=/opt/conda

# Install required packages and Miniconda
RUN apt-get update -y && \
    apt-get install -y curl git python3-dev build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    curl -sS https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p $CONDA_DIR && \
    rm /tmp/miniconda.sh && \
    $CONDA_DIR/bin/conda clean -afy


# Add conda to PATH
ENV PATH=$CONDA_DIR/bin:$PATH

# Creating a working directory
WORKDIR /wst_app

# Create a conda environment with Python 3.11.4
RUN conda create --name venv python=3.11.4 -y

COPY ./requirements.txt /wst_app/

# Activate the conda environment and install dependencies
RUN /bin/bash -c "source activate venv && pip3 install -r requirements.txt"

# Copy the rest of the application code
COPY . .

# Set environment variables for the application
ENV HOST=0.0.0.0
ENV LISTEN_PORT=8080
ENV CONDA_DEFAULT_ENV=venv

# Expose the application port
EXPOSE 8080

# Run the application
CMD ["bash", "-c", "source activate venv && streamlit run app.py --server.port 8080"]
