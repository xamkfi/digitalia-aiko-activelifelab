# Use an official miniconda image as the base image
FROM continuumio/miniconda3

# Set the working directory inside the container
WORKDIR /app

# Copy the environment YAML file to the container
COPY environment.yml .

# Create the conda environment and activate it
RUN conda env create -f environment.yml
RUN echo "source activate aiko-neural" > ~/.bashrc
ENV PATH="/opt/conda/envs/aiko-neural/bin:$PATH"

# Copy the application code to the container
COPY aiko-demo-activelifelab.py /app

# Specify the command to run the application
CMD ["python", "aiko-demo-activelifelab.py"]
