# Self-Hosted Turn Detection Server

This directory contains everything you need to deploy the TEN Turn Detection model on your own infrastructure, eliminating the dependency on Cerebrium or any third-party cloud service.

## Overview

The self-hosted solution uses [vLLM](https://github.com/vllm-project/vllm) to provide an OpenAI-compatible API endpoint for the [TEN_Turn_Detection](https://huggingface.co/TEN-framework/TEN_Turn_Detection) model. This allows you to:

- **Run locally** on your own hardware
- **No cloud costs** - pay only for your infrastructure
- **Full control** over model deployment and configuration
- **Privacy** - your data never leaves your infrastructure
- **Same API** - drop-in replacement for the Cerebrium deployment

## Prerequisites

### Hardware Requirements

- **GPU**: NVIDIA GPU with at least 8GB VRAM (recommended: RTX 3080, A10, or better)
- **RAM**: 16GB+ system RAM
- **Storage**: 20GB free space (for model weights and Docker images)
- **CUDA**: CUDA 12.1+ installed and configured

### Software Requirements

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **NVIDIA Container Toolkit**: For GPU support in Docker

#### Installing NVIDIA Container Toolkit

If you haven't already, install the NVIDIA Container Toolkit:

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

Verify GPU access in Docker:
```bash
docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi
```

## Quick Start

### 1. Deploy the Server

Run the automated deployment script:

```bash
cd self_hosted
./deploy.sh
```

This will:
1. Pull the latest vLLM Docker image
2. Download the TEN_Turn_Detection model (~7GB)
3. Start the server on port 8000
4. Wait for the server to be ready

**First deployment takes 2-5 minutes** while the model downloads.

### 2. Verify Deployment

Test the server:

```bash
# Export environment variables (not required for local deployment)
export TTD_BASE_URL="http://localhost:8000/v1"
export TTD_API_KEY="not-needed-for-local"

# Run tests
python test.py
```

You should see output like:
```
Testing Self-Hosted Turn Detection API
[Test 1] Incomplete sentence:
User: 'Hello I have a question about'
Turn Detection Result: unfinished
✅ All tests completed successfully!
```

### 3. Configure Voice Assistant

Update your `.env` file in the voice assistant directory:

```bash
# Self-hosted Turn Detection (local deployment)
TTD_BASE_URL=http://localhost:8000/v1
TTD_API_KEY=not-needed-for-local
```

Or if deploying on a remote server:
```bash
TTD_BASE_URL=http://your-server-ip:8000/v1
TTD_API_KEY=not-needed-for-local
```

### 4. Run Voice Assistant

```bash
cd ../
task run
```

## Deployment Options

### Option 1: Docker Compose (Recommended)

The easiest way to deploy:

```bash
docker compose up -d
```

To stop:
```bash
docker compose down
```

To view logs:
```bash
docker compose logs -f turn-detection
```

### Option 2: Docker Run

For more control over Docker parameters:

```bash
docker run -d \
  --name ten-turn-detection \
  --gpus all \
  -p 8000:8000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  vllm/vllm-openai:latest \
  --model TEN-framework/TEN_Turn_Detection \
  --host 0.0.0.0 \
  --port 8000 \
  --trust-remote-code \
  --dtype auto \
  --gpu-memory-utilization 0.9
```

### Option 3: Python Script

If you prefer not to use Docker:

```bash
# Install dependencies
pip install vllm transformers

# Run the server
python main.py
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HUGGING_FACE_HUB_TOKEN` | - | Optional, for private models |

### Server Arguments

The server can be configured with these arguments:

```bash
python main.py \
  --model TEN-framework/TEN_Turn_Detection \
  --host 0.0.0.0 \
  --port 8000 \
  --gpu-memory-utilization 0.9
```

### Performance Tuning

**GPU Memory Utilization**
- Default: `0.9` (90% of GPU memory)
- Lower if you run other GPU workloads
- Higher for better performance (max: 0.95)

**Model Quantization** (for smaller GPUs)
```bash
# Add to docker-compose.yml command:
--quantization awq
```

**Batch Size**
```bash
# Add to docker-compose.yml command:
--max-num-seqs 32
```

## Remote Deployment

### Deploy on a Server

1. Copy the `self_hosted` directory to your server:
   ```bash
   scp -r self_hosted user@your-server:/path/to/deployment
   ```

2. SSH into your server and run deployment:
   ```bash
   ssh user@your-server
   cd /path/to/deployment/self_hosted
   ./deploy.sh
   ```

3. Update your local `.env` file with the server address:
   ```bash
   TTD_BASE_URL=http://your-server-ip:8000/v1
   ```

### Security Considerations

For production deployments:

1. **Use HTTPS**: Put the server behind a reverse proxy (nginx, Caddy)
2. **Add Authentication**: Use API keys or OAuth
3. **Firewall**: Restrict access to port 8000
4. **Rate Limiting**: Prevent abuse
5. **Monitoring**: Set up health checks and alerts

Example nginx configuration:
```nginx
server {
    listen 443 ssl;
    server_name turn-detection.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### API Documentation

Interactive API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Server Stats

```bash
curl http://localhost:8000/v1/models
```

## Troubleshooting

### Server Won't Start

**GPU not detected:**
```bash
# Verify GPU access
docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi
```

**Out of memory:**
- Reduce `--gpu-memory-utilization` to 0.7 or 0.8
- Close other GPU-using applications
- Consider model quantization

**Port already in use:**
```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Slow Performance

**First request is slow:**
- This is normal - the model is loading
- Subsequent requests will be fast (~50-100ms)

**All requests are slow:**
- Check GPU utilization: `nvidia-smi`
- Increase `--gpu-memory-utilization`
- Verify no other GPU workloads are running

### Model Download Fails

**Timeout during download:**
```bash
# Manually download model
export HF_HOME=~/.cache/huggingface
huggingface-cli download TEN-framework/TEN_Turn_Detection
```

**Private model access:**
```bash
# Set Hugging Face token
export HUGGING_FACE_HUB_TOKEN=your_token_here
```

## Cost Comparison

### Cerebrium (Cloud)
- **Setup**: 5 minutes
- **Cost**: ~$0.50-1.00 per hour of GPU usage
- **Scaling**: Automatic
- **Maintenance**: None

### Self-Hosted
- **Setup**: 15-30 minutes
- **Cost**: Only your infrastructure (one-time hardware or monthly VPS)
- **Scaling**: Manual
- **Maintenance**: Updates, monitoring, backups

### When to Use Each

**Use Cerebrium if:**
- You want zero maintenance
- You prefer pay-as-you-go pricing
- You need automatic scaling
- You don't have GPU infrastructure

**Use Self-Hosted if:**
- You have existing GPU infrastructure
- You want full control and privacy
- You need predictable costs
- You have compliance requirements

## Alternative Deployment Methods

### 1. Using vLLM's API Server Directly

```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server \
  --model TEN-framework/TEN_Turn_Detection \
  --trust-remote-code \
  --dtype auto \
  --host 0.0.0.0 \
  --port 8000
```

### 2. Using Text Generation Inference (TGI)

```bash
docker run --gpus all -p 8000:80 \
  -v ~/.cache/huggingface:/data \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id TEN-framework/TEN_Turn_Detection \
  --trust-remote-code
```

### 3. Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests (if needed).

## Support

For issues with:
- **This deployment**: Open an issue in the TEN Framework repository
- **vLLM**: See [vLLM documentation](https://docs.vllm.ai/)
- **The model**: See [TEN_Turn_Detection on Hugging Face](https://huggingface.co/TEN-framework/TEN_Turn_Detection)

## Learn More

- [vLLM Documentation](https://docs.vllm.ai/)
- [TEN Framework Documentation](https://theten.ai/docs)
- [TEN Turn Detection Model](https://huggingface.co/TEN-framework/TEN_Turn_Detection)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)
