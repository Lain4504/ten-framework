# Technical Integration Notes

This document explains how the voice assistant integrates with both Cerebrium and self-hosted turn detection deployments.

## API Compatibility

Both deployment options provide **OpenAI-compatible API endpoints**, which means:
- Same request format
- Same authentication method (API key in headers)
- Same response structure (with minor wrapper differences)

### Request Format

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url=TTD_BASE_URL,  # Different per deployment
    api_key=TTD_API_KEY
)

response = await client.chat.completions.create(
    model="TEN-framework/TEN_Turn_Detection",
    messages=[
        {"role": "user", "content": "Hello I have a question about"}
    ],
    max_tokens=1,
    temperature=0.1,
    top_p=0.1
)
```

### Response Handling

The code in `turn_detector.py` handles both response formats automatically:

**Self-Hosted (Standard OpenAI):**
```python
content = chat_completion.choices[0].message.content
usage = chat_completion.usage
```

**Cerebrium (Wrapped):**
```python
content = chat_completion.result["choices"][0]["message"]["content"]
usage = chat_completion.result.get("usage", {})
```

The existing code checks for both formats and uses whichever is present:

```python
# From turn_detector.py lines 160-171
if hasattr(chat_completion, "result") and isinstance(
    chat_completion.result, dict
):
    # Cerebrium format
    content = chat_completion.result["choices"][0]["message"]["content"]
else:
    # Standard OpenAI format
    content = chat_completion.choices[0].message.content
```

## Configuration

Both deployments use the same environment variables:

```bash
# Self-Hosted
TTD_BASE_URL=http://localhost:8000/v1
TTD_API_KEY=not-needed-for-local

# Cerebrium
TTD_BASE_URL=https://api.cortex.cerebrium.ai/v4/p-xxxxx/ten-turn-detection-project/run
TTD_API_KEY=your_cerebrium_api_key_here
```

These are read by `config.py`:

```python
class TENTurnDetectorConfig(BaseModel):
    base_url: str = "http://localhost:8000/v1"
    api_key: str = "TEN_Turn_Detection"
    model: str = "TEN_Turn_Detection"
    temperature: float = 0.1
    top_p: float = 0.1
```

And used to initialize the OpenAI client in `turn_detector.py`:

```python
self.client_session = AsyncOpenAI(
    api_key=self.config.api_key,
    base_url=self.config.base_url,
    http_client=self.http_client,
)
```

## Model Behavior

Both deployments use the **exact same model**: `TEN-framework/TEN_Turn_Detection`

This model is a fine-tuned LLM that:
- Takes conversation transcripts as input
- Returns one of three tokens: `finished`, `unfinished`, or `wait`
- Uses single-token classification (max_tokens=1)
- Optimized for low latency (~30-100ms)

**Turn Detection States:**
- `finished` - Speaker has completed their thought → Send to LLM for response
- `unfinished` - Speaker is mid-sentence → Continue listening
- `wait` - Ambiguous state → Hold briefly, then timeout

## Network Flow

### Self-Hosted Flow
```
User Speech
    ↓
Deepgram STT
    ↓
Transcript → Turn Detection (Local GPU)
    ↓
State: finished/unfinished/wait
    ↓
If finished → OpenAI LLM → ElevenLabs TTS → User
```

### Cerebrium Flow
```
User Speech
    ↓
Deepgram STT
    ↓
Transcript → Cerebrium API → Turn Detection (Cerebrium GPU)
    ↓
State: finished/unfinished/wait
    ↓
If finished → OpenAI LLM → ElevenLabs TTS → User
```

## Performance Characteristics

### Latency Components

**Self-Hosted:**
- Network: ~5-10ms (local network)
- Model inference: ~30-50ms
- Total: ~35-60ms

**Cerebrium:**
- Network: ~50-100ms (internet)
- Model inference: ~30-50ms  
- Total: ~80-150ms

### Cold Start Behavior

**Self-Hosted:**
- First request: ~5-10 seconds (model loading)
- Subsequent: ~35-60ms
- Cold start only happens on server restart

**Cerebrium:**
- First request: ~10-20 seconds (container start + model loading)
- Subsequent: ~80-150ms
- Cold start happens after idle timeout (auto-scaling)

## Error Handling

Both deployments share the same error handling logic in `turn_detector.py`:

```python
try:
    content = await asyncio.wait_for(task, timeout=5.0)
    # ... process response
except asyncio.TimeoutError:
    self.ten_env.log_warn(f"eval task {task.get_name()} was timeout")
    return TurnDetectorDecision.Unfinished  # Default to continue listening
