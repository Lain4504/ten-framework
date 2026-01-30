import asyncio
import os
from openai import AsyncOpenAI

# Read configuration from environment variables or use defaults for local deployment
TTD_BASE_URL = os.getenv("TTD_BASE_URL", "http://localhost:8000/v1")
TTD_API_KEY = os.getenv("TTD_API_KEY", "not-needed-for-local")

print(f"Testing Turn Detection API at: {TTD_BASE_URL}")
print(f"API Key: {'*' * len(TTD_API_KEY)}")

# Initialize AsyncOpenAI client with self-hosted endpoint
client = AsyncOpenAI(base_url=TTD_BASE_URL, api_key=TTD_API_KEY)


async def test_turn_detection():
    """Test the OpenAI-compatible Turn Detection API"""

    print("=" * 60)
    print("Testing Self-Hosted Turn Detection API")
    print("=" * 60)

    # Test Case 1: Incomplete sentence
    print("\n[Test 1] Incomplete sentence:")
    try:
        response1 = await client.chat.completions.create(
            model="TEN-framework/TEN_Turn_Detection",
            messages=[{"role": "user", "content": "Hello I have a question about"}],
        )

        turn_state1 = response1.choices[0].message.content
        print("User: 'Hello I have a question about'")
        print(f"Turn Detection Result: {turn_state1}")
        print(f"Response ID: {response1.id}")
        print(f"Tokens Used: {response1.usage.total_tokens}")
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
        return False

    # Test Case 2: Complete question
    print("\n[Test 2] Complete question:")
    try:
        response2 = await client.chat.completions.create(
            model="TEN-framework/TEN_Turn_Detection",
            messages=[
                {"role": "user", "content": "Can you help me with my order?"}
            ],
        )

        turn_state2 = response2.choices[0].message.content
        print("User: 'Can you help me with my order?'")
        print(f"Turn Detection Result: {turn_state2}")
        print(f"Response ID: {response2.id}")
        print(f"Tokens Used: {response2.usage.total_tokens}")
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
        return False

    # Test Case 3: With system prompt
    print("\n[Test 3] With system prompt:")
    try:
        response3 = await client.chat.completions.create(
            model="TEN-framework/TEN_Turn_Detection",
            messages=[
                {
                    "role": "system",
                    "content": "You are analyzing conversation turns.",
                },
                {"role": "user", "content": "Hey there I was wondering"},
            ],
        )

        turn_state3 = response3.choices[0].message.content
        print("User: 'Hey there I was wondering'")
        print(f"Turn Detection Result: {turn_state3}")
        print(f"Response ID: {response3.id}")
        print(f"Tokens Used: {response3.usage.total_tokens}")
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
        return False

    # Test Case 4: Multi-turn conversation
    print("\n[Test 4] Multi-turn conversation:")
    try:
        response4 = await client.chat.completions.create(
            model="TEN-framework/TEN_Turn_Detection",
            messages=[
                {"role": "user", "content": "What is a mistral?"},
                {
                    "role": "assistant",
                    "content": "A mistral is a type of cold, dry wind.",
                },
                {"role": "user", "content": "How does the mistral wind form?"},
            ],
        )

        turn_state4 = response4.choices[0].message.content
        print("User: 'How does the mistral wind form?'")
        print(f"Turn Detection Result: {turn_state4}")
        print(f"Response ID: {response4.id}")
        print(f"Tokens Used: {response4.usage.total_tokens}")
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
        return False

    # Test Case 5: Batch requests (running concurrently)
    print("\n[Test 5] Concurrent batch requests:")
    try:
        prompts = [
            "I need help with",
            "What is the weather like?",
            "Thank you very much!",
        ]

        tasks = [
            client.chat.completions.create(
                model="TEN-framework/TEN_Turn_Detection",
                messages=[{"role": "user", "content": prompt}],
            )
            for prompt in prompts
        ]

        responses = await asyncio.gather(*tasks)

        for i, (prompt, response) in enumerate(zip(prompts, responses), 1):
            turn_state = response.choices[0].message.content
            print(f"  {i}. '{prompt}' → {turn_state}")
    except Exception as e:
        print(f"❌ Test 5 failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60)
    print("\nYour self-hosted Turn Detection server is working correctly.")
    print("You can now use it with the voice assistant application.")
    return True


# Run the async test
if __name__ == "__main__":
    try:
        success = asyncio.run(test_turn_detection())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("\nMake sure the Turn Detection server is running:")
        print("  ./deploy.sh")
        exit(1)
