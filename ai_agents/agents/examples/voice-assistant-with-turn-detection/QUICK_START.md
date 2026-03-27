# Quick Start Guide

Choose your turn detection deployment method and get started in minutes.

## Option 1: Self-Hosted (Full Control)

**Best for:** Privacy, cost control, existing GPU infrastructure

```bash
# 1. Start the turn detection server
cd self_hosted
./deploy.sh

# 2. Configure environment
export TTD_BASE_URL="http://localhost:8000/v1"
export TTD_API_KEY="not-needed-for-local"

# 3. Run voice assistant
cd ..
task run
```

📖 **Full guide:** [self_hosted/README.md](self_hosted/README.md)

---

## Option 2: Cerebrium (Cloud Hosted)

**Best for:** Quick setup, no infrastructure, automatic scaling

```bash
# 1. Deploy to Cerebrium
pip install cerebrium
cerebrium login
cd cerebrium
cerebrium deploy

# 2. Configure environment (use your deployment URL)
export TTD_BASE_URL="https://api.cortex.cerebrium.ai/v4/p-xxxxx/ten-turn-detection-project/run"
export TTD_API_KEY="your_cerebrium_api_key"

# 3. Run voice assistant
cd ..
task run
```

📖 **Full guide:** [cerebrium/README.md](cerebrium/README.md)

---

## Need Help Choosing?

See [DEPLOYMENT_COMPARISON.md](DEPLOYMENT_COMPARISON.md) for detailed comparison.

**TL;DR:**
- **Prototyping?** → Use Cerebrium
- **Production with GPU?** → Use Self-Hosted  
- **Enterprise/Regulated?** → Use Self-Hosted
- **No GPU hardware?** → Use Cerebrium

---

## Test Your Deployment

```bash
# For self-hosted
cd self_hosted
python test.py

# For Cerebrium
cd cerebrium
python test.py
```

---

## Additional Resources

- 📚 [Integration Guide](INTEGRATION_GUIDE.md) - Technical details
- 🔧 [Troubleshooting](#troubleshooting) - Common issues
- 🤔 [FAQ](#faq) - Frequently asked questions

---

## Troubleshooting

### Self-Hosted Issues

**Server won't start:**
```bash
# Check Docker
docker --version
docker compose version

# Check GPU
nvidia-smi

# View logs
docker compose logs -f turn-detection
```

**Connection refused:**
```bash
# Check server is running
curl http://localhost:8000/health

# Check firewall
sudo ufw status
```

### Cerebrium Issues

**Deployment fails:**
```bash
# Re-login
cerebrium logout
cerebrium login

# Check status
cerebrium status
```

**Slow responses:**
- First request after idle (cold start) takes 10-20 seconds
- Set `min_replicas = 1` in cerebrium.toml to keep warm

---

## FAQ

### Q: Can I use both deployments?

Yes! You can switch between them by changing environment variables. No code changes needed.

### Q: What if I want to switch later?

Simply:
1. Set up the new deployment
2. Update `TTD_BASE_URL` and `TTD_API_KEY`
3. Restart the voice assistant

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for details.

### Q: Which is cheaper?

- **Self-hosted**: Fixed costs (GPU hardware or VPS rental)
- **Cerebrium**: Pay per use (~$0.50-1.00/GPU hour)

For >100 hours/month, self-hosted is usually cheaper.

See [DEPLOYMENT_COMPARISON.md](DEPLOYMENT_COMPARISON.md) for cost analysis.

### Q: Which is faster?

- **Self-hosted**: ~35-60ms (local network)
- **Cerebrium**: ~80-150ms (includes internet latency)

Both are fast enough for real-time conversation.

### Q: Can I use a different model?

Yes, but you'll need to:
1. Deploy the new model using the same method
2. Update the `model` parameter in your configuration
3. Ensure it returns the same turn detection format

### Q: Is my data private?

- **Self-hosted**: Yes, all data stays on your infrastructure
- **Cerebrium**: Transcripts are sent to Cerebrium for processing

For HIPAA/GDPR compliance, use self-hosted.

### Q: What GPU do I need?

Minimum:
- NVIDIA GPU with 8GB+ VRAM
- CUDA 12.1+

Recommended:
- RTX 3080, RTX 4090, or A10
- For production, A10 or better

---

## Next Steps

After deployment:

1. ✅ Test turn detection with `test.py`
2. ✅ Configure other services (Deepgram, OpenAI, ElevenLabs)
3. ✅ Run the voice assistant: `task run`
4. ✅ Access at http://localhost:3000

Enjoy your voice assistant! 🎉