except asyncio.CancelledError:
    self.ten_env.log_warn(f"eval task {task.get_name()} was cancelled")
    return TurnDetectorDecision.Unfinished
except Exception as e:
    self.ten_env.log_warn(f"eval task {task.get_name()} error {e}")
    return TurnDetectorDecision.Unfinished
```

**Fallback behavior**: If turn detection fails for any reason, the system defaults to `Unfinished` (continue listening), which is the safe choice.

## Testing Both Deployments

The test scripts in both directories verify:
1. Basic turn detection (incomplete sentence → "unfinished")
2. Complete question → "finished"
3. System prompts work correctly
4. Multi-turn conversation handling
5. Concurrent request handling

Run tests:
```bash
# Self-hosted
cd self_hosted
export TTD_BASE_URL="http://localhost:8000/v1"
export TTD_API_KEY="not-needed-for-local"
python test.py

# Cerebrium
cd cerebrium
export TTD_BASE_URL="https://api.cortex.cerebrium.ai/v4/p-xxxxx/ten-turn-detection-project/run"
export TTD_API_KEY="your_cerebrium_api_key"
python test.py
```

## Switching Between Deployments

To switch from one deployment to another:

1. **Update `.env` file** with new `TTD_BASE_URL` and `TTD_API_KEY`
2. **Restart the voice assistant**: `task run`

That's it! No code changes required.

### Quick Switch Script

```bash
# Switch to self-hosted
export TTD_BASE_URL="http://localhost:8000/v1"
export TTD_API_KEY="not-needed-for-local"

# Switch to Cerebrium
export TTD_BASE_URL="https://api.cortex.cerebrium.ai/v4/p-xxxxx/ten-turn-detection-project/run"
export TTD_API_KEY="your_cerebrium_api_key"

# Restart app
task run
```

## Monitoring & Debugging

### Enable Debug Logging

The turn detection extension logs important events:

```python
# In turn_detector.py
self.ten_env.log_debug(f"eval task {task.get_name()} messages: {messages}")
self.ten_env.log_debug(f"got content: {content}")
self.ten_env.log_info(f"KEYPOINT [ttfb:{ttfb}ms], [text:{content}]")
```

Check logs to verify:
- Requests are reaching the turn detection service
- Responses are being parsed correctly
- Latency is within expected range

### Common Issues

**Self-Hosted:**
- Server not running: `docker compose ps` to check status
- GPU not detected: `docker run --rm --gpus all nvidia/cuda:12.1.1-base-ubuntu22.04 nvidia-smi`
- Port conflict: Change port in `docker-compose.yml`

**Cerebrium:**
- Wrong base URL: Ensure it ends with `/run`
- API key incorrect: Check Cerebrium dashboard
- Deployment sleeping: First request wakes it up (cold start)

## Extension Points

The turn detection system can be extended:

### Custom Turn Detection Logic

Modify `extension.py` to add custom rules:

```python
async def _eval_decision(self, ten_env: AsyncTenEnv) -> None:
    # Get AI decision
    decision = await self.turn_detector.eval(self.cached_text)
    
    # Add custom logic
    if len(self.cached_text) < 5:
        # Too short, always continue listening
        decision = TurnDetectorDecision.Unfinished
    
    # Process decision
    if decision == TurnDetectorDecision.Finished:
        await self._process_new_turn(ten_env, decision)
```

### Forced Turn Timeout

The system includes a configurable timeout (default 5 seconds):

```python
class TENTurnDetectorConfig(BaseModel):
    force_threshold_ms: int = 5000  # Force turn after 5 seconds of silence
```

This ensures the assistant responds even if the AI thinks the turn is unfinished.

## Security Considerations

### Self-Hosted

- **API Key**: Not strictly required for local deployment, but recommended for production
- **Network**: Bind to `127.0.0.1` instead of `0.0.0.0` for localhost-only access
- **Firewall**: Restrict access to port 8000

### Cerebrium

- **API Key**: Required, stored in environment variables
- **HTTPS**: All traffic is encrypted
- **Data**: Transcripts are sent to Cerebrium for processing

## Summary

The voice assistant's turn detection integration is **deployment-agnostic**:
- Same code works with both Cerebrium and self-hosted
- Switch by changing 2 environment variables
- Automatic response format handling
- Consistent error handling and fallback behavior

This design allows you to:
- Start with Cerebrium for quick setup
- Migrate to self-hosted later for cost/privacy
- Or vice versa
- Switch based on environment (dev vs prod)
