#!/bin/bash
set -e

echo "================================================"
echo "TEN Turn Detection - Self-Hosted Deployment"
echo "================================================"
echo ""

# Check for NVIDIA GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo "⚠️  Warning: nvidia-smi not found. GPU support may not be available."
    echo "   This server requires a CUDA-compatible GPU for optimal performance."
    echo ""
fi

# Check for Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed."
    echo "   Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Determine which docker compose command to use
DOCKER_COMPOSE_CMD=""
if command -v docker compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    echo "❌ Error: Docker Compose is not installed."
    echo "   Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Pull the latest vLLM image
echo "📦 Pulling vLLM Docker image..."
docker pull vllm/vllm-openai:latest

echo ""
echo "🚀 Starting Turn Detection Server..."
echo "   This will:"
echo "   1. Download the TEN_Turn_Detection model (~7GB)"
echo "   2. Load the model into GPU memory"
echo "   3. Start the OpenAI-compatible API server on port 8000"
echo ""

# Start the service
$DOCKER_COMPOSE_CMD up -d

echo ""
echo "⏳ Waiting for server to be ready..."
echo "   (This may take 2-5 minutes on first run while the model downloads)"
echo ""

# Wait for health check
max_wait=300  # 5 minutes
elapsed=0
while [ $elapsed -lt $max_wait ]; do
    if $DOCKER_COMPOSE_CMD ps | grep -q "healthy"; then
        echo ""
        echo "✅ Turn Detection Server is ready!"
        break
    fi
    
    if $DOCKER_COMPOSE_CMD ps | grep -q "unhealthy"; then
        echo ""
        echo "❌ Server failed health check. Check logs with:"
        echo "   $DOCKER_COMPOSE_CMD logs turn-detection"
        exit 1
    fi
    
    sleep 5
    elapsed=$((elapsed + 5))
    echo -n "."
done

if [ $elapsed -ge $max_wait ]; then
    echo ""
    echo "⚠️  Server did not become healthy within ${max_wait}s"
    echo "   Check logs with: $DOCKER_COMPOSE_CMD logs turn-detection"
    exit 1
fi

echo ""
echo "================================================"
echo "✅ Deployment Complete!"
echo "================================================"
echo ""
echo "Server Information:"
echo "  • API Endpoint: http://localhost:8000/v1"
echo "  • Health Check: http://localhost:8000/health"
echo "  • API Documentation: http://localhost:8000/docs"
echo ""
echo "Environment Variables to use:"
echo "  export TTD_BASE_URL=\"http://localhost:8000/v1\""
echo "  export TTD_API_KEY=\"not-needed-for-local\""
echo ""
echo "Useful Commands:"
echo "  • View logs:    $DOCKER_COMPOSE_CMD logs -f turn-detection"
echo "  • Stop server:  $DOCKER_COMPOSE_CMD down"
echo "  • Restart:      $DOCKER_COMPOSE_CMD restart"
echo ""
echo "Next Steps:"
echo "  1. Test the deployment with: python test.py"
echo "  2. Update your .env file with the variables above"
echo "  3. Run the voice assistant: task run"
echo ""
