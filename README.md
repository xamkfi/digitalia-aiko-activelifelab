# digitalia-aiko-activelifelab
Aiko hankkeen activelifelab demo joka on testattavissa https://memorylab.fi/AIKO/activelifelab-demo/

The demo is using Openchat LLM available at https://huggingface.co/openchat/openchat_3.5
Running this demo requires at least 16GB free VRAM on CUDA capable GPU, tested using NVIDIA A100 80GB

The demo can be tested with the provided Excel-files

## Build the Docker image from the provided 'Dockerfile':
`sudo docker build -t activelifelab .`

## Run the Docker container
`docker run --gpus 2 -p 7862:7862 --name activelifelab -d --restart unless-stopped activelifelab`
*This command passes two GPUs into container and exposes port 7862
## Test
*Should be accessible via localhost:7862, e.g. http://192.168.10.128:7862/ (or what ever your internal IP is)
