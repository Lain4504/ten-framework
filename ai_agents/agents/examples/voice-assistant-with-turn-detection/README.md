# Voice Assistant with Turn Detection

A voice assistant enhanced with AI-powered turn detection using a fine-tuned LLM model. Unlike traditional Voice Activity Detection (VAD) which only detects when speech starts/stops, turn detection intelligently determines when a speaker has finished their conversational turn by understanding context and intent.

The turn detection model can be deployed in two ways:
- **☁️ Cloud Deployment** - Using Cerebrium (managed GPU hosting, zero setup)
- **🏠 Self-Hosted** - On your own infrastructure (full control, privacy, no recurring costs)

> **🚀 Quick Start**: See [QUICK_START.md](QUICK_START.md) for fastest path to running the voice assistant.

## What is Turn Detection?

**Turn Detection** analyzes speech transcription in real-time to determine if the speaker has finished their thought (turn complete) or is pausing mid-sentence (turn incomplete). This enables:

- **Natural conversation flow** - The assistant waits for complete thoughts before responding
- **Better interruption handling** - Distinguishes between pauses and completion
- **Context-aware decisions** - Uses LLM reasoning rather than simple audio thresholds

## Prerequisites

### Turn Detection Deployment

Choose one of the following deployment options for the Turn Detection model.

**Not sure which to choose?** See [DEPLOYMENT_COMPARISON.md](DEPLOYMENT_COMPARISON.md) for a detailed comparison.

#### Option A: Self-Hosted (Recommended for Full Control)

**Requirements:**
- NVIDIA GPU with 8GB+ VRAM (RTX 3080, A10, or better)
- Docker with NVIDIA Container Toolkit
- 20GB free storage

**Quick Setup:**
```bash
cd self_hosted
./deploy.sh
```

This deploys the model locally on your own hardware. See [self_hosted/README.md](self_hosted/README.md) for detailed instructions.

**Pros:**
- ✅ Full control and privacy
- ✅ No recurring cloud costs
- ✅ Data never leaves your infrastructure
- ✅ Predictable performance

**Cons:**
- ⚠️ Requires GPU hardware
- ⚠️ Manual setup and maintenance

#### Option B: Cerebrium (Cloud Hosted)

**Requirements:**
- Cerebrium account (free tier available)
- Internet connection

**Quick Setup:**

**Quick Setup:**
```bash
# Install Cerebrium CLI
pip install cerebrium

# Login
cerebrium login

# Deploy
cd cerebrium
cerebrium deploy
```

See [cerebrium/README.md](cerebrium/README.md) for detailed instructions.

**Pros:**
- ✅ Zero hardware requirements
- ✅ Automatic scaling
- ✅ No maintenance
- ✅ 5-minute setup

**Cons:**
- ⚠️ Recurring cloud costs (~$0.50-1.00/hour)
- ⚠️ Data sent to third-party service

---

### Required Environment Variables

After deploying the turn detection model (either option), set these in your `.env` file:

```bash
# Agora (required for audio streaming)
AGORA_APP_ID=your_agora_app_id_here
AGORA_APP_CERTIFICATE=your_agora_certificate_here  # optional

# Deepgram (required for STT)
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# OpenAI (required for LLM)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini  # or gpt-4o, gpt-3.5-turbo

# ElevenLabs (required for TTS)
ELEVENLABS_TTS_KEY=your_elevenlabs_api_key_here

# Turn Detection - Choose based on your deployment:
# For Self-Hosted:
TTD_BASE_URL=http://localhost:8000/v1
TTD_API_KEY=not-needed-for-local

# OR for Cerebrium:
# TTD_BASE_URL=https://api.cortex.cerebrium.ai/v4/p-xxxxx/ten-turn-detection-project/run
# TTD_API_KEY=your_cerebrium_api_key_here

# Optional
WEATHERAPI_API_KEY=your_weather_api_key_here  # for weather tool
```

## Setup and Running

> **Note**: Make sure you've completed one of the [Turn Detection deployment options](#turn-detection-deployment) before proceeding.

### 1. Install Voice Assistant Dependencies

```bash
cd agents/examples/voice-assistant-with-turn-detection
task install
```

### 2. Run the Voice Assistant

```bash
task run
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **API Server**: http://localhost:8080
- **TMAN Designer**: http://localhost:49483

## How Turn Detection Works

1. **Speech Input**: User speaks → Deepgram STT transcribes in real-time
2. **Turn Analysis**: Each transcription chunk is sent to the turn detection model
3. **Classification**: The model returns one of three states:
   - `finished` - Turn is complete, send to LLM
   - `unfinished` - Continue listening, user still speaking
   - `wait` - Wait for clarification or timeout
4. **Response**: When `finished`, text is sent to OpenAI LLM → ElevenLabs TTS → User

### Turn Detection States

| State | Description | Action |
|-------|-------------|--------|
| `finished` | Speaker has completed their thought | Send transcription to LLM for response |
| `unfinished` | Speaker is mid-sentence or pausing | Continue collecting transcription |
| `wait` | Ambiguous state, waiting for more input | Hold briefly, then timeout |

## Customization

The voice assistant uses a modular design. Access the visual designer at http://localhost:49483 to:
- Replace STT provider (Deepgram → Azure, Speechmatics, AssemblyAI, etc.)
- Change LLM (OpenAI → Claude, Llama, Coze, etc.)
- Swap TTS (ElevenLabs → Azure, Cartesia, Fish Audio, etc.)
- Adjust turn detection sensitivity

For detailed usage, see [TMAN Designer documentation](https://theten.ai/docs/ten_agent/customize_agent/tman-designer).

## Docker Deployment

**Note**: Execute outside of any Docker container.

### Build Image

```bash
cd ai_agents
docker build -f agents/examples/voice-assistant-with-turn-detection/Dockerfile -t voice-assistant-turn-detection .
```

### Run

```bash
docker run --rm -it --env-file .env -p 8080:8080 -p 3000:3000 voice-assistant-turn-detection
```

### Access

- Frontend: http://localhost:3000
- API Server: http://localhost:8080
- TMAN Designer: http://localhost:49483

## Learn More

- [Cerebrium Documentation](https://docs.cerebrium.ai/)
- [TEN Turn Detection Model](https://huggingface.co/TEN-framework/TEN_Turn_Detection)
- [vLLM Documentation](https://docs.vllm.ai/)
- [TEN Framework Documentation](https://theten.ai/docs)
- [Agora RTC Documentation](https://docs.agora.io/en/voice-calling/overview/product-overview)
- [Deepgram API Documentation](https://developers.deepgram.com/)
- [ElevenLabs API Documentation](https://docs.elevenlabs.io/)
