# Cerebrium Deployment Guide

Deploy the TEN Turn Detection model to Cerebrium's managed GPU infrastructure. This provides a fully managed, auto-scaling API endpoint with zero infrastructure management.

## Overview

[Cerebrium](https://www.cerebrium.ai/) is a serverless GPU platform that makes it easy to deploy ML models with automatic scaling, monitoring, and management. This deployment option is ideal for:

- Quick prototyping and demos
- Production workloads without infrastructure management
- Variable traffic patterns that benefit from auto-scaling
- Teams without GPU infrastructure or DevOps resources

## Prerequisites

### Software Requirements

- Python 3.8+
- pip (Python package manager)
- Cerebrium account (free tier available)

### Create Cerebrium Account

1. Sign up at [Cerebrium](https://www.cerebrium.ai/)
2. Verify your email
3. Get your API key from the dashboard

## Quick Start

### 1. Install Cerebrium CLI

```bash
pip install cerebrium
```

### 2. Login to Cerebrium

```bash
cerebrium login
```

This will open your browser to authenticate and store your credentials locally.

### 3. Deploy the Model

```bash
cd cerebrium
cerebrium deploy
```

This command will:
- Package the deployment code and configuration
- Upload to Cerebrium
- Provision an NVIDIA A10 GPU instance
- Download and load the TEN_Turn_Detection model (~7GB)
- Start the OpenAI-compatible API server
- Return your deployment URL and API key

**First deployment takes 5-10 minutes** while infrastructure is provisioned.

### 4. Get Your Credentials

After successful deployment, Cerebrium provides:

- **Base URL**: `https://api.cortex.cerebrium.ai/v4/p-xxxxx/ten-turn-detection-project/run`
- **API Key**: Your Cerebrium API token (from login)

**Important**: The base URL must end with `/run` for OpenAI client compatibility.

### 5. Test the Deployment

```bash
# Set environment variables
export TTD_BASE_URL="https://api.cortex.cerebrium.ai/v4/p-xxxxx/ten-turn-detection-project/run"
export TTD_API_KEY="your_cerebrium_api_key"

# Run test script
python test.py
```

Expected output:
```
Testing Turn Detection API with AsyncOpenAI
[Test 1] Incomplete sentence:
User: 'Hello I have a question about'
Turn Detection Result: unfinished
Run Time: 124.56ms
✅ All tests completed successfully!
```

## Configuration

### Deployment Settings

The deployment is configured in `cerebrium.toml`:

```toml
[cerebrium.deployment]
name = "ten-turn-detection-project"
python_version = "3.12"
docker_base_image_url = "nvidia/cuda:12.1.1-runtime-ubuntu22.04"

[cerebrium.hardware]
cpu = 2.0           # CPU cores
memory = 14.0       # GB of RAM
compute = "AMPERE_A10"  # GPU type
gpu_count = 1

[cerebrium.scaling]
min_replicas = 1    # Always-on instances
max_replicas = 2    # Maximum for auto-scaling
cooldown = 300      # Seconds before scaling down
```

### Customizing Hardware

You can adjust hardware in `cerebrium.toml`:

**For smaller workloads:**
```toml
[cerebrium.hardware]
compute = "AMPERE_A4000"  # Smaller, cheaper GPU
```

**For higher throughput:**
```toml
[cerebrium.scaling]
max_replicas = 5    # More instances
```

**For faster cold starts:**
```toml
[cerebrium.scaling]
min_replicas = 2    # Keep 2 instances always warm
```

### Dependencies

Python dependencies are specified in `cerebrium.toml`:

```toml
[cerebrium.dependencies.pip]
vllm = "latest"
transformers = "latest"
pydantic = "latest"
```

## Usage with Voice Assistant

### Update Environment Variables

Add to your `.env` file:

```bash
# Cerebrium Turn Detection
TTD_BASE_URL=https://api.cortex.cerebrium.ai/v4/p-xxxxx/ten-turn-detection-project/run
TTD_API_KEY=your_cerebrium_api_key_here
```

### Run Voice Assistant

```bash
cd ../
task run
```

The voice assistant will now use your Cerebrium-hosted turn detection model.

## Management

### View Deployment Status

```bash
cerebrium status
```

### View Logs

```bash
cerebrium logs ten-turn-detection-project
```

Or view in the Cerebrium dashboard: https://dashboard.cerebrium.ai/

### Update Deployment

After making changes to `main.py` or `cerebrium.toml`:

```bash
cerebrium deploy
```

### Delete Deployment

```bash
cerebrium delete ten-turn-detection-project
```

## Monitoring

### Cerebrium Dashboard

Access https://dashboard.cerebrium.ai/ to view:
- Request metrics (count, latency, errors)
- GPU utilization
- Costs and usage
- Logs and traces

### Custom Monitoring

The deployment automatically tracks:
- Request latency (see test.py output)
- Token usage
- Error rates

### Alerts

Set up alerts in the Cerebrium dashboard for:
- High error rates
- Unusual latency
- Cost thresholds

## Pricing

Cerebrium charges for:
- **GPU time**: Pay per second of GPU usage
- **Compute**: Based on GPU type (A10, A4000, etc.)
- **Storage**: Model weights storage (minimal)

**Typical costs:**
- NVIDIA A10: ~$0.50-1.00 per GPU hour
- Automatic scaling means you only pay for what you use
- Free tier available for testing

**Cost optimization:**
- Set `min_replicas = 0` to avoid idle costs (adds cold start latency)
- Use smaller GPU for lower traffic
- Monitor usage in dashboard

See [Cerebrium Pricing](https://www.cerebrium.ai/pricing) for current rates.

## Troubleshooting

### Deployment Fails

**Authentication error:**
```bash
# Re-login
cerebrium logout
cerebrium login
```

**Out of quota:**
- Check your account limits in the dashboard
- Upgrade plan or request limit increase

**Model download timeout:**
- This is usually temporary
- Retry deployment: `cerebrium deploy`

### Slow Response Times

**Cold starts:**
- First request after idle takes 10-20 seconds
- Set `min_replicas = 1` to keep always warm
- Or accept cold start for cost savings

**High latency:**
- Check network connectivity
- View metrics in dashboard
- Consider geographic region of deployment

### Test Script Fails

**Connection error:**
```bash
# Verify deployment is running
cerebrium status

# Check URL ends with /run
export TTD_BASE_URL="...your-url.../run"
```

**Response format error:**
- Ensure using latest cerebrium CLI: `pip install --upgrade cerebrium`
- Check compatibility notes in code comments

## Security

### API Authentication

- API key is required for all requests
- Store API key securely (environment variables, secrets manager)
- Rotate keys periodically in dashboard

### Network Access

- Deployment is publicly accessible by default
- Add IP whitelist in Cerebrium dashboard (Enterprise)
- Use VPC for private deployments (Enterprise)

### Data Privacy

- Requests are processed on Cerebrium infrastructure
- Subject to Cerebrium's [Privacy Policy](https://www.cerebrium.ai/privacy)
- Consider self-hosted for sensitive data

## Advanced Features

### Custom Domain

Set up custom domain in Cerebrium dashboard:
1. Add CNAME record to your DNS
2. Configure in dashboard
3. Update `TTD_BASE_URL` to use custom domain

### Multiple Environments

Deploy separate instances for dev/staging/prod:

```bash
# Development
cerebrium deploy --env dev

# Production
cerebrium deploy --env prod
```

Update deployment name in `cerebrium.toml` for each environment.

### A/B Testing

Deploy multiple versions:
```bash
# Deploy v1
cerebrium deploy --version v1

# Deploy v2
cerebrium deploy --version v2
```

Route traffic via different URLs or split in application code.

## Migration to Self-Hosted

If you later want to self-host:

1. Follow [self_hosted/README.md](../self_hosted/README.md) guide
2. Update `.env` with new `TTD_BASE_URL`
3. Restart voice assistant
4. Optionally delete Cerebrium deployment

**No code changes required** - both use the same OpenAI-compatible API.

## Support

### Cerebrium Support

- Documentation: https://docs.cerebrium.ai/
- Discord: https://discord.gg/cerebrium
- Email: support@cerebrium.ai

### TEN Framework Support

- Documentation: https://theten.ai/docs
- GitHub Issues: https://github.com/TEN-framework/ten-framework/issues
- Model: https://huggingface.co/TEN-framework/TEN_Turn_Detection

## Learn More

- [Cerebrium Documentation](https://docs.cerebrium.ai/)
- [vLLM Documentation](https://docs.vllm.ai/)
- [TEN Turn Detection Model](https://huggingface.co/TEN-framework/TEN_Turn_Detection)
- [Deployment Comparison Guide](../DEPLOYMENT_COMPARISON.md)
