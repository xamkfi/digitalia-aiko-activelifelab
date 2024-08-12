The demo is using Openchat LLM available at https://huggingface.co/openchat/openchat_3.5
Running this demo requires at least 16GB free VRAM on CUDA capable GPU, tested using NVIDIA A100 80GB

The demo can be tested with the provided Excel-files

Build the Docker image from the provided 'Dockerfile':
docker build -t aiko-demo-activelifelab .

Run the Docker container
docker run -p 7860:7860 aiko-demo-activelifelab